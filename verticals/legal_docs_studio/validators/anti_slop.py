"""Переиспользует generic anti-slop ядра поверх студийных BANNED/QUOTAS."""
from autogen.kernel.validators import validate_anti_slop

def validate(studio, brief, artifact):
    return validate_anti_slop(studio.path, artifact)
