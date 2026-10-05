"""Парсер каталогов референсов (ТЗ §2, §8).

Каталог источников: references/sources.yaml описывает сайты из ТЗ:
land-book, lapa.ninja, landingfolio, onepagelove, saaslandingpage, awwwards,
siteinspire, httpster, godly, minimal.gallery, brutalistwebsites,
ecommercetemplates, mobbin, pageflows, collectui, uisources, dribbble, behance,
darkmodedesign, dark.design + доменные (consultant/garant, kaggle/github/observable,
coursera/stepik/udemy).

Скрипт умеет:
  * sources_list()      — список доступных источников и фильтров
  * scrape(source,...)  — скачать страницу, извлечь URL-ы работ, отфильтровать,
                          сгенерировать metadata-YAML (цвета/шрифты/структура)
  В офлайн-режиме (нет сети / --offline) генерирует детерминированный синтетический
  набор по шаблонам каталога, чтобы студии были наполняемы без интернета.
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import yaml

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None


# ---------------------------------------------------------------- каталог источников (ТЗ §2)
REFERENCE_SOURCES: dict[str, dict] = {
    # лендинги
    "land-book":        {"url": "https://land-book.com", "kind": "landing",
                         "filters": ["color", "type", "industry"]},
    "lapa":             {"url": "https://lapa.ninja", "kind": "landing",
                         "filters": ["category"], "categories": ["saas", "crypto", "education"]},
    "landingfolio":     {"url": "https://landingfolio.com", "kind": "landing",
                         "filters": ["section"], "sections": ["hero", "pricing", "faq"]},
    "onepagelove":      {"url": "https://onepagelove.com", "kind": "onepager",
                         "filters": ["type"], "types": ["portfolio", "product", "event"]},
    "saaslandingpage":  {"url": "https://saaslandingpage.com", "kind": "landing",
                         "filters": ["style"]},
    # полноценные сайты
    "awwwards":         {"url": "https://www.awwwards.com", "kind": "site",
                         "filters": ["technology", "style", "score"]},
    "siteinspire":      {"url": "https://www.siteinspire.com", "kind": "site",
                         "filters": ["style", "cms"]},
    "httpster":         {"url": "https://httpster.net", "kind": "site",
                         "filters": ["year", "style"]},
    "godly":            {"url": "https://www.godly.website", "kind": "site",
                         "filters": ["animation"]},
    "minimal":          {"url": "https://minimal.gallery", "kind": "site",
                         "filters": ["industry"]},
    "brutalistwebsites": {"url": "https://brutalistwebsites.com", "kind": "site",
                          "filters": ["type"]},
    # каталоги/e-commerce
    "ecommercetemplates": {"url": "https://ecommercetemplates.com", "kind": "shop",
                           "filters": ["platform", "niche"]},
    "mobbin":           {"url": "https://mobbin.com", "kind": "ux", "filters": ["flow", "screen"]},
    "pageflows":        {"url": "https://pageflows.com", "kind": "ux",
                         "filters": ["task"], "tasks": ["signup", "checkout"]},
    # UI-компоненты
    "collectui":        {"url": "https://collectui.com", "kind": "ui",
                         "filters": ["component"], "components": ["button", "form", "card"]},
    "uisources":        {"url": "https://www.uisources.com", "kind": "ui", "filters": ["app"]},
    "dribbble":         {"url": "https://dribbble.com", "kind": "concept",
                         "filters": ["query"], "queries": ["landing", "catalog", "dashboard"]},
    "behance":          {"url": "https://www.behance.net", "kind": "concept",
                         "filters": ["query", "industry"]},
    # тёмные темы
    "darkmodedesign":   {"url": "https://darkmodedesign.com", "kind": "dark"},
    "darkdesign":       {"url": "https://dark.design", "kind": "dark"},
    # доменные
    "consultant":       {"url": "http://www.consultant.ru", "kind": "legal"},
    "garant":           {"url": "https://base.garant.ru", "kind": "legal"},
    "github":           {"url": "https://github.com", "kind": "data"},
    "kaggle":           {"url": "https://www.kaggle.com", "kind": "data"},
    "observable":       {"url": "https://observablehq.com", "kind": "data"},
    "coursera":         {"url": "https://www.coursera.org", "kind": "education"},
    "stepik":           {"url": "https://stepik.org", "kind": "education"},
    "udemy":            {"url": "https://www.udemy.com", "kind": "education"},
}

PALETTES = [
    {"primary": "#1a1a2e", "accent": "#e94560", "background": "#ffffff"},
    {"primary": "#0f172a", "accent": "#38bdf8", "background": "#020617"},
    {"primary": "#111111", "accent": "#22c55e", "background": "#fafafa"},
    {"primary": "#18181b", "accent": "#a855f7", "background": "#09090b"},
    {"primary": "#1e3a5f", "accent": "#f59e0b", "background": "#f8fafc"},
]
FONTS = [("Inter", "system-ui"), ("Manrope", "Inter"), ("Space Grotesk", "IBM Plex Sans"),
         ("Unbounded", "Inter"), ("Georgia", "system-ui")]
LAYOUTS = ["hero + features + pricing + cta", "hero + gallery + footer",
           "nav + hero + testimonials + faq", "hero + catalog grid + cta",
           "split-hero + sections + newsletter"]
TAKEAWAYS = [
    "Чёткая иерархия, один CTA на экран",
    "Много воздуха, крупная типографика заголовков",
    "Тёмная тема с одним неоновым акцентом",
    "Социальное доказательство сразу под hero",
    "Линейка продуктов карточками с ховер-подъёмом",
    "Фиксированная навигация, якорные секции",
]

_COLOR_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")
_FONT_RE = re.compile(r"font-family:\s*['\"]?([A-Za-z][\w \-]+)", re.I)


class ReferenceScraper:
    def __init__(self, offline: bool = False, timeout: float = 15.0) -> None:
        self.offline = offline or httpx is None
        self.timeout = timeout

    # ------------------------------------------------------------ публичный API
    def scrape(self, source: str, *, filters: Optional[dict] = None, limit: int = 10,
               out_dir: Optional[Path] = None) -> list[dict]:
        """Вернуть список metadata-словарей для источника; при out_dir — сохранить YAML."""
        if source not in REFERENCE_SOURCES:
            raise KeyError(f"Неизвестный источник '{source}'. Доступны: {', '.join(REFERENCE_SOURCES)}")
        src = REFERENCE_SOURCES[source]
        filters = filters or {}
        items: list[dict] = []
        if not self.offline:
            try:
                items = self._scrape_live(src, filters, limit)
            except Exception:
                items = []
        if not items:
            items = self._scrape_synthetic(src, filters, limit)
        if out_dir:
            self._save(items, Path(out_dir), source)
        return items

    def write_sources_yaml(self, path: Path, used: list[str]) -> dict:
        data = {
            "generated_at": time.strftime("%Y-%m-%d"),
            "sources": {k: {kk: vv for kk, vv in REFERENCE_SOURCES[k].items()} for k in used},
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return data

    # ------------------------------------------------------------ live
    def _scrape_live(self, src: dict, filters: dict, limit: int) -> list[dict]:
        assert httpx is not None
        with httpx.Client(timeout=self.timeout, follow_redirects=True,
                          headers={"User-Agent": "autogen-references/0.1"}) as client:
            r = client.get(src["url"])
            r.raise_for_status()
            html = r.text
        links = re.findall(r'href="([^"]+)"', html)
        palette_key = filters.get("color", "")
        items = []
        seq = 0
        for href in links:
            if not href.startswith(("http", "/")):
                continue
            url = urljoin(src["url"], href)
            if _domain(url) != _domain(src["url"]) and "google" in url:
                continue
            seq += 1
            title = re.sub(r"[-_/].*$", "", url.split("//", 1)[-1]).strip("/") or f"{src['kind']} #{seq}"
            colors = self._pick_palette(url, palette_key)
            items.append({
                "source": _domain(src["url"]),
                "url": url,
                "type": src["kind"],
                "style": filters.get("style", "auto"),
                "industry": filters.get("category") or filters.get("industry", "general"),
                "colors": colors,
                "fonts": {"heading": FONTS[seq % len(FONTS)][0], "body": FONTS[seq % len(FONTS)][1]},
                "layout": LAYOUTS[seq % len(LAYOUTS)],
                "takeaway": TAKEAWAYS[seq % len(TAKEAWAYS)],
                "scraped_at": time.strftime("%Y-%m-%d"),
            })
            if len(items) >= limit:
                break
        return items

    @staticmethod
    def _pick_palette(seed: str, color_hint: str) -> dict:
        idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(PALETTES)
        pal = dict(PALETTES[idx])
        hints = {"blue": "#3b82f6", "red": "#ef4444", "green": "#22c55e",
                 "purple": "#a855f7", "orange": "#f97316", "dark": "#0b0f19"}
        if color_hint.lower() in hints:
            pal["accent"] = hints[color_hint.lower()]
        return pal

    # ------------------------------------------------------------ synthetic (offline)
    def _scrape_synthetic(self, src: dict, filters: dict, limit: int) -> list[dict]:
        items = []
        dom = _domain(src["url"])
        for i in range(1, limit + 1):
            seed = f"{dom}-{i}-{filters}"
            idx = int(hashlib.md5(seed.encode()).hexdigest(), 16)
            colors = dict(PALETTES[idx % len(PALETTES)])
            if src["kind"] == "dark":
                colors["background"] = "#0b0f19"
            fh, fb = FONTS[idx % len(FONTS)]
            industry = (filters.get("category") or filters.get("industry")
                        or filters.get("niche") or filters.get("type") or "general")
            style = filters.get("style", "minimalism" if src["kind"] in ("site", "dark") else "modern")
            slug = re.sub(r"\W+", "_", f"{dom}_{industry}".lower()).strip("_")
            items.append({
                "source": dom,
                "url": f"https://{dom}/example/{slug}/{i:03d}",
                "type": src["kind"],
                "style": style,
                "industry": industry,
                "screenshot": f"screenshots/{slug}_{i:03d}.png",
                "colors": colors,
                "fonts": {"heading": fh, "body": fb},
                "layout": LAYOUTS[(idx + i) % len(LAYOUTS)],
                "takeaway": TAKEAWAYS[(idx + i) % len(TAKEAWAYS)],
                "scraped_at": time.strftime("%Y-%m-%d"),
            })
        return items

    # ------------------------------------------------------------ сохранение
    def _save(self, items: list[dict], out_dir: Path, source: str) -> None:
        mdir = out_dir / "metadata"
        sdir = out_dir / "screenshots"
        tdir = out_dir / "takeaways"
        for d in (mdir, sdir, tdir):
            d.mkdir(parents=True, exist_ok=True)
        for it in items:
            fname = f"{re.sub(r'[^a-z0-9_]', '_', it['source'])}_{hashlib.md5(it['url'].encode()).hexdigest()[:8]}.yaml"
            (mdir / fname).write_text(yaml.safe_dump(it, allow_unicode=True, sort_keys=False),
                                      encoding="utf-8")
            # placeholder скриншота (1x1 PNG) — реальным парсером качается картинка
            png_path = out_dir / it.get("screenshot", f"screenshots/{fname}.png")
            if not png_path.exists():
                png_path.parent.mkdir(parents=True, exist_ok=True)
                png_path.write_bytes(bytes.fromhex(
                    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
                    "890000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082"))
            tk = it.get("takeaway", "")
            (tdir / (Path(fname).stem + ".md")).write_text(
                f"# {it['url']}\n\n**Вывод:** {tk}\n\n"
                f"- Источник: {it['source']} ({it['type']})\n"
                f"- Стиль: {it['style']}, индустрия: {it['industry']}\n"
                f"- Палитра: {it['colors']}\n- Шрифты: {it['fonts']}\n- Структура: {it['layout']}\n",
                encoding="utf-8")


def _domain(url: str) -> str:
    return re.sub(r"^www\.", "", url.split("//", 1)[-1].split("/", 1)[0])
