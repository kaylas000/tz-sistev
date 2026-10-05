"""API Gateway (FastAPI) — ТЗ §3: Auth, Rate limit, маршрутизация к студиям, Композиции.

Эндпоинты:
  GET  /health                      — живой ли гейт
  GET  /metrics                     — Prometheus-exposition (observability)
  GET  /studios                     — список вертикалей
  GET  /studios/{name}              — метаданные студии (Конституция, скиллы, референсы)
  POST /studios/{name}/runs         — запустить цикл по брифу (Bearer-токен + rate limit)
  GET  /runs/{run_id}               — состояние/лог run'а
  POST /compositions                — композиция: задача раскладывается на несколько студий
  GET  /openapi.json (встроенный)   — контракт для Telegram/Web клиентов
"""
from __future__ import annotations

import threading
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from autogen import __version__
from autogen.kernel.budget import BudgetLimits, BudgetManager
from autogen.kernel.errors import ErrorItem
from autogen.kernel.llm import LLMManager
from autogen.kernel.observability import METRICS, observe_run
from autogen.kernel.registry import StudioRegistry
from autogen.kernel.runner import KernelRunner, RunState

# ------------------------------------------------------------------ конфигурация
DEFAULT_TOKENS = {"dev-token": "local-dev"}      # токен -> клиент
RATE_LIMIT_RPM = 30                               # запросов в минуту на токен

_runs: dict[str, RunState] = {}
_runs_lock = threading.Lock()
_rate_buckets: dict[str, deque] = defaultdict(deque)
_rate_lock = threading.Lock()


def create_app(root: Optional[str | Path] = None, llm_backend: str = "mock",
               tokens: Optional[dict[str, str]] = None) -> FastAPI:
    root = Path(root) if root else Path.cwd()
    registry = StudioRegistry(root / "verticals")
    budget = BudgetManager(limits=BudgetLimits())
    app = FastAPI(title="АвтоГен API Gateway", version=__version__)
    app.state.registry = registry
    app.state.budget = budget
    app.state.llm_backend = llm_backend
    allowed_tokens = tokens or DEFAULT_TOKENS

    # ------------------------------------------------------------- auth
    def require_auth(authorization: str = Header(default="")) -> str:
        if not authorization.lower().startswith("bearer "):
            raise HTTPException(401, "Требуется Authorization: Bearer <token>")
        token = authorization.split(" ", 1)[1].strip()
        if token not in allowed_tokens:
            raise HTTPException(403, "Неизвестный токен")
        return token

    # ------------------------------------------------------------- rate limit
    def rate_limit(client: str = Depends(require_auth)) -> str:
        with _rate_lock:
            bucket = _rate_buckets[client]
            now = time.time()
            while bucket and now - bucket[0] > 60:
                bucket.popleft()
            if len(bucket) >= RATE_LIMIT_RPM:
                METRICS.inc("autogen_ratelimited_total", client=client)
                raise HTTPException(429, f"Rate limit: {RATE_LIMIT_RPM} req/min")
            bucket.append(now)
        return client

    # ------------------------------------------------------------- схемы
    class BriefIn(BaseModel):
        skill: Optional[str] = None
        goal: str = ""
        audience: str = ""
        deliverable: str = ""
        constraints: str = ""
        extra: dict[str, Any] = Field(default_factory=dict)

    class CompositionIn(BaseModel):
        task: str
        studios: list[str]

    # ------------------------------------------------------------- routes
    @app.get("/health")
    def health():
        return {"ok": True, "version": __version__, "studios": registry.discover()}

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics():
        return METRICS.exposition()

    @app.get("/studios")
    def studios(_: str = Depends(require_auth)):
        out = []
        for name in registry.discover():
            s = registry.get(name)
            out.append({"name": s.name, "title": s.meta.get("title"),
                        "domain": s.meta.get("domain"), "skills": list(s.skills),
                        "rules": len(s.rules), "references": s.reference_count(),
                        "min_references": s.min_references})
        return out

    @app.get("/studios/{name}")
    def studio_detail(name: str, _: str = Depends(require_auth)):
        try:
            s = registry.get(name)
        except KeyError:
            raise HTTPException(404, f"Студия '{name}' не найдена")
        return {"name": s.name, "meta": s.meta,
                "constitution": [{"id": r.id, "text": r.text[:200], "code": r.error_code}
                                 for r in s.rules],
                "skills": {k: v.meta for k, v in s.skills.items()},
                "references": s.reference_count()}

    @app.post("/studios/{name}/runs")
    def create_run(name: str, brief: BriefIn, client: str = Depends(rate_limit)):
        try:
            studio = registry.get(name)
        except KeyError:
            raise HTTPException(404, f"Студия '{name}' не найдена")
        llm = LLMManager(backend=app.state.llm_backend)
        runner = KernelRunner(llm=llm, budget=budget)
        payload = brief.model_dump(exclude_none=True)
        payload.update(payload.pop("extra", {}) or {})
        st = runner.run(studio, payload, skill_name=brief.skill)
        with _runs_lock:
            _runs[st.run_id] = st
        tokens = sum(c.total_tokens for c in llm.calls)
        observe_run(studio.name, st.skill, st.status, st.cycles, tokens, 0.0,
                    time.time() - st.started_at)
        code = 200 if st.passed else (422 if st.status in ("g1_fail", "error") else 504)
        body = _run_json(st)
        if code != 200:
            raise HTTPException(code, detail=body)
        return body

    @app.get("/runs/{run_id}")
    def get_run(run_id: str, _: str = Depends(require_auth)):
        with _runs_lock:
            st = _runs.get(run_id)
        if st is None:
            raise HTTPException(404, "Run не найден")
        return _run_json(st)

    @app.post("/compositions")
    def compose(body: CompositionIn, client: str = Depends(rate_limit)):
        """Композиция: одна задача раздаётся нескольким студиям параллельно."""
        results: dict[str, dict] = {}
        threads = []
        lock = threading.Lock()

        def _work(sname: str):
            try:
                studio = registry.get(sname)
            except KeyError as exc:
                with lock:
                    results[sname] = {"error": str(exc)}
                return
            llm = LLMManager(backend=app.state.llm_backend)
            runner = KernelRunner(llm=llm, budget=budget)
            br = {"goal": body.task, "audience": "клиент композиции",
                  "deliverable": studio.meta.get("title", sname)}
            st = runner.run(studio, br)
            with _runs_lock:
                _runs[st.run_id] = st
            with lock:
                results[sname] = _run_json(st)

        for s in body.studios:
            t = threading.Thread(target=_work, args=(s,), daemon=True)
            threads.append(t); t.start()
        for t in threads:
            t.join(timeout=300)
        composition_id = uuid.uuid4().hex[:8]
        METRICS.inc("autogen_compositions_total", n=len(body.studios))
        return {"composition_id": composition_id, "task": body.task, "parts": results}

    return app


def _run_json(st: RunState) -> dict:
    return {
        "run_id": st.run_id, "studio": st.studio, "skill": st.skill,
        "status": st.status, "passed": st.passed, "cycles": st.cycles,
        "needs_human_review": st.needs_human_review,
        "errors": [e.to_dict() for e in st.errors],
        "artifact_preview": st.artifact[:400],
        "log": st.log,
    }


# uvicorn autogen.api_gateway:app --port 8080
app = create_app()
