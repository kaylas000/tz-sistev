"""Registry: загрузка и поиск студий-вертикалей (ТЗ §4).

Студия = каталог verticals/{name}/ с vertical.yaml, CONSTITUTION.md,
BRIEF-TEMPLATE.md, skills/, validators/, references/, anti-slop/, gates/.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

VERTICALS_DIR_NAME = "verticals"

# Правило Конституции вида:  ## К-03. Название  /  - К-07: формулировка
_RULE_RE = re.compile(r"^#{1,4}\s*(К-\d+)\.?\s+(.+?)\s*$", re.M)
_RULE_LIST_RE = re.compile(r"^[-*]\s*\**(К-\d+)\**\s*[:.]\s*(.+?)\s*$", re.M)


@dataclass(slots=True)
class ConstitutionRule:
    id: str          # К-01
    text: str        # формулировка
    check: str = ""  # имя python-функции проверки в validators/constitution.py

    @property
    def error_code(self) -> str:
        num = int(re.sub(r"\D", "", self.id) or 0)
        return f"V-{num:02d}"


@dataclass(slots=True)
class SkillSpec:
    name: str
    path: Path
    meta: dict = field(default_factory=dict)

    @property
    def templates_dir(self) -> Path:
        return self.path / "templates"

    def template(self, role: str) -> Optional[Path]:
        for ext in ("md.j2", "j2", "md", "txt"):
            p = self.templates_dir / f"{role}.{ext}"
            if p.exists():
                return p
        return None


@dataclass(slots=True)
class Studio:
    name: str
    path: Path
    meta: dict
    rules: list[ConstitutionRule]
    skills: dict[str, SkillSpec]

    # -------------------------------------------------- factory
    @classmethod
    def load(cls, path: str | Path) -> "Studio":
        path = Path(path)
        vfile = path / "vertical.yaml"
        if not vfile.exists():
            raise FileNotFoundError(f"Студия {path} не содержит vertical.yaml")
        meta = yaml.safe_load(vfile.read_text(encoding="utf-8")) or {}
        rules = cls.parse_constitution(path / "CONSTITUTION.md")
        skills = cls.load_skills(path / "skills")
        return cls(name=path.name, path=path, meta=meta, rules=rules, skills=skills)

    @staticmethod
    def parse_constitution(cfile: Path) -> list[ConstitutionRule]:
        """Распарсить CONSTITUTION.md в проверяемые правила К-xx."""
        if not cfile.exists():
            return []
        text = cfile.read_text(encoding="utf-8")
        found: dict[str, str] = {}
        for m in _RULE_RE.finditer(text):
            found[m.group(1)] = m.group(2).strip()
        for m in _RULE_LIST_RE.finditer(text):
            found.setdefault(m.group(1), m.group(2).strip())
        rules = [ConstitutionRule(id=k, text=v) for k, v in sorted(
            found.items(), key=lambda kv: int(re.sub(r"\D", "", kv[0]) or 0))]
        return rules

    @staticmethod
    def load_skills(sdir: Path) -> dict[str, SkillSpec]:
        skills: dict[str, SkillSpec] = {}
        if not sdir.is_dir():
            return skills
        for sub in sorted(sdir.iterdir()):
            y = sub / "skill.yaml"
            if sub.is_dir() and y.exists():
                meta = yaml.safe_load(y.read_text(encoding="utf-8")) or {}
                skills[sub.name] = SkillSpec(name=sub.name, path=sub, meta=meta)
        return skills

    # -------------------------------------------------- helpers
    @property
    def brief_required_fields(self) -> list[str]:
        tpl = self.path / "BRIEF-TEMPLATE.md"
        fields: list[str] = []
        if tpl.exists():
            fields = re.findall(r"^##\s+([a-z0-9_]+)\s*$", tpl.read_text(encoding="utf-8"), re.M)
        if not fields:
            fields = ["goal", "audience", "deliverable"]
        return fields

    @property
    def budget_limits(self) -> dict:
        return self.meta.get("budget", {})

    @property
    def models(self) -> dict:
        return self.meta.get("models", {})

    @property
    def max_cycles(self) -> int:
        return int(self.meta.get("limits", {}).get("max_cycles", 10))

    @property
    def validators_path(self) -> Path:
        return self.path / "validators"

    @property
    def min_references(self) -> int:
        return int(self.meta.get("references", {}).get("min_count", 0))

    def reference_count(self) -> int:
        mdir = self.path / "references" / "metadata"
        return len(list(mdir.glob("*.yaml"))) + len(list(mdir.glob("*.yml"))) if mdir.is_dir() else 0


class StudioRegistry:
    """Реестр всех студий в каталоге verticals/."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def discover(self) -> list[str]:
        if not self.root.is_dir():
            return []
        return sorted(p.name for p in self.root.iterdir()
                      if p.is_dir() and (p / "vertical.yaml").exists())

    def get(self, name: str) -> Studio:
        path = self.root / name
        if not (path / "vertical.yaml").exists():
            raise KeyError(f"Студия '{name}' не найдена. Доступны: {', '.join(self.discover())}")
        return Studio.load(path)

    def all(self) -> list[Studio]:
        return [self.get(n) for n in self.discover()]
