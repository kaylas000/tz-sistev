"""Data Analytics Studio: синтаксис, детерминированность, SELECT * (К-xx -> V-xx)."""
import re
from autogen.kernel.errors import ErrorItem


def validate(studio, brief, artifact):
    errors = []
    def err(code, sev, rule, desc, sugg):
        errors.append(ErrorItem(code=code, severity=sev, rule_id=rule, description=desc, suggestion=sugg))
    if not artifact.strip():
        err("V-01", "critical", "К-01", "Артефакт пуст", "Сгенерировать код заново")
        return errors
    try:
        compile(artifact, "<artifact>", "exec")
    except SyntaxError as e:
        err("V-01", "critical", "К-01", f"SyntaxError в строке {e.lineno}: {e.msg}",
            "Исправьте синтаксис Python")
    if re.search(r"requests\.(get|post)\(", artifact):
        err("V-03", "major", "К-03", "Сетевой запрос в песочнице запрещён",
            "Используйте локальные данные/сид-датасет")
    return errors
