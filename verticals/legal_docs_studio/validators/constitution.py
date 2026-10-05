"""Legal Docs Studio: проверка существенных условий, реквизитов, противоречий (К-xx -> V-xx)."""
import re
from autogen.kernel.errors import ErrorItem


def validate(studio, brief, artifact):
    errors = []
    def err(code, sev, rule, desc, sugg):
        errors.append(ErrorItem(code=code, severity=sev, rule_id=rule, description=desc, suggestion=sugg))
    if not artifact.strip():
        err("V-01", "critical", "К-01", "Документ пуст", "Сгенерировать договор заново")
        return errors
    if not re.search(r"предмет", artifact, re.I):
        err("V-02", "critical", "К-02", "Не найден раздел «Предмет» — существенное условие",
            "Добавьте раздел 1. Предмет с конкретными обязательствами")
    if "реквизиты" not in artifact.lower():
        err("V-03", "critical", "К-03", "Нет блока «Реквизиты сторон»", "Добавьте раздел Реквизиты сторон с ИНН/ОГРН")
    # К-06: противоречие бессрочности и конкретного срока
    if re.search(r"бессрочн", artifact, re.I) and re.search(r"\d{2}\.\d{2}\.\d{4}", artifact):
        err("V-06", "major", "К-06", "Противоречие: «бессрочно» вместе с конкретной датой",
            "Уберите одно из положений о сроке")
    # К-08: согласия на ПДн
    if re.search(r"(согласие|персональн)", artifact, re.I) and "152" not in artifact:
        err("V-08", "major", "К-08", "Документ про ПДн без ссылки на 152-ФЗ",
            "Добавьте ссылку на ФЗ-152 «О персональных данных»")
    return errors
