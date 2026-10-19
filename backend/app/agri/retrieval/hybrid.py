from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from app.agri.retrieval.store import FactRecord

_TOKEN = re.compile(r"[\w\u0900-\u097F\u0C00-\u0C7F]+", re.UNICODE)


@dataclass
class ScoredRecord:
    record: FactRecord
    score: float
    bm25: float
    dense: float


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


def bm25_score(query_tokens: list[str], doc_tokens: list[str], avg_dl: float, k1: float = 1.5, b: float = 0.75) -> float:
    if not query_tokens:
        return 0.0
    dl = len(doc_tokens)
    tf = Counter(doc_tokens)
    score = 0.0
    for qt in query_tokens:
        f = tf.get(qt, 0)
        if f == 0:
            continue
        idf = math.log(1 + 1)  # single-doc corpus per record in hybrid pass
        denom = f + k1 * (1 - b + b * dl / max(avg_dl, 1))
        score += idf * (f * (k1 + 1)) / denom
    return score


def char_ngrams(text: str, n: int = 3) -> Counter[str]:
    text = text.lower()
    if len(text) < n:
        return Counter({text: 1})
    return Counter(text[i : i + n] for i in range(len(text) - n + 1))


def cosine_counter(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a[k] * b.get(k, 0) for k in a)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def hybrid_retrieve(
    query: str,
    records: list[FactRecord],
    *,
    top_k: int = 5,
) -> list[ScoredRecord]:
    q_tokens = tokenize(query)
    q_ngrams = char_ngrams(query)
    docs = [(r, tokenize(r.title + " " + r.body)) for r in records]
    avg_dl = sum(len(d) for _, d in docs) / max(len(docs), 1)

    scored: list[ScoredRecord] = []
    for rec, dtoks in docs:
        bm = bm25_score(q_tokens, dtoks, avg_dl)
        dense = cosine_counter(q_ngrams, char_ngrams(rec.title + " " + rec.body))
        overlap_bonus = len(set(q_tokens) & set(dtoks)) * 0.08
        # Cross-encoder placeholder: emphasize metadata agreement via bm25
        combined = 0.5 * bm + 0.35 * dense + overlap_bonus
        scored.append(ScoredRecord(record=rec, score=combined, bm25=bm, dense=dense))

    scored.sort(key=lambda s: s.score, reverse=True)
    return scored[:top_k]
