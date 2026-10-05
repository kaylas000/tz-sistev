"""Студийный валидатор Конституции Web Studio (К-01..К-24 -> V-01..V-24).

Проверяет правила, которые удобно кодировать на Python: доctype, lang, title/description,
viewport, секции hero/features/cta, alt у img, один H1, отсутствие console.log.
Остальные правила покрываются generic check_regex из CONSTITUTION.md.
"""
from __future__ import annotations

import re

from autogen.kernel.errors import ErrorItem


def _err(code, sev, rule, desc, sugg):
    return ErrorItem(code=code, severity=sev, rule_id=rule, description=desc, suggestion=sugg)


def validate(studio, brief: dict, artifact: str) -> list[ErrorItem]:
    html = artifact.lower()
    errors: list[ErrorItem] = []

    # К-01: полный HTML5-документ
    if "<!doctype html" not in html or "<html" not in html or "<body" not in html:
        errors.append(_err("V-01", "critical", "К-01",
                          "Артефакт не является полным HTML5-документом (doctype/html/body)",
                          "Оберните содержимое в <!DOCTYPE html><html lang=\"ru\"><head>...</head><body>...</body></html>"))

    # К-03: обязательные секции
    for sec, name in (("hero", "герой"), ("feature", "преимущества"), ("cta", "финальный CTA")):
        if sec not in html and f"id=\"{sec}" not in html:
            if sec == "hero" and ("<h1" not in html):
                errors.append(_err("V-03", "major", "К-03", f"Нет секции {name} ({sec})",
                                  f"Добавьте секцию <section class=\"{sec}\">..."))
            elif sec != "hero":
                errors.append(_err("V-03", "major", "К-03", f"Нет секции {name} ({sec})",
                                  f"Добавьте блок '{sec}' в структуру страницы"))

    # К-05: alt у изображений
    bad_imgs = re.findall(r"<img(?![^>]*alt=\"[^\"]+\")[^>]*>", artifact, re.I)
    if bad_imgs:
        errors.append(_err("V-05", "major", "К-05",
                          f"{len(bad_imgs)} изображений без непустого alt",
                          "Добавьте alt=\"описание\" каждому <img>"))

    # К-06: title + meta description
    if "<title>" not in html and "title>" not in html:
        errors.append(_err("V-06", "major", "К-06", "В <head> нет <title>", "Добавьте <title>...</title>"))
    if 'name="description"' not in html and "name='description'" not in html:
        errors.append(_err("V-06", "minor", "К-06", "Нет meta description",
                          'Добавьте <meta name="description" content="...">'))

    # К-08: viewport
    if "viewport" not in html:
        errors.append(_err("V-08", "critical", "К-08", "Нет viewport meta — страница не адаптивна",
                          'Добавьте <meta name="viewport" content="width=device-width, initial-scale=1">'))

    # К-17: ровно один H1
    h1s = len(re.findall(r"<h1[\s>]", artifact, re.I))
    if h1s > 1:
        errors.append(_err("V-17", "major", "К-17", f"Насчитано {h1s} заголовков H1 (нужен 1)",
                          "Оставьте единственный H1, остальные понизьте до H2"))
    if h1s == 0 and "<body" in html:
        errors.append(_err("V-17", "major", "К-17", "Отсутствует H1", "Добавьте единственный <h1> с названием продукта"))

    # К-19: debug-код
    if re.search(r"console\.log\(|debugger\b", artifact):
        errors.append(_err("V-19", "major", "К-19", "В JS остался debug-код (console.log/debugger)",
                          "Удалите отладочные вызовы из финального артефакта"))

    return errors
