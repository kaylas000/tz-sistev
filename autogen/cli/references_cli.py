"""CLI сборщика референсов (ТЗ §8.1): `autogen-references`.

  autogen-references scrape --source lapa.ninja --category saas --limit 50
  autogen-references list-sources
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from autogen.kernel.references import REFERENCE_SOURCES, ReferenceScraper


def _normalize_source(name: str) -> str:
    """lapa.ninja -> lapa; land-book.com -> land-book; awwwards.com -> awwwards."""
    name = name.lower().strip()
    if name in REFERENCE_SOURCES:
        return name
    stem = re.sub(r"\.(com|ru|net|org|website|gallery|ninja)$", "", name).replace(".", "-")
    for key in REFERENCE_SOURCES:
        if key == stem or stem.startswith(key) or key.startswith(stem):
            return key
    raise KeyError(f"Неизвестный источник '{name}'. Список: autogen-references list-sources")


def cmd_scrape(args) -> int:
    source = _normalize_source(args.source)
    filters = {}
    for f in ("category", "color", "style", "type", "industry", "section"):
        v = getattr(args, f, None)
        if v:
            filters[f] = v
    scraper = ReferenceScraper(offline=args.offline)
    out_dir = Path(args.out) if args.out else None
    items = scraper.scrape(source, filters=filters, limit=args.limit, out_dir=out_dir)
    if out_dir:
        print(f"✔ {len(items)} референсов сохранено в {out_dir}/metadata/")
    else:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    return 0


def cmd_list_sources(args) -> int:
    for k, v in REFERENCE_SOURCES.items():
        print(f"{k:20s} {v['url']:38s} kind={v['kind']:9s} "
              f"фильтры={','.join(v.get('filters', [])) or '-'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="autogen-references",
                                description="Сборщик референсов из каталогов дизайна (ТЗ §2)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scrape", help="Собрать референсы источника")
    s.add_argument("--source", required=True, help="lapa.ninja | land-book.com | awwwards.com | ...")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--category"); s.add_argument("--color"); s.add_argument("--style")
    s.add_argument("--type"); s.add_argument("--industry"); s.add_argument("--section")
    s.add_argument("--out", help="Каталог references/ студии; без него — stdout JSON")
    s.add_argument("--offline", action="store_true")
    s.set_defaults(fn=cmd_scrape)

    ls = sub.add_parser("list-sources", help="Каталог доступных источников")
    ls.set_defaults(fn=cmd_list_sources)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except (KeyError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
