"""Observability: метрики, трейсы шагов, cost tracking (ТЗ §10.1, §12).

Прометеус-совместимый text-exposition отдаётся /metrics без зависимости от пакета.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Metrics:
    _counters: dict = field(default_factory=lambda: defaultdict(float))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, name: str, value: float = 1.0, **labels) -> None:
        key = _fmt(name, labels)
        with self._lock:
            self._counters[key] += value

    def set(self, name: str, value: float, **labels) -> None:
        key = _fmt(name, labels)
        with self._lock:
            self._counters[key] = value

    def snapshot(self) -> dict[str, float]:
        with self._lock:
            return dict(self._counters)

    def exposition(self) -> str:
        """Prometheus text format."""
        lines = []
        for key, val in sorted(self.snapshot().items()):
            lines.append(f"{key} {val}")
        return "\n".join(lines) + "\n"


def _fmt(name: str, labels: dict) -> str:
    if not labels:
        return name
    lbl = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return f"{name}{{{lbl}}}"


METRICS = Metrics()


def observe_run(studio: str, skill: str, status: str, cycles: int, tokens: int, cost_usd: float,
                duration_s: float) -> None:
    """Записать итоги run'а в метрики и cost tracking."""
    METRICS.inc("autogen_runs_total", studio=studio, skill=skill, status=status)
    METRICS.inc("autogen_run_cycles_sum", float(cycles), studio=studio)
    METRICS.inc("autogen_llm_tokens_total", float(tokens), studio=studio)
    METRICS.inc("autogen_cost_usd_total", cost_usd, studio=studio)
    METRICS.inc("autogen_run_duration_seconds_sum", duration_s, studio=studio)
    METRICS.set("autogen_last_run_cycles", float(cycles), studio=studio, skill=skill)


class TraceLogger:
    """JSONL-трейсер событий платформы (OpenTelemetry-совместимая схема полей)."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        self.events: list[dict] = []

    def event(self, kind: str, **fields) -> None:
        rec = {"ts": time.time(), "kind": kind, **fields}
        self.events.append(rec)
        if self.path:
            import json
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
