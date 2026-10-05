"""The-AI-Corporation: CEO-агент (ТЗ §1, слой оркестратора).

CEO получает высокоуровневую задачу клиента, декомпозирует её на подзадачи,
маршрутизирует каждая в свою студию-вертикаль, запускает параллельно
(потоки), собирает результаты и формирует итоговый пакет.
"""
from __future__ import annotations

import json
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Optional

from autogen.kernel.llm import LLMManager, extract_json
from autogen.kernel.registry import StudioRegistry
from autogen.kernel.runner import KernelRunner

# домены студий -> ключевые слова маршрутизации CEO
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "web":       ["сайт", "лендинг", "landing", "веб", "web", "страниц", "каталог", "магазин", "портфолио"],
    "legal":     ["договор", "оферт", "nda", "соглашен", "прав", "юрисdic", "консультант", "закон", "согласие"],
    "content":   ["стать", "текст", "seo", "blog", "пост", "рассылк", "email", "описан"],
    "data":      ["sql", "дашборд", "dashboard", "аналитик", "отчет", "отчёт", "датасет", "pipeline", "график"],
    "education": ["урок", "курс", "тест", "quiz", "обучен", "образован", "модул"],
}


@dataclass(slots=True)
class CorporateTask:
    id: str
    title: str
    studio: str
    brief: dict
    status: str = "pending"
    result: Optional[dict] = None


@dataclass(slots=True)
class CorporateRun:
    id: str
    goal: str
    tasks: list[CorporateTask] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


class CEOAgent:
    def __init__(self, registry: StudioRegistry, llm: Optional[LLMManager] = None,
                 max_workers: int = 4) -> None:
        self.registry = registry
        self.llm = llm or LLMManager(backend="mock")
        self.max_workers = max_workers

    # ------------------------------------------------------------ маршрутизация
    def route(self, subtask_title: str) -> Optional[str]:
        """Выбрать студию по ключевым словам домена; при LLM — уточнить."""
        text = subtask_title.lower()
        best_studio, best_score = None, 0
        for studio in self.registry.all():
            domain = studio.meta.get("domain", "")
            score = sum(1 for kw in DOMAIN_KEYWORDS.get(domain, []) if kw in text)
            if domain and domain in text:
                score += 2
            if score > best_score:
                best_studio, best_score = studio.name, score
        return best_studio

    def decompose(self, goal: str) -> list[dict]:
        """Planner-ответ CEO: список {title, studio?}. Fallback — эвристика по словам."""
        prompt = (f"Ты — CEO ИИ-корпорации со студиями: "
                  f"{', '.join(self.registry.discover())}. Разбей цель на 1-5 подзадач.\n"
                  f"ЦЕЛЬ: {goal}\nВерни JSON: {{\"tasks\":[{{\"title\":\"...\",\"studio\":\"имя или null\"}}]}}")
        try:
            resp = self.llm.complete("planner", prompt)
            data = extract_json(resp.text)
            if data and isinstance(data.get("tasks"), list) and data["tasks"]:
                return [t for t in data["tasks"] if isinstance(t, dict) and t.get("title")]
        except Exception:
            pass
        # эвристический fallback: одна задача на каждый совпавший домен
        found = []
        text = goal.lower()
        for studio in self.registry.all():
            domain = studio.meta.get("domain", "")
            if any(kw in text for kw in DOMAIN_KEYWORDS.get(domain, [])):
                found.append({"title": f"{studio.meta.get('title', studio.name)}: {goal[:80]}",
                              "studio": studio.name})
        if not found:
            first = self.registry.discover()
            found = [{"title": goal[:100], "studio": first[0] if first else None}]
        return found

    # ------------------------------------------------------------ запуск
    def execute(self, goal: str) -> CorporateRun:
        crun = CorporateRun(id=uuid.uuid4().hex[:10], goal=goal)
        for td in self.decompose(goal):
            studio_name = td.get("studio") or self.route(td["title"])
            if studio_name is None:
                continue
            try:
                studio = self.registry.get(studio_name)
            except KeyError:
                continue
            skill = td.get("skill") or next(iter(studio.skills), None)
            brief = {"goal": td["title"], "audience": "конечный клиент",
                     "deliverable": studio.meta.get("title", studio_name),
                     "constraints": td.get("constraints", ""), "skill": skill or ""}
            crun.tasks.append(CorporateTask(id=uuid.uuid4().hex[:6], title=td["title"],
                                            studio=studio_name, brief=brief))

        def _run_task(task: CorporateTask) -> CorporateTask:
            llm = LLMManager(backend=self.llm.backend, mock_handler=self.llm.mock_handler)
            runner = KernelRunner(llm=llm)
            st = runner.run(self.registry.get(task.studio), task.brief,
                            skill_name=task.brief.get("skill") or None)
            task.status = st.status
            task.result = {"run_id": st.run_id, "passed": st.passed, "cycles": st.cycles,
                           "errors": [e.to_dict() for e in st.errors][:10]}
            return task

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            list(pool.map(_run_task, crun.tasks))

        passed = sum(1 for t in crun.tasks if t.status == "passed")
        crun.summary = {
            "total": len(crun.tasks), "passed": passed,
            "failed_or_escalated": len(crun.tasks) - passed,
            "success_rate": round(passed / max(1, len(crun.tasks)), 3),
        }
        return crun
