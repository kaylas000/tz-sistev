"""LLM Manager: единый интерфейс к моделям (ТЗ §10.2).

Роли Planner/Coder/Verifier/Fixer имеют свои модели и температуры.
Бэкенды:
  * ollama  — реальные вызовы через HTTP API Ollama (бесплатные локальные модели)
  * litellm — опционально, если установлен пакет litellm
  * mock    — детерминированный офлайн-бэкенд для тестов/разработки

Менеджер считает токены и стоимость, пропуская каждый запрос через BudgetManager.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Optional

# роль -> (модель, температура) — из ТЗ §10.2
DEFAULT_ROLE_MODELS: dict[str, dict] = {
    "planner":  {"model": "llama3.1:8b",     "temperature": 0.3},
    "coder":    {"model": "qwen2.5-coder:7b","temperature": 0.7},
    "verifier": {"model": "gemma2:9b",       "temperature": 0.0},
    "fixer":    {"model": "llama3.1:8b",     "temperature": 0.3},
}

# грубая оценка стоимости $/1K токенов для локальных моделей (Ollama => 0)
PRICE_PER_1K: dict[str, float] = {}


@dataclass(slots=True)
class LLMResponse:
    text: str
    model: str
    role: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def _estimate_tokens(text: str) -> int:
    """Эвристика ~4 символа на токен."""
    return max(1, len(text) // 4)


class LLMManager:
    def __init__(
        self,
        backend: str = "mock",
        base_url: str = "http://localhost:11434",
        role_models: Optional[dict] = None,
        budget=None,  # kernel.budget.BudgetManager
        mock_handler: Optional[Callable[[str, str, dict], str]] = None,
        timeout: int = 120,
    ) -> None:
        if backend not in ("mock", "ollama", "litellm"):
            raise ValueError(f"Неизвестный LLM-бэкенд: {backend}")
        self.backend = backend
        self.base_url = base_url.rstrip("/")
        self.role_models = {**DEFAULT_ROLE_MODELS, **(role_models or {})}
        self.budget = budget
        self.mock_handler = mock_handler
        self.timeout = timeout
        self.calls: list[LLMResponse] = []

    # ------------------------------------------------------------ public API
    def complete(self, role: str, prompt: str, *, context: Optional[dict] = None) -> LLMResponse:
        cfg = self.role_models.get(role)
        if cfg is None:
            raise KeyError(f"Неизвестная роль LLM: {role}")
        model, temperature = cfg["model"], cfg["temperature"]

        if self.budget is not None:
            self.budget.check_and_charge(
                est_prompt_tokens=_estimate_tokens(prompt),
                est_completion_tokens=2048,
                price_per_1k=PRICE_PER_1K.get(model, 0.0),
            )

        if self.backend == "ollama":
            text = self._ollama_generate(model, prompt, temperature)
        elif self.backend == "litellm":
            text = self._litellm_generate(model, prompt, temperature)
        else:
            text = self._mock_generate(role, prompt, context or {})

        resp = LLMResponse(
            text=text, model=model, role=role,
            prompt_tokens=_estimate_tokens(prompt),
            completion_tokens=_estimate_tokens(text),
            cost=PRICE_PER_1K.get(model, 0.0) / 1000.0 * (_estimate_tokens(prompt) + _estimate_tokens(text)),
        )
        self.calls.append(resp)
        return resp

    # ------------------------------------------------------------ бэкенды
    def _ollama_generate(self, model: str, prompt: str, temperature: float) -> str:
        payload = json.dumps({
            "model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": temperature},
        }).encode()
        req = urllib.request.Request(f"{self.base_url}/api/generate",
                                     data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read().decode())
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"Ollama недоступна ({self.base_url}): {exc}") from exc
        return data.get("response", "")

    def _litellm_generate(self, model: str, prompt: str, temperature: float) -> str:
        try:
            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Пакет litellm не установлен") from exc
        resp = litellm.completion(
            model=model, messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return resp.choices[0].message.content

    def _mock_generate(self, role: str, prompt: str, context: dict) -> str:
        """Офлайн-бэкенд. Если задан mock_handler — используем его."""
        if self.mock_handler is not None:
            return self.mock_handler(role, prompt, context)
        return f"[mock:{role}] {prompt[:120]}"


# ------------------------------------------------------------------ парсинг ответов
_FENCE_RE = re.compile(r"```(?:[a-zA-Z0-9_+-]*)?\n(.*?)```", re.S)


def extract_code_block(text: str, fallback_whole: bool = True) -> str:
    """Достать первый ```блок``` из ответа модели (артефакт кодера)."""
    m = _FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    return text.strip() if fallback_whole else ""


def extract_json(text: str) -> Optional[dict]:
    """Достать первый JSON-объект из текста ответа (планы, вердикты)."""
    # сначала fenced
    fence = _FENCE_RE.search(text)
    candidates = [fence.group(1)] if fence else []
    candidates.append(text)
    for cand in candidates:
        # ищем самый внешний {...}
        start = cand.find("{")
        while start != -1:
            depth = 0
            for i in range(start, len(cand)):
                if cand[i] == "{":
                    depth += 1
                elif cand[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(cand[start:i + 1])
                        except json.JSONDecodeError:
                            break
            start = cand.find("{", start + 1)
    return None
