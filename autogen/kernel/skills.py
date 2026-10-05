"""Skills Engine: загрузка скиллов, рендер Jinja2-промптов, pre/post hooks (ТЗ §4).

Если Jinja2 не установлен — используется простой fallback-рендерер {{ var }}.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any, Optional


def render_template(text: str, variables: dict[str, Any]) -> str:
    """Рендер Jinja2 с graceful fallback на {{ var }}-подстановку."""
    try:
        from jinja2 import Template  # type: ignore
        return Template(text, autoescape=False).render(**variables)
    except ImportError:
        def _sub(m: re.Match) -> str:
            key = m.group(1).strip()
            val: Any = variables
            for part in key.split("."):
                if isinstance(val, dict):
                    val = val.get(part, "")
                else:
                    val = getattr(val, part, "")
            return str(val)
        return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", _sub, text)


class SkillRunner:
    """Обёртка одного скилла студии: промпты + hooks + конфигурация."""

    def __init__(self, studio, skill_spec) -> None:
        self.studio = studio
        self.spec = skill_spec
        self.meta = skill_spec.meta or {}

    # ------------------------------------------------------- промпты
    def prompt(self, role: str, variables: dict[str, Any]) -> Optional[str]:
        """Собрать промпт для роли (planner/coder/verifier/fixer)."""
        tpl_path = self.spec.template(role)
        default_path = self.studio.path / "skills" / "_default" / "templates"
        if tpl_path is None and default_path.is_dir():
            for ext in ("md.j2", "j2", "md", "txt"):
                p = default_path / f"{role}.{ext}"
                if p.exists():
                    tpl_path = p
                    break
        if tpl_path is None:
            return None
        base_vars = {
            "brief": variables.get("brief", {}),
            "studio": {"name": self.studio.name, "constitution": [vars(r) for r in self.studio.rules]},
            "skill": self.meta,
            "references": variables.get("references", []),
            "errors": variables.get("errors", []),
            "artifact": variables.get("artifact", ""),
            **variables,
        }
        return render_template(tpl_path.read_text(encoding="utf-8"), base_vars)

    # ------------------------------------------------------- hooks
    def _load_hooks_module(self) -> Optional[Any]:
        hooks_dir = self.spec.path / "hooks"
        init = hooks_dir / "__init__.py"
        if not init.exists():
            return None
        spec = importlib.util.spec_from_file_location(
            f"hooks_{self.studio.name}_{self.spec.name}", init)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def pre_execute(self, context: dict) -> dict:
        mod = self._load_hooks_module()
        if mod and hasattr(mod, "pre_execute"):
            return mod.pre_execute(context) or context
        return context

    def post_execute(self, context: dict, artifact: str) -> str:
        mod = self._load_hooks_module()
        if mod and hasattr(mod, "post_execute"):
            return mod.post_execute(context, artifact) or artifact
        return artifact

    # ------------------------------------------------------- мета
    @property
    def artifact_kind(self) -> str:
        return self.meta.get("artifact", "text")

    @property
    def output_schema(self) -> Optional[dict]:
        return self.meta.get("output_schema")
