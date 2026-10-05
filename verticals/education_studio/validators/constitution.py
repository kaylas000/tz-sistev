"""Education Studio: цели по Блуму, вопросы теста, обратная связь (К-xx -> V-xx)."""
import re
from autogen.kernel.errors import ErrorItem

BLOOM = ["знать", "понимать", "применять", "анализиров", "оценив", "создат", "научитесь"]


def validate(studio, brief, artifact):
    errors = []
    def err(code, sev, rule, desc, sugg):
        errors.append(ErrorItem(code=code, severity=sev, rule_id=rule, description=desc, suggestion=sugg))
    low = artifact.lower()
    if not any(b in low for b in BLOOM):
        err("V-01", "major", "К-01", "Нет цели урока по таксономии Блума",
            "Добавьте «Научитесь …» с глаголом уровня Блума")
    questions = re.findall(r"\?\s*$|^\s*\d+[.)]\s+.*\?", artifact, re.M)
    is_quiz = "quiz" in str(brief).lower() or "тест" in low
    if is_quiz and len(questions) < 3:
        err("V-05", "major", "К-05", f"Вопросов теста: {len(questions)} (нужно ≥3)",
            "Добавьте минимум 3 вопроса с правильными ответами")
    return errors
