"""Валидаторы ядра: запуск студийных валидаторов + generic-проверки.

Конвейер Verifier'а (ТЗ §5):
  1. schema        — JSON Schema артефакта/брифа
  2. constitution  — правила К-xx студии -> коды V-xx
  3. anti_slop     — запреты B-xx и квоты Q-xx из anti-slop/BANNED.md, QUOTAS.md
  4. llm_judge     — LLM-критик (опционально, через LLMManager)

Студийные валидаторы лежат в verticals/{name}/validators/*.py и подключаются
динамически; если их нет — работают generic-реализации этого модуля.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Optional

from .errors import ErrorItem


# ---------------------------------------------------------------- generic helpers
def _load_validator_module(studio_dir: Path, filename: str):
    p = studio_dir / "validators" / filename
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"v_{studio_dir.name}_{filename[:-3]}", p)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- schema
def validate_schema(payload: dict, schema: dict) -> list[ErrorItem]:
    """Минимальная JSON-Schema проверка (type/required/properties). Без внешних зависимостей."""
    errors: list[ErrorItem] = []
    required = schema.get("required", [])
    for field in required:
        if field not in payload or payload[field] in (None, "", [], {}):
            errors.append(ErrorItem(
                code="A-03", severity="critical", rule_id="schema",
                description=f"Поле '{field}' обязательно и должно быть непустым",
                suggestion=f"Добавьте заполненное поле '{field}'"))
    props = schema.get("properties", {})
    type_map = {"string": str, "object": dict, "array": list, "number": (int, float), "integer": int}
    for key, pspec in props.items():
        if key in payload and payload[key] is not None:
            exp = type_map.get(pspec.get("type", ""))
            if exp and not isinstance(payload[key], exp):
                errors.append(ErrorItem(
                    code="A-03", severity="major", rule_id="schema",
                    description=f"Поле '{key}' имеет тип {type(payload[key]).__name__}, ожидался {pspec['type']}",
                    suggestion=f"Исправьте тип поля '{key}'"))
    return errors


def validate_brief(brief: dict, required_fields: list[str]) -> list[ErrorItem]:
    """G1: входной гейт — полнота брифа (коды E-01/E-02)."""
    errors: list[ErrorItem] = []
    for f in required_fields:
        v = brief.get(f)
        if v is None or (isinstance(v, str) and not v.strip()):
            errors.append(ErrorItem(
                code="E-01", severity="critical", rule_id=f"brief:{f}",
                description=f"Бриф не содержит обязательного поля '{f}'",
                suggestion=f"Уточните у клиента значение поля '{f}'"))
    return errors


# ---------------------------------------------------------------- constitution
def validate_constitution_generic(rules, artifact: str) -> list[ErrorItem]:
    """Fallback-проверка: если в тексте Конституции есть маркер `check:` с regex — применяем.

    Формат правила в CONSTITUTION.md может содержать строку:
        check_regex: <python regex>, message: <текст>, severity: critical|major|minor
    Правило считается НАРУШЕННЫМ, если regex найден в артефакте.
    """
    errors: list[ErrorItem] = []
    for rule in rules:
        m = re.search(r"check_regex:\s*(.+?),\s*message:\s*(.+?)(?:,\s*severity:\s*(\w+))?$",
                      rule.text, re.S)
        if not m:
            continue
        pattern, message, sev = m.group(1).strip(), m.group(2).strip(), (m.group(3) or "major")
        try:
            if re.search(pattern, artifact, re.I | re.S):
                errors.append(ErrorItem(
                    code=rule.error_code, severity=sev, rule_id=rule.id,
                    description=f"Нарушение {rule.id}: {message}",
                    suggestion=f"Устраните нарушение правила {rule.id} ({rule.text.splitlines()[0][:80]})"))
        except re.error:
            continue
    return errors


# ---------------------------------------------------------------- anti-slop
_BANNED_RE = re.compile(r"^[-*]\s*\**(B-\d+)\**\s*[:.]\s*(.+?)\s*$", re.M)
_QUOTA_RE = re.compile(r"^[-*]\s*\**(Q-\d+)\**\s*[:.]\s*(?P<pattern>.+?)\s*max\s*=?\s*(?P<limit>\d+)", re.M | re.I)


def parse_banned(md_path: Path) -> list[tuple[str, str]]:
    if not md_path.exists():
        return []
    return [(m.group(1), m.group(2).strip()) for m in _BANNED_RE.finditer(md_path.read_text(encoding="utf-8"))]


def parse_quotas(md_path: Path) -> list[tuple[str, str, int]]:
    """Строки вида: - Q-01: паттерн `<regex>` max=3"""
    if not md_path.exists():
        return []
    out = []
    for m in _QUOTA_RE.finditer(md_path.read_text(encoding="utf-8")):
        pat = re.search(r"`([^`]+)`", m.group("pattern"))
        if pat:
            out.append((m.group(1), pat.group(1), int(m.group("limit"))))
    return out


def validate_anti_slop(studio_dir: Path, artifact: str) -> list[ErrorItem]:
    errors: list[ErrorItem] = []
    banned = parse_banned(studio_dir / "anti-slop" / "BANNED.md")
    for code, desc in banned:
        # запрет формулируется как фраза; пытаемся извлечь `код-шаблон` в backticks
        token = re.search(r"`([^`]+)`", desc)
        needle = token.group(1) if token else desc
        if needle.lower() in artifact.lower():
            errors.append(ErrorItem(
                code=code, severity="major", rule_id=code,
                description=f"Запрещённый anti-slop паттерн: {desc}",
                suggestion="Замените паттерн на осмысленную альтернативу"))
    for qid, pattern, limit in parse_quotas(studio_dir / "anti-slop" / "QUOTAS.md"):
        try:
            n = len(re.findall(pattern, artifact, re.I))
        except re.error:
            continue
        if n > limit:
            errors.append(ErrorItem(
                code=qid, severity="minor", rule_id=qid,
                description=f"Квота превышена: '{pattern}' встречается {n} раз (максимум {limit})",
                suggestion=f"Сократите количество вхождений до {limit}"))
    return errors


# ---------------------------------------------------------------- llm judge
JUDGE_PROMPT = """Ты — строгий критик. Оцени артефакт по брифу и правилам.
BRIF: {brief}
ПРАВИЛА: {rules}
АРТЕФАКТ:
{artifact}

