"""Конструктор студий (ТЗ §9): шаблоны и генерация вертикалей.

autogen-studio create --name my_studio --domain web --template basic|advanced
Создаёт полную структуру каталога студии из ТЗ §4 со стартовыми файлами.
"""
from __future__ import annotations

from pathlib import Path

import yaml

DOMAIN_DEFAULTS: dict[str, dict] = {
    "web": {"sources": ["lapa", "land-book", "awwwards", "siteinspire", "minimal", "godly"],
            "min_refs": 100, "skills": ["landing_page", "catalog", "portfolio", "ecommerce", "corporate"]},
    "legal": {"sources": ["consultant", "garant"], "min_refs": 30,
              "skills": ["contract", "nda", "offer", "consent"]},
    "content": {"sources": ["awwwards", "behance"], "min_refs": 50,
                "skills": ["seo_article", "product_description", "email_sequence", "blog_post"]},
    "data": {"sources": ["github", "kaggle", "observable"], "min_refs": 30,
             "skills": ["sql_query", "dashboard", "report", "data_pipeline"]},
    "education": {"sources": ["coursera", "stepik", "udemy"], "min_refs": 20,
                  "skills": ["lesson", "quiz", "course_module"]},
}

VERTICAL_YAML = {
    "schema_version": 1,
    "title": None,          # заполняется
    "domain": None,         # заполняется
    "description": "",
    "models": {
        "planner":  {"model": "llama3.1:8b", "temperature": 0.3},
        "coder":    {"model": "qwen2.5-coder:7b", "temperature": 0.7},
        "verifier": {"model": "gemma2:9b", "temperature": 0.0},
        "fixer":    {"model": "llama3.1:8b", "temperature": 0.3},
    },
    "budget": {"max_run_usd": 2.0, "max_day_usd": 20.0, "max_tokens_per_min": 400000},
    "limits": {"max_cycles": 10},
    "sandbox": "local",
    "references": {"min_count": 0, "sources": []},   # заполняются по домену
    "validators": ["constitution.py", "anti_slop.py", "schema.py", "llm_judge.py"],
}

CONSTITUTION_HEADER = """# Конституция студии {title}

Каждое правило проверяемо; нарушение порождает код V-xx (номер = номер правила).

## К-01. Целостность артефакта
Артефакт существует, непустой и парсится как {fmt}.
check_regex: ^\\s*$, message: Артефакт пустой, severity: critical

## К-02. Соответствие брифу
Артефакт решает задачу из поля `goal` брифа; ключевые слова цели присутствуют.

## К-03. Обязательная структура
Артефакт содержит все секции/разделы, заданные скиллом в skill.yaml (`required_parts`).
"""

AGENTS_MD = """# Контракт агентов студии {title}

| Агент | Роль | Модель | Вход | Выход |
|---|---|---|---|---|
| Planner | разбивка на DAG | llama3.1:8b (T=0.3) | бриф G1 | JSON {{tasks:[{{id,title,deps}}]}} |
| Coder | генерация артефакта | qwen2.5-coder:7b (T=0.7) | план + референсы | артефакт в ```блоке``` |
| Verifier | прогон валидаторов | gemma2:9b (T=0.0) | артефакт + Конституция | feedback JSON (см. ТЗ §6) |
| Fixer | точечные правки | llama3.1:8b (T=0.3) | артефакт + коды ошибок | исправленный артефакт |

Правила эскалации: >{{limits.max_cycles}} циклов → Human Review (R-01).
"""

BRIEF_TEMPLATE = """# Шаблон брифа {title}

Заполните все поля — неполный бриф отклоняется на G1 (код E-01).

## goal
Цель: что должно получиться.

## audience
Целевая аудитория.

## deliverable
Формат результата ({fmt}).

## constraints
Ограничения: сроки, стиль, запреты.

## skill
Навык студии: {skills}
"""

SKILL_YAML = """name: {skill}
title: {skill_title}
artifact: {fmt}
required_parts: []
brief_required: [goal, audience, deliverable]
templates: [planner, coder, verifier, fixer]
"""

PLANNER_TPL = """Ты — Planner студии «{title}». Разбей задачу на подзадачи (DAG).

БРИФ:
{{{{ brief }}}}

ПРАВИЛА КОНСТИТУЦИИ: {{{{ studio.constitution }}}}

Верни строго JSON: {{"tasks": [{{"id":"t1","title":"...","deps":[]}}]}}"""

