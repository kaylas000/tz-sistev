"""CLI конструктора студий (ТЗ §9): `autogen-studio`.

Команды:
  create / populate-references / setup-constitution / add-skill / test / list
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autogen import __version__
from autogen.cli.builder import DOMAIN_DEFAULTS, create_studio
from autogen.kernel.registry import StudioRegistry
from autogen.kernel.references import REFERENCE_SOURCES, ReferenceScraper


def _root(arg: str | None) -> Path:
    return Path(arg).resolve() if arg else Path.cwd()


def cmd_create(args) -> int:
    base = create_studio(_root(args.root), args.name, domain=args.domain,
                         template=args.template, title=args.title)
    print(f"✔ Студия '{args.name}' создана: {base}")
    print(f"  домен={args.domain} template={args.template} "
          f"скиллы={len(list((base/'skills').glob('*/skill.yaml')))}")
    return 0


def cmd_populate(args) -> int:
    root = _root(args.root)
    reg = StudioRegistry(root / "verticals")
    studio = reg.get(args.name)
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    scraper = ReferenceScraper(offline=args.offline)
    out = studio.path / "references"
    total = 0
    for src in sources:
        filters = {}
        if args.category:
            filters["category"] = args.category
        if args.color:
            filters["color"] = args.color
        if args.style:
            filters["style"] = args.style
        items = scraper.scrape(src, filters=filters, limit=args.limit, out_dir=out)
        total += len(items)
        print(f"  {src}: +{len(items)} референсов")
    used = list(dict.fromkeys(sources + studio.meta.get("references", {}).get("sources", [])))
    scraper.write_sources_yaml(out / "sources.yaml", used)
    have = studio.reference_count()
    need = studio.min_references
    status = "OK" if have >= need else f"МАЛО (нужно минимум {need})"
    print(f"✔ '{args.name}': добавлено {total}, всего metadata: {have} — {status}")
    return 0


def cmd_setup_constitution(args) -> int:
    root = _root(args.root)
    reg = StudioRegistry(root / "verticals")
    studio = reg.get(args.name)
    print(f"Конституция '{args.name}' ({len(studio.rules)} правил):")
    for r in studio.rules:
        print(f"  {r.id} [{r.error_code}] {r.text.splitlines()[0][:70]}")
    if args.interactive:
        print("\nДобавьте правило в формате 'К-NN. Текст' в "
              f"{studio.path / 'CONSTITUTION.md'} и повторите команду для проверки.")
    return 0


def cmd_add_skill(args) -> int:
    root = _root(args.root)
    reg = StudioRegistry(root / "verticals")
    studio = reg.get(args.name)
    fmt = {"web": "html", "legal": "markdown", "content": "markdown",
           "data": "python", "education": "markdown"}.get(studio.meta.get("domain", "web"), "text")
    sdir = studio.path / "skills" / args.skill
    if (sdir / "skill.yaml").exists():
        print(f"Скилл '{args.skill}' уже существует в '{args.name}'")
        return 1
    from autogen.cli.builder import SKILL_YAML, PLANNER_TPL, CODER_TPL, VERIFIER_TPL, FIXER_TPL
    (sdir / "templates").mkdir(parents=True, exist_ok=True)
    (sdir / "hooks").mkdir(parents=True, exist_ok=True)
    (sdir / "skill.yaml").write_text(SKILL_YAML.format(
        skill=args.skill, skill_title=args.skill.replace("_", " ").title(), fmt=fmt), encoding="utf-8")
    (sdir / "hooks" / "__init__.py").write_text(
        "def pre_execute(ctx):\n    return ctx\n\n\ndef post_execute(ctx, artifact):\n"
        "    return artifact\n", encoding="utf-8")
    for role, tpl in (("planner", PLANNER_TPL), ("coder", CODER_TPL),
                      ("verifier", VERIFIER_TPL), ("fixer", FIXER_TPL)):
        (sdir / "templates" / f"{role}.md.j2").write_text(
            tpl.replace("{title}", studio.meta.get("title", args.name)), encoding="utf-8")
    print(f"✔ Скилл '{args.skill}' добавлен в студию '{args.name}'")
    return 0


def cmd_test(args) -> int:
    root = _root(args.root)
    reg = StudioRegistry(root / "verticals")
    studio = reg.get(args.name)
    from autogen.kernel.llm import LLMManager
    from autogen.kernel.runner import KernelRunner
    brief = {"goal": args.brief, "audience": "тест", "deliverable": "тест",
             "constraints": "", "skill": args.skill or ""}
    runner = KernelRunner(llm=LLMManager(backend="mock"), use_llm_judge=False)
    st = runner.run(studio, brief, skill_name=args.skill)
    print(json.dumps({"run_id": st.run_id, "status": st.status, "cycles": st.cycles,
                      "passed": st.passed, "needs_human_review": st.needs_human_review,
                      "errors": [e.to_dict() for e in st.errors]}, ensure_ascii=False, indent=2))
    return 0 if st.passed else 2


def cmd_list(args) -> int:
    root = _root(args.root)
    reg = StudioRegistry(root / "verticals")
    names = reg.discover()
    if not names:
        print("Студии не найдены. Создайте: autogen-studio create --name my_studio --domain web")
        return 0
    for n in names:
        s = reg.get(n)
        print(f"{n:24s} domain={s.meta.get('domain','?'):10s} правил={len(s.rules):3d} "
              f"скиллов={len(s.skills):2d} референсов={s.reference_count():4d}/{s.min_references}")
    return 0


def cmd_sources(args) -> int:
    for k, v in REFERENCE_SOURCES.items():
        print(f"{k:20s} {v['url']:40s} kind={v['kind']:10s} фильтры={','.join(v.get('filters', [])) or '-'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="autogen-studio",
                                description="Конструктор ИИ-студий АвтоГен v" + __version__)
    p.add_argument("--root", help="Корень проекта (по умолчанию cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Создать новую студию")
    c.add_argument("--name", required=True)
    c.add_argument("--domain", default="web", choices=list(DOMAIN_DEFAULTS))
    c.add_argument("--template", default="basic", choices=["basic", "advanced"])
    c.add_argument("--title")
    c.set_defaults(fn=cmd_create)

    pr = sub.add_parser("populate-references", help="Заполнить студию референсами из каталогов")
    pr.add_argument("--name", required=True)
    pr.add_argument("--sources", required=True, help="Список через запятую: lapa,land-book,awwwards")
    pr.add_argument("--limit", type=int, default=50)
    pr.add_argument("--category")
    pr.add_argument("--color")
    pr.add_argument("--style")
    pr.add_argument("--offline", action="store_true", help="Не ходить в сеть; детерминированный синтетический сбор")
    pr.set_defaults(fn=cmd_populate)

    sc = sub.add_parser("setup-constitution", help="Показать/проверить Конституцию студии")
    sc.add_argument("--name", required=True)
    sc.add_argument("--interactive", action="store_true")
    sc.set_defaults(fn=cmd_setup_constitution)

    ask = sub.add_parser("add-skill", help="Добавить скилл в студию")
    ask.add_argument("--name", required=True)
    ask.add_argument("--skill", required=True)
    ask.set_defaults(fn=cmd_add_skill)

    t = sub.add_parser("test", help="Протестировать студию на mock-LLM сквозным циклом")
    t.add_argument("--name", required=True)
    t.add_argument("--brief", required=True)
    t.add_argument("--skill")
    t.set_defaults(fn=cmd_test)

    ls = sub.add_parser("list", help="Список студий")
    ls.set_defaults(fn=cmd_list)

    sr = sub.add_parser("sources", help="Каталог источников референсов (ТЗ §2)")
    sr.set_defaults(fn=cmd_sources)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except (KeyError, FileNotFoundError, ValueError, FileExistsError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
