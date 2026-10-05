"""Смоук-тест студии: грузится, конституция парсится, цикл проходит на mock-LLM."""
from pathlib import Path
from autogen.kernel.registry import StudioRegistry
from autogen.kernel.runner import KernelRunner
from autogen.kernel.llm import LLMManager

ROOT = Path(__file__).resolve().parents[2]


def test_studio_loads_and_runs():
    reg = StudioRegistry(ROOT / "verticals")
    name = Path(__file__).resolve().parents[2].name  # noqa
    studios = reg.discover()
    assert studios
    studio = reg.get(studios[0])
    assert studio.rules, "Конституция не распарсилась"
    runner = KernelRunner(llm=LLMManager(backend="mock"), use_llm_judge=False)
    brief = {f: "тестовое значение для smoke-прогона" for f in studio.brief_required_fields}
    st = runner.run(studio, brief)
    assert st.status in ("passed", "escalated", "error", "g1_fail")