Ответь строго JSON: {{"passed": true/false, "score": 0-10,
"errors": [{{"code": "V-XX", "severity": "critical|major|minor", "description": "...", "suggestion": "..."}}]}}"""


def llm_judge(llm, studio, brief: dict, artifact: str) -> list[ErrorItem]:
    """LLM-критик: вердикт извлекается из JSON-ответа модели."""
    prompt = JUDGE_PROMPT.format(
        brief=json.dumps(brief, ensure_ascii=False)[:1500],
        rules="; ".join(f"{r.id}: {r.text[:100]}" for r in studio.rules)[:1500],
        artifact=artifact[:6000])
    try:
        resp = llm.complete("verifier", prompt)
    except Exception as exc:
        return [ErrorItem(code="L-01", severity="minor",
                          description=f"LLM-критик недоступен: {exc}", suggestion="")]
    from .llm import extract_json
    data = extract_json(resp.text)
    if not data:
        return []
    errors: list[ErrorItem] = []
    for e in data.get("errors", []):
        if not isinstance(e, dict) or "code" not in e:
            continue
        errors.append(ErrorItem(
            code=str(e["code"]), severity=str(e.get("severity", "minor")),
            rule_id=e.get("rule_id"), description=str(e.get("description", "")),
            suggestion=str(e.get("suggestion", ""))))
    return errors


# ---------------------------------------------------------------- конвейер
class ValidationPipeline:
    """Прогон артефакта через все валидаторы студии (ТЗ §5 Verifier)."""

    def __init__(self, studio, llm=None, use_llm_judge: bool = True) -> None:
        self.studio = studio
        self.llm = llm
        self.use_llm_judge = use_llm_judge and llm is not None

    def run(self, brief: dict, artifact: str) -> list[ErrorItem]:
        errors: list[ErrorItem] = []
        if not artifact.strip():
            return [ErrorItem(code="A-02", severity="critical",
                              description="Артефакт пуст", suggestion="Сгенерируйте артефакт заново")]

        # 1. студийные валидаторы (verticals/{name}/validators/constitution.py и др.)
        mod = _load_validator_module(self.studio.path, "constitution.py")
        if mod and hasattr(mod, "validate"):
            try:
                errors += list(mod.validate(self.studio, brief, artifact) or [])
            except Exception as exc:
                errors.append(ErrorItem(code="L-01", severity="minor",
                                        description=f"Ошибка студийного валидатора: {exc}", suggestion=""))
        else:
            errors += validate_constitution_generic(self.studio.rules, artifact)

        # 2. anti-slop (студийный или generic)
        amod = _load_validator_module(self.studio.path, "anti_slop.py")
        if amod and hasattr(amod, "validate"):
            try:
                errors += list(amod.validate(self.studio, brief, artifact) or [])
            except Exception:
                errors += validate_anti_slop(self.studio.path, artifact)
        else:
            errors += validate_anti_slop(self.studio.path, artifact)

        # 3. schema
        smod = _load_validator_module(self.studio.path, "schema.py")
        if smod and hasattr(smod, "validate"):
            try:
                errors += list(smod.validate(self.studio, brief, artifact) or [])
            except Exception:
                pass

        # 4. LLM-критик
        if self.use_llm_judge:
            jmod = _load_validator_module(self.studio.path, "llm_judge.py")
            if jmod and hasattr(jmod, "validate"):
                try:
                    errors += list(jmod.validate(self.studio, self.llm, brief, artifact) or [])
                except Exception:
                    errors += llm_judge(self.llm, self.studio, brief, artifact)
            else:
                errors += llm_judge(self.llm, self.studio, brief, artifact)

        return errors
