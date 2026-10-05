"""Anti-slop Web Studio: запреты B-xx и квоты Q-xx из anti-slop/*.md (generic-движок ядра)."""
from autogen.kernel.validators import validate_anti_slop


def validate(studio, brief, artifact):
    return validate_anti_slop(studio.path, artifact)