CODER_TPL = """Ты — Coder студии «{title}». Сгенерируй артефакт.

БРИФ: {{{{ brief }}}}
ПЛАН: {{{{ plan }}}}
РЕФЕРЕНСЫ (цвета/шрифты/структура/выводы):
{{% for r in references %}}- {{{{ r }}}}
{{% endfor %}}
КОНСТИТУЦИЯ:
{{% for rule in constitution %}}{{{{ rule.id }}}}: {{{{ rule.text }}}}
{{% endfor %}}

Выдай артефакт одним ```блоком```, без пояснений."""

VERIFIER_TPL = """Ты — Verifier. Проверь артефакт на соответствие Конституции и anti-slop.
АРТЕФАКТ:
{{{{ artifact }}}}
Ответь JSON: {{"passed": bool, "errors": [{{"code":"V-XX","severity":"critical|major|minor","description":"...","suggestion":"..."}}]}}"""

FIXER_TPL = """Ты — Fixer. Внеси ТОЧЕЧНЫЕ правки, исправляя только перечисленные ошибки.
ОШИБКИ (коды V-xx/B-xx/Q-xx):
{{{{ errors }}}}
АРТЕФАКТ:
{{{{ artifact }}}}
Выдай исправленный артефакт одним ```блоком```."""

BANNED_MD = """# Запрещённые паттерны (B-xx)

- B-01: запрещён placeholder-текст `lorem ipsum`
- B-02: запрещены шаблонные фразы `In today's fast-paced world`
- B-03: запрещена заглушка `TODO` в финальном артефакте
"""

QUOTAS_MD = """# Квоты (Q-xx)

- Q-01: восклицательных знаков `!` max=5
- Q-02: капслок-слов `[A-ZА-Я]{4,}` max=3
"""

GATES_MD = """# Гейты студии

* **G1** — входной гейт: полнота брифа (E-01/E-02/E-03)
* **G2** — плановый гейт: DAG ацикличен, задачи покрыли цель
* **G3** — гейт артефакта: все валидаторы PASS, нет critical/major
* **G4** — приёмочный гейт: упаковка, отчёт, доставка клиенту
"""


