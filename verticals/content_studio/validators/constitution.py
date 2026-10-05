"""Content Studio: вода/штампы, объём, SEO-структура (К-xx -> V-xx)."""
import re
from autogen.kernel.errors import ErrorItem

CLICHES = ["в современном мире", "не секрет что", "стоит отметить что"]


def validate(studio, brief, artifact):
    errors = []
    def err(code, sev, rule, desc, sugg):
        errors.append(ErrorItem(code=code, severity=sev, rule_id=rule, description=desc, suggestion=sugg))
    low = artifact.lower()
    for i, c in enumerate(CLICHES):
        if c in low:
            err("B-0%d" % (i + 10), "minor", "К-04", f"Штамп/вода: «{c}»", "Переписать конкретикой")
    h2 = len(re.findall(r"^##\s+\S", artifact, re.M))
    if h2 < 2 and len(artifact) > 500:
        err("V-03", "minor", "К-03", f"H2-разделов: {h2} (нужно ≥2)", "Разбейте текст на секции ##")
    return errors
