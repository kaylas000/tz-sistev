"""LangGraph Runner: цикл Бриф → G1 → Planner → Coder → Verifier → (Fixer ↻) → G3 → Packager.

Если LangGraph установлен — граф строится через StateGraph; иначе используется
эквивалентный прямой движок с той же топологией (для окружений без langgraph).
Превышение лимита циклов -> эскалация на Human Review (ТЗ §5).
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .budget import BudgetExceeded, BudgetLimits, BudgetManager
from .errors import ErrorItem, make_feedback
from .llm import LLMManager, extract_code_block, extract_json
from .registry import Studio
from .sandbox import make_sandbox
from .skills import SkillRunner
from .validators import ValidationPipeline, validate_brief


@dataclass(slots=True)
class RunState:
    run_id: str
    studio: str
    skill: str
    brief: dict
    artifact: str = ""
    plan: Optional[dict] = None
    cycles: int = 0
    errors: list[ErrorItem] = field(default_factory=list)
    passed: bool = False
    needs_human_review: bool = False
    status: str = "new"           # new|g1_fail|running|passed|escalated|error
    log: list[dict] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)

    def step(self, node: str, **info) -> None:
        self.log.append({"ts": round(time.time() - self.started_at, 3), "node": node, **info})


class KernelRunner:
    """Оркестрация цикла выполнения одной задачи студии."""

    def __init__(
        self,
        llm: Optional[LLMManager] = None,
        budget: Optional[BudgetManager] = None,
        sandbox_kind: str = "local",
        use_llm_judge: bool = True,
        projects_root: Optional[str | Path] = None,
    ) -> None:
        self.llm = llm or LLMManager(backend="mock")
        self.budget = budget or BudgetManager(limits=BudgetLimits())
        self.sandbox_kind = sandbox_kind
        self.use_llm_judge = use_llm_judge
        self.projects_root = Path(projects_root) if projects_root else None

    # ------------------------------------------------------------- узлы графа
    def node_g1(self, st: RunState, studio: Studio, skill: SkillRunner) -> list[ErrorItem]:
        """G1: входной гейт — проверка полноты брифа."""
        required = list(studio.brief_required_fields)
        skill_required = skill.meta.get("brief_required", [])
        required += [f for f in skill_required if f not in required]
        return validate_brief(st.brief, required)

    def node_planner(self, st: RunState, studio: Studio, skill: SkillRunner) -> dict:
        prompt = skill.prompt("planner", {"brief": st.brief}) or \
            f"Разбей задачу на подзадачи (DAG) и верни JSON {{\"tasks\":[...]}}. Бриф: {st.brief}"
        resp = self.llm.complete("planner", prompt, context={"brief": st.brief})
        plan = extract_json(resp.text) or {"tasks": [{"id": "t1", "title": "Создать артефакт", "deps": []}]}
        st.plan = plan
        return plan

    def node_coder(self, st: RunState, studio: Studio, skill: SkillRunner) -> str:
        refs = _load_reference_takeaways(studio, limit=8)
        prompt = skill.prompt("coder", {
            "brief": st.brief, "plan": st.plan, "references": refs,
            "constitution": [vars(r) for r in studio.rules],
        }) or f"Сгенерируй артефакт по брифу: {st.brief}. Правила: {[r.id for r in studio.rules]}"
        ctx = skill.pre_execute({"brief": st.brief, "plan": st.plan, "prompt": prompt})
        prompt = ctx.get("prompt", prompt)
        resp = self.llm.complete("coder", prompt, context={"brief": st.brief, "plan": st.plan})
        artifact = extract_code_block(resp.text)
        artifact = skill.post_execute(ctx, artifact)
        st.artifact = artifact
        return artifact

    def node_verifier(self, st: RunState, studio: Studio, skill: SkillRunner) -> list[ErrorItem]:
        pipeline = ValidationPipeline(studio, llm=self.llm if self.use_llm_judge else None,
                                      use_llm_judge=self.use_llm_judge)
        errors = pipeline.run(st.brief, st.artifact)
        # для исполняемых скиллов — прогон в песочнице
        if skill.artifact_kind == "python":
            errors += self._sandbox_check(st, skill, errors)
        st.errors = errors
        return errors

    def _sandbox_check(self, st: RunState, skill: SkillRunner, errors: list[ErrorItem]) -> list[ErrorItem]:
        sbx = make_sandbox(self.sandbox_kind)
        try:
            res = sbx.run_python(st.artifact, timeout=skill.meta.get("sandbox_timeout", 20))
        finally:
            sbx.cleanup()
        if res.ok:
            return []
        code = res.error.split(":")[0] if res.error.startswith(("L-", "E-")) else "L-01"
        detail = res.error or (res.stderr[-500:] if res.stderr else f"exit={res.exit_code}")
        return [ErrorItem(code=code, severity="critical", rule_id="sandbox",
                          description=f"Артефакт не исполнился в песочнице: {detail}",
                          suggestion="Исправьте ошибку исполнения/синтаксиса")]

    def node_fixer(self, st: RunState, studio: Studio, skill: SkillRunner) -> str:
        feedback = make_feedback(st.errors)
        prompt = skill.prompt("fixer", {
            "brief": st.brief, "artifact": st.artifact, "errors": feedback["errors"],
        }) or ("Внеси точечные правки в артефакт по ошибкам.\nАРТЕФАКТ:\n"
               f"{st.artifact}\nОШИБКИ:\n{json.dumps(feedback['errors'], ensure_ascii=False)}")
        resp = self.llm.complete("fixer", prompt, context={"errors": feedback["errors"]})
        st.artifact = extract_code_block(resp.text)
        return st.artifact

    def node_packager(self, st: RunState, studio: Studio, skill: SkillRunner) -> Optional[Path]:
        """G3 + Packager: сохранить артефакт в verticals/{studio}/projects/{run_id}/."""
        base = self.projects_root or (studio.path / "projects")
        outdir = Path(base) / st.run_id
        outdir.mkdir(parents=True, exist_ok=True)
        ext = {"html": ".html", "python": ".py", "markdown": ".md"}.get(skill.artifact_kind, ".txt")
        (outdir / f"artifact{ext}").write_text(st.artifact, encoding="utf-8")
        report = {
            "run_id": st.run_id, "studio": st.studio, "skill": st.skill,
            "brief": st.brief, "cycles": st.cycles, "passed": st.passed,
            "status": st.status, "log": st.log,
            "budget": self.budget.summary(st.run_id),
        }
        (outdir / "run-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return outdir

    # ------------------------------------------------------------- обход
    def run(self, studio: Studio, brief: dict, skill_name: Optional[str] = None) -> RunState:
        skill_name = skill_name or brief.get("skill") or next(iter(studio.skills), "default")
        spec = studio.skills.get(skill_name)
        if spec is None:
            st = RunState(run_id=_rid(), studio=studio.name, skill=skill_name, brief=brief,
                          status="g1_fail")
            st.errors = [ErrorItem(code="E-03", severity="critical", rule_id=skill_name,
                                   description=f"Неизвестный скилл '{skill_name}'",
                                   suggestion=f"Доступны: {', '.join(studio.skills) or 'нет'}")]
            return st

        skill = SkillRunner(studio, spec)
        st = RunState(run_id=_rid(), studio=studio.name, skill=skill_name, brief=brief)

        # --- G1
        g1_errors = self.node_g1(st, studio, skill)
        st.step("G1", errors=[e.to_dict() for e in g1_errors])
        if g1_errors:
            st.errors = g1_errors
            st.status = "g1_fail"
            return st

        try:
            # --- Planner
            self.node_planner(st, studio, skill)
            st.step("planner", tasks=len((st.plan or {}).get("tasks", [])))

            max_cycles = studio.max_cycles
            while True:
                cycle = self.budget.register_cycle(st.run_id)
                st.cycles = cycle
                # --- Coder (первый цикл) / Fixer (следующие) уже дали артефакт
                if cycle == 1 or not st.artifact:
                    self.node_coder(st, studio, skill)
                    st.step("coder", length=len(st.artifact))
                # --- Verifier
                errors = self.node_verifier(st, studio, skill)
                st.step("verifier", errors=[e.to_dict() for e in errors])
                critical_major = [e for e in errors if e.severity in ("critical", "major")]
                if not critical_major:
                    st.passed = True
                    st.status = "passed"
                    break
                if cycle >= max_cycles:
                    st.needs_human_review = True
                    st.status = "escalated"
                    st.errors = critical_major
                    st.step("human_review", reason="R-01")
                    break
                # --- Fixer
                self.node_fixer(st, studio, skill)
                st.step("fixer", target_codes=[e.code for e in critical_major])

            if st.passed:
                out = self.node_packager(st, studio, skill)
                st.step("G3+packager", path=str(out) if out else None)

        except BudgetExceeded as exc:
            st.status = "error"
            code = "R-01" if "R-01" in str(exc) else "R-02"
            st.errors = [ErrorItem(code=code, severity="critical",
                                   description=str(exc), suggestion="Уменьшите бюджет/циклы или разбейте задачу")]
            st.step("budget_stop", error=str(exc))
        except Exception as exc:  # noqa: BLE001
            st.status = "error"
            st.errors = [ErrorItem(code="L-01", severity="critical",
                                   description=f"Ошибка выполнения цикла: {exc}",
                                   suggestion="Проверьте доступность LLM-бэкенда и целостность студии")]
            st.step("error", error=str(exc))
        finally:
            # учёт токенов в бюджете
            total_tokens = sum(c.total_tokens for c in self.llm.calls)
            self.budget.charge(st.run_id, tokens=total_tokens, cost_usd=0.0)
        return st


def _rid() -> str:
    return uuid.uuid4().hex[:12]


def _load_reference_takeaways(studio: Studio, limit: int = 8) -> list[dict]:
    mdir = studio.path / "references" / "metadata"
    refs: list[dict] = []
    if not mdir.is_dir():
        return refs
    import yaml
    files = sorted(mdir.glob("*.y*ml"))[:limit]
    for f in files:
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        refs.append({k: d.get(k) for k in ("source", "style", "industry", "colors", "layout", "takeaway")
                     if d.get(k) is not None})
    return refs


# ---------------------------------------------------------------- LangGraph (опционально)
def build_langgraph_graph(runner: KernelRunner, studio: Studio, skill_name: str):
    """Построить тот же цикл поверх langgraph.StateGraph, если пакет доступен."""
    try:
        from langgraph.graph import StateGraph, END  # type: ignore
    except ImportError:
        return None

    spec = studio.skills[skill_name]
    skill = SkillRunner(studio, spec)

    g = StateGraph(dict)

    def _wrap(node_fn):
        def inner(state: dict) -> dict:
            st: RunState = state["_st"]
            node_fn(st)
            return state
        return inner

    g.add_node("g1", lambda s: s)
    g.add_node("planner", _wrap(lambda st: runner.node_planner(st, studio, skill)))
    g.add_node("coder", _wrap(lambda st: runner.node_coder(st, studio, skill)))
    g.add_node("verifier", _wrap(lambda st: runner.node_verifier(st, studio, skill)))
    g.add_node("fixer", _wrap(lambda st: runner.node_fixer(st, studio, skill)))
    g.set_entry_point("planner")
    g.add_edge("planner", "coder")
    g.add_edge("coder", "verifier")
    g.add_conditional_edges(
        "verifier",
        lambda s: "end" if not any(e.severity in ("critical", "major") for e in s["_st"].errors)
                  else "fixer",
        {"end": END, "fixer": "fixer"},
    )
    g.add_edge("fixer", "verifier")
    return g.compile()
