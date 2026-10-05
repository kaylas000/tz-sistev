"""LLM-критик Web Studio: делегирование generic-реализации ядра (gemma2:9b, T=0.0)."""
from autogen.kernel.validators import llm_judge


def validate(studio, llm, brief, artifact):
    if llm is None:
        return []
    return llm_judge(llm, studio, brief, artifact)