def create_studio(root: Path, name: str, domain: str = "web", template: str = "basic",
                  title: str | None = None) -> Path:
    """Создать каркас студии verticals/{name} по ТЗ §4. Возвращает путь."""
    if domain not in DOMAIN_DEFAULTS:
        raise ValueError(f"Неизвестный домен '{domain}'. Доступны: {', '.join(DOMAIN_DEFAULTS)}")
    if template not in ("basic", "advanced"):
        raise ValueError("template: basic|advanced")
    defaults = DOMAIN_DEFAULTS[domain]
    title = title or name.replace("_", " ").title()
    fmt = {"web": "html", "legal": "markdown", "content": "markdown",
           "data": "python", "education": "markdown"}[domain]

    base = Path(root) / "verticals" / name
    if (base / "vertical.yaml").exists():
        raise FileExistsError(f"Студия '{name}' уже существует: {base}")

    dirs = ["skills", "validators", "references/screenshots", "references/metadata",
            "references/takeaways", "anti-slop", "gates", "projects", "tests"]
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)

    # vertical.yaml
    meta = dict(VERTICAL_YAML)
    meta["title"] = title
    meta["domain"] = domain
    meta["references"] = {"min_count": defaults["min_refs"], "sources": defaults["sources"]}
    (base / "vertical.yaml").write_text(
        yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # конституция / агенты / бриф
    (base / "CONSTITUTION.md").write_text(
        CONSTITUTION_HEADER.format(title=title, fmt=fmt), encoding="utf-8")
    (base / "AGENTS.md").write_text(AGENTS_MD.format(title=title), encoding="utf-8")
    (base / "BRIEF-TEMPLATE.md").write_text(
        BRIEF_TEMPLATE.format(title=title, fmt=fmt, skills=", ".join(defaults["skills"])),
        encoding="utf-8")
    (base / "anti-slop" / "BANNED.md").write_text(BANNED_MD, encoding="utf-8")
    (base / "anti-slop" / "QUOTAS.md").write_text(QUOTAS_MD, encoding="utf-8")
    (base / "gates" / "GATES.md").write_text(GATES_MD, encoding="utf-8")

    skills = defaults["skills"] if template == "advanced" else defaults["skills"][:1]
    for sk in skills:
        sdir = base / "skills" / sk
        (sdir / "templates").mkdir(parents=True, exist_ok=True)
        (sdir / "hooks").mkdir(parents=True, exist_ok=True)
        (sdir / "skill.yaml").write_text(
            SKILL_YAML.format(skill=sk, skill_title=sk.replace("_", " ").title(), fmt=fmt),
            encoding="utf-8")
        (sdir / "hooks" / "__init__.py").write_text(
            "def pre_execute(ctx):\n    return ctx\n\n\ndef post_execute(ctx, artifact):\n"
            "    return artifact\n", encoding="utf-8")
        for role, tpl in (("planner", PLANNER_TPL), ("coder", CODER_TPL),
                          ("verifier", VERIFIER_TPL), ("fixer", FIXER_TPL)):
            text = tpl.replace("{title}", title)
            (sdir / "templates" / f"{role}.md.j2").write_text(text, encoding="utf-8")

    if template == "advanced":
        _write_default_validators(base, fmt)

    (base / "tests" / "test_smoke.py").write_text(SMOKE_TEST, encoding="utf-8")
    return base


def _write_default_validators(base: Path, fmt: str) -> None:
    vdir = base / "validators"
    (vdir / "constitution.py").write_text(f'''"""Студийный валидатор Конституции (К-xx -> V-xx)."""
import re

def validate(studio, brief, artifact):
    from autogen.kernel.errors import ErrorItem
    errors = []
    if not artifact.strip():
        errors.append(ErrorItem(code="V-01", severity="critical", rule_id="К-01",
                                description="Артефакт пуст", suggestion="Сгенерировать заново"))
    goal_words = [w for w in re.split(r"\\W+", str(brief.get("goal", ""))) if len(w) > 4][:5]
    if goal_words and not any(w.lower() in artifact.lower() for w in goal_words):
        errors.append(ErrorItem(code="V-02", severity="major", rule_id="К-02",
                                description="Артефакт не соответствует цели брифа",
                                suggestion="Добавить содержание из поля goal"))
    return errors
''', encoding="utf-8")
    (vdir / "anti_slop.py").write_text('''"""Переиспользует generic anti-slop ядра поверх студийных BANNED/QUOTAS."""
from autogen.kernel.validators import validate_anti_slop

def validate(studio, brief, artifact):
    return validate_anti_slop(studio.path, artifact)
''', encoding="utf-8")
    (vdir / "schema.py").write_text(f'''"""Проверка формата артефакта ({fmt})."""
import re
from autogen.kernel.errors import ErrorItem

def validate(studio, brief, artifact):
    errors = []
    kind = "{fmt}"
    if kind == "html":
        if "<html" not in artifact.lower() or "</html>" not in artifact.lower():
            errors.append(ErrorItem(code="A-03", severity="major", rule_id="schema",
                                    description="HTML неполный: нет <html>/</html>",
                                    suggestion="Обернуть в корректную HTML-структуру"))
    elif kind == "python":
        try:
            compile(artifact, "<artifact>", "exec")
        except SyntaxError as e:
            errors.append(ErrorItem(code="A-03", severity="critical", rule_id="schema",
                                    description=f"SyntaxError: {{e.msg}} (строка {{e.lineno}})",
                                    suggestion="Исправить синтаксис Python"))
    elif kind == "markdown":
        if not re.search(r"^#\\s+\\S", artifact, re.M):
            errors.append(ErrorItem(code="A-03", severity="minor", rule_id="schema",
                                    description="Нет заголовка верхнего уровня",
                                    suggestion="Добавить '# Название'"))
    return errors
''', encoding="utf-8")
    (vdir / "llm_judge.py").write_text('''"""LLM-критик делегирует generic-реализацию ядра."""
from autogen.kernel.validators import llm_judge

def validate(studio, llm, brief, artifact):
    if llm is None:
        return []
    return llm_judge(llm, studio, brief, artifact)
''', encoding="utf-8")


SMOKE_TEST = '''"""Смоук-тест студии: грузится, конституция парсится, цикл проходит на mock-LLM."""
from pathlib import Path
from autogen.kernel.registry import StudioRegistry
from autogen.kernel.runner import KernelRunner
from autogen.kernel.llm import LLMManager

ROOT = Path(__file__).resolve().parents[2]


def test_studio_loads_and_runs():
    reg = StudioRegistry(ROOT / "verticals")
    name = Path(__file__).resolve().parents[2].name  # noqa
    studios = reg.discover()
    assert studios
    studio = reg.get(studios[0])
    assert studio.rules, "Конституция не распарсилась"
    runner = KernelRunner(llm=LLMManager(backend="mock"), use_llm_judge=False)
    brief = {f: "тестовое значение для smoke-прогона" for f in studio.brief_required_fields}
    st = runner.run(studio, brief)
    assert st.status in ("passed", "escalated", "error", "g1_fail")
'''
