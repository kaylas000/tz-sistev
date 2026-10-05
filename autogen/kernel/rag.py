"""Knowledge Base (RAG) — поиск по референсам студии (ТЗ §3, §8).

Бэкенды:
  * qdrant   — продакшен-векторная БД (если доступен SDK + сервер)
  * builtin  — офлайн TF-IDF-индекс поверх references/metadata/*.yaml
"""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Optional

import yaml


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\-а-яё#]+", text.lower())


class BuiltinVectorStore:
    """Мини-RAG: TF-IDF + косинусное сходство. Без внешних зависимостей."""

    def __init__(self) -> None:
        self.docs: list[dict] = []       # {id, text, meta}
        self._df: Counter = Counter()
        self._tf: list[Counter] = []

    def add(self, doc_id: str, text: str, meta: dict) -> None:
        toks = _tokenize(text)
        tf = Counter(toks)
        for t in set(toks):
            self._df[t] += 1
        self._tf.append(tf)
        self.docs.append({"id": doc_id, "text": text, "meta": meta})

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        q = Counter(_tokenize(query))
        n = max(1, len(self.docs))
        scores = []
        for i, tf in enumerate(self._tf):
            s = 0.0
            for t, qn in q.items():
                if tf[t]:
                    idf = math.log(1 + n / (1 + self._df.get(t, 0)))
                    s += (1 + math.log(tf[t])) * qn * idf
            norm = math.sqrt(sum(v * v for v in tf.values())) or 1.0
            scores.append((s / norm, i))
        scores.sort(reverse=True)
        out = []
        for sc, i in scores[:top_k]:
            if sc <= 0:
                continue
            d = self.docs[i]
            out.append({"id": d["id"], "score": round(sc, 4), "text": d["text"][:400], "meta": d["meta"]})
        return out


class KnowledgeBase:
    def __init__(self, backend: str = "builtin", studio=None, qdrant_url: Optional[str] = None) -> None:
        self.backend = backend
        self.store = BuiltinVectorStore()
        if backend == "qdrant":
            try:
                from qdrant_client import QdrantClient  # type: ignore
                self._qdrant = QdrantClient(url=qdrant_url)
            except Exception as exc:
                raise RuntimeError(f"Qdrant недоступен ({exc}); используйте backend='builtin'") from exc
        else:
            self._qdrant = None
        if studio is not None:
            self.index_studio(studio)

    def index_studio(self, studio) -> int:
        """Загрузить все references/metadata/*.yaml студии в индекс."""
        mdir = Path(studio.path) / "references" / "metadata"
        count = 0
        if not mdir.is_dir():
            return 0
        for f in sorted(mdir.glob("*.y*ml")):
            try:
                meta = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            text = " ".join(str(v) for v in meta.values())
            takeaway = meta.get("takeaway") or ""
            self.store.add(doc_id=f.stem, text=f"{meta.get('source','')} {meta.get('style','')} "
                                          f"{meta.get('industry','')} {meta.get('layout','')} {takeaway}",
                           meta=meta)
            count += 1
        return count

    def query(self, text: str, top_k: int = 5) -> list[dict]:
        return self.store.search(text, top_k)
