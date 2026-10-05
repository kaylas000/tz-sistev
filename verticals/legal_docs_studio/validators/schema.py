"""Проверка формата артефакта (markdown)."""
import re
from autogen.kernel.errors import ErrorItem

def validate(studio, brief, artifact):
    errors = []
    kind = "markdown"
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
                                    description=f"SyntaxError: {e.msg} (строка {e.lineno})",
                                    suggestion="Исправить синтаксис Python"))
    elif kind == "markdown":
        if not re.search(r"^#\s+\S", artifact, re.M):
            errors.append(ErrorItem(code="A-03", severity="minor", rule_id="schema",
                                    description="Нет заголовка верхнего уровня",
                                    suggestion="Добавить '# Название'"))
    return errors
