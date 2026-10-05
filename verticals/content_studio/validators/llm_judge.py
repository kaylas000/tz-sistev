"""LLM-критик делегирует generic-реализацию ядра."""
from autogen.kernel.validators import llm_judge

def validate(studio, llm, brief, artifact):
    if llm is None:
        return []
    return llm_judge(llm, studio, brief, artifact)
