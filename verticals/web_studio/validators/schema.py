"""Схема HTML-артефакта Web Studio: корректность структуры на парсер из stdlib."""
from html.parser import HTMLParser

from autogen.kernel.errors import ErrorItem


class _Balance(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack: list[str] = []
        self.mismatch: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.mismatch.append(self.stack.pop())
            if self.stack:
                self.stack.pop()
        else:
            self.mismatch.append(f"stray </{tag}>")


def validate(studio, brief, artifact):
    errors = []
    low = artifact.lower()
    if "<html" not in low or "</html>" not in low:
        errors.append(ErrorItem(code="A-03", severity="major", rule_id="schema",
                                description="HTML неполный: нет <html>/</html>",
                                suggestion="Выдать полный документ с <!DOCTYPE html>"))
        return errors
    p = _Balance()
    try:
        p.feed(artifact)
    except Exception as exc:
        errors.append(ErrorItem(code="A-03", severity="major", rule_id="schema",
                                description=f"HTML не парсится: {exc}",
                                suggestion="Исправьте разметку"))
        return errors
    unclosed = [t for t in p.stack if t not in ("html",)]
    if unclosed or p.mismatch:
        errors.append(ErrorItem(code="A-03", severity="minor", rule_id="schema",
                                description=f"Незакрытые теги: {unclosed[:5]}, лишние: {p.mismatch[:5]}",
                                suggestion="Сбалансировать открывающие/закрывающие теги"))
    return errors
