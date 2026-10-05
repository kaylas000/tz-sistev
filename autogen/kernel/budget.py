"""Budget Manager (ТЗ §10.3) — лимиты на run / день / токены в минуту.

Хранение: SQLite (переносимая БД бюджета из ТЗ §10.1).
Лимиты по умолчанию: $2 на run, $20 в день, 400 000 токенов/мин, 10 циклов.
"""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class BudgetExceeded(RuntimeError):
    """Превышение бюджетного лимита -> код R-02."""


@dataclass(slots=True)
class BudgetLimits:
    max_run_usd: float = 2.0
    max_day_usd: float = 20.0
    max_tokens_per_min: int = 400_000
    max_cycles: int = 10

    @classmethod
    def from_dict(cls, d: dict) -> "BudgetLimits":
        return cls(
            max_run_usd=float(d.get("max_run_usd", cls.max_run_usd)),
            max_day_usd=float(d.get("max_day_usd", cls.max_day_usd)),
            max_tokens_per_min=int(d.get("max_tokens_per_min", cls.max_tokens_per_min)),
            max_cycles=int(d.get("max_cycles", cls.max_cycles)),
        )


_SCHEMA = """
CREATE TABLE IF NOT EXISTS spend (
    ts REAL NOT NULL,
    run_id TEXT NOT NULL,
    tokens INTEGER NOT NULL,
    cost_usd REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_spend_ts ON spend(ts);
CREATE INDEX IF NOT EXISTS idx_spend_run ON spend(run_id);
"""


class BudgetManager:
    def __init__(self, db_path: str | Path = ":memory:", limits: Optional[BudgetLimits] = None) -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True) if self.db_path != ":memory:" else None
        self.limits = limits or BudgetLimits()
        self._conn = sqlite3.connect(self.db_path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        # счётчик циклов живёт в памяти процесса run'а
        self._cycles: dict[str, int] = {}

    # ------------------------------------------------------------- учёт
    def check_and_charge(self, *, est_prompt_tokens: int, est_completion_tokens: int,
                         price_per_1k: float, run_id: str = "default") -> None:
        """Проверить лимиты ДО запроса; бросить BudgetExceeded при нарушении."""
        est_cost = (est_prompt_tokens + est_completion_tokens) / 1000.0 * price_per_1k
        run_spent = self.run_spent(run_id)
        if run_spent + est_cost > self.limits.max_run_usd:
            raise BudgetExceeded(f"R-02: превышен лимит на run (${run_spent + est_cost:.4f} > ${self.limits.max_run_usd})")
        day_spent = self.day_spent()
        if day_spent + est_cost > self.limits.max_day_usd:
            raise BudgetExceeded(f"R-02: превышен дневной лимит (${day_spent + est_cost:.4f} > ${self.limits.max_day_usd})")
        if self.tokens_last_minute() + est_prompt_tokens + est_completion_tokens > self.limits.max_tokens_per_min:
            raise BudgetExceeded("R-02: превышен лимит токенов в минуту")

    def charge(self, run_id: str, tokens: int, cost_usd: float) -> None:
        self._conn.execute("INSERT INTO spend VALUES (?,?,?,?)",
                           (time.time(), run_id, tokens, cost_usd))
        self._conn.commit()

    # ------------------------------------------------------------- вопросы
    def run_spent(self, run_id: str) -> float:
        row = self._conn.execute("SELECT COALESCE(SUM(cost_usd),0) FROM spend WHERE run_id=?",
                                 (run_id,)).fetchone()
        return float(row[0])

    def day_spent(self) -> float:
        since = time.time() - 86400
        row = self._conn.execute("SELECT COALESCE(SUM(cost_usd),0) FROM spend WHERE ts>=?",
                                 (since,)).fetchone()
        return float(row[0])

    def tokens_last_minute(self) -> int:
        since = time.time() - 60
        row = self._conn.execute("SELECT COALESCE(SUM(tokens),0) FROM spend WHERE ts>=?",
                                 (since,)).fetchone()
        return int(row[0])

    # ------------------------------------------------------------- циклы
    def register_cycle(self, run_id: str) -> int:
        """Вернуть номер цикла; CycleLimitExceeded после max_cycles."""
        n = self._cycles.get(run_id, 0) + 1
        self._cycles[run_id] = n
        if n > self.limits.max_cycles:
            raise BudgetExceeded(f"R-01: превышен лимит циклов ({n} > {self.limits.max_cycles})")
        return n

    def cycles(self, run_id: str) -> int:
        return self._cycles.get(run_id, 0)

    def summary(self, run_id: str) -> dict:
        return {
            "run_id": run_id,
            "run_spent_usd": round(self.run_spent(run_id), 6),
            "day_spent_usd": round(self.day_spent(), 6),
            "tokens_last_minute": self.tokens_last_minute(),
            "cycles": self.cycles(run_id),
            "limits": vars(self.limits),
        }

    def close(self) -> None:
        self._conn.close()
