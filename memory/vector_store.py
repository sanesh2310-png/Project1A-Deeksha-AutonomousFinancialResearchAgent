"""
Long-term (semantic) memory -- Section A3.2 / A3.3 of the project brief.

This implements the vector-database record schema from Section A3.3
(id, content, embedding, ticker, source_type, date, confidence,
researcher_session, verified) using a lightweight, dependency-free
hashing-trick embedding function rather than a hosted embedding API
(no external network access is available in this environment; swap
`_embed()` for a real OpenAI/Cohere embedding call in production --
the rest of the store is embedding-provider-agnostic).

Hashing-trick embeddings are a real, if simplified, embedding technique:
each token is hashed into one of N buckets, and the resulting vector is
L2-normalized. This gives sane cosine-similarity behavior for keyword and
topic overlap, which is sufficient for the deterministic test suite and
demo challenges in this project, while keeping the store swappable.
"""
import json
import math
import os
import re
import time
import uuid
from dataclasses import dataclass, field, asdict

from config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _embed(text: str, dim: int = settings.EMBEDDING_DIM) -> list[float]:
    vec = [0.0] * dim
    for tok in _tokenize(text):
        idx = hash(tok) % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class MemoryRecord:
    id: str
    content: str
    ticker: str
    source_type: str
    date: str
    confidence: float
    researcher_session: str
    verified: bool = False
    embedding: list[float] = field(default_factory=list)


class VectorStore:
    def __init__(self, path: str = settings.VECTOR_STORE_PATH):
        self.path = path
        self._records: dict[str, MemoryRecord] = {}
        self._load()

    # -- persistence ------------------------------------------------------
    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                raw = json.load(f)
            for r in raw:
                self._records[r["id"]] = MemoryRecord(**r)

    def _save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump([asdict(r) for r in self._records.values()], f, indent=2)

    # -- write --------------------------------------------------------------
    def store(self, content: str, metadata: dict) -> dict:
        rec_id = metadata.get("id") or str(uuid.uuid4())[:12]
        rec = MemoryRecord(
            id=rec_id,
            content=content,
            ticker=metadata.get("ticker", ""),
            source_type=metadata.get("source_type", "analysis"),
            date=metadata.get("date", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
            confidence=float(metadata.get("confidence", 0.8)),
            researcher_session=metadata.get("researcher_session", "session-unknown"),
            verified=bool(metadata.get("verified", False)),
            embedding=_embed(content),
        )
        self._records[rec_id] = rec
        self._save()
        return {"stored": True, "document_id": rec_id}

    # -- read ----------------------------------------------------------------
    def search(self, query: str, top_k: int = 5, filter: dict | None = None) -> dict:
        q_vec = _embed(query)
        candidates = list(self._records.values())
        if filter:
            for key, val in filter.items():
                candidates = [r for r in candidates if getattr(r, key, None) == val]
        scored = [(r, _cosine(q_vec, r.embedding)) for r in candidates]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        top = scored[:top_k]
        return {
            "query": query,
            "hits": [
                {
                    "id": r.id, "content": r.content, "ticker": r.ticker,
                    "source_type": r.source_type, "date": r.date,
                    "confidence": r.confidence, "similarity": round(score, 4),
                }
                for r, score in top if score > 0
            ],
        }

    def count(self) -> int:
        return len(self._records)
