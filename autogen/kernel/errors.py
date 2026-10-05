"""Единый словарь кодов ошибок платформы (ТЗ §6).

Префиксы:
  V-xx — нарушение правила Конституции (V-01 => К-01)
  B-xx — запрещённый anti-slop паттерн
  Q-xx — превышение anti-slop квоты
  E-xx — проблема со входными данными (бриф)
  A-xx — проблема артефакта
  R-xx — отклонение/лимиты цикла
  L-xx — ошибка выполнения цикла
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

SEVERITIES = ("critical", "major", "minor")


@dataclass(slots=True)
class ErrorItem:
    """Одна структурированная ошибка для фидбека агенту."""
    code: str
    severity: str
    description: str
    suggestion: str = ""
    rule_id: Optional[str] = None  # например К-03 / B-07 / Q-02

    def to_dict(self) -> dict:
        d = asdict(self)
        if d["rule_id"] is None:
            del d["rule_id"]
        return d


# ---------------------------------------------------------------- стандартные коды
ERROR_CATALOG: dict[str, str] = {
    # Входные данные
    "E-01": "Неполный бриф: не хватает обязательных полей",
    "E-02": "Бриф не соответствует схеме студийного BRIEF-TEMPLATE",
    "E-03": "Неизвестный скилл запрошен в брифе",
    # Артефакт
    "A-01": "Артефакт не прошёл валидацию",
    "A-02": "Артефакт отсутствует или пуст",
    "A-03": "Артефакт не проходит JSON Schema",
    # Лимиты и циклы
    "R-01": "Превышен лимит циклов генерация-валидация",
    "R-02": "Превышен бюджет run/day/token-rate",
    "L-01": "Ошибка выполнения цикла (исключение агента/песочницы)",
}


def constitution_error_code(rule_id: str) -> str:
    """К-03 -> V-03. Правило Конституции порождает код категории V."""
    num = "".join(ch for ch in rule_id if ch.isdigit())
    return f"V-{int(num):02d}" if num else "V-00"


def make_feedback(errors: list[ErrorItem]) -> dict:
    """Сформировать структурированный JSON-фидбек (ТЗ §6)."""
    return {
        "passed": not any(e.severity in ("critical", "major") for e in errors),
        "errors": [e.to_dict() for e in errors],
    }
