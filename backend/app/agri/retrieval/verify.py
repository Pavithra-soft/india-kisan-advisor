from __future__ import annotations

import re
from dataclasses import dataclass

from app.agri.retrieval.store import FactRecord

_NUM = re.compile(r"\d+(?:\.\d+)?")


@dataclass
class VerificationResult:
    ok: bool
    unsupported_sentences: list[str]
    numeric_mismatches: list[str]


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[\w\u0900-\u097F\u0C00-\u0C7F]+", text, re.UNICODE) if len(t) > 2}


def verify_claim_support(sentences: list[str], records: list[FactRecord], min_overlap: float = 0.12) -> VerificationResult:
    corpus = " ".join(r.title + " " + r.body for r in records)
    corpus_t = _tokens(corpus)
    unsupported: list[str] = []
    for sent in sentences:
        st = _tokens(sent)
        if not st:
            continue
        overlap = len(st & corpus_t) / len(st)
        if overlap < min_overlap:
            unsupported.append(sent)
    return VerificationResult(ok=not unsupported, unsupported_sentences=unsupported, numeric_mismatches=[])


def verify_numeric_exact_match(sentences: list[str], records: list[FactRecord]) -> VerificationResult:
    allowed: set[str] = set()
    for r in records:
        allowed.update(r.numbers.values())
        allowed.update(_NUM.findall(r.body))

    mismatches: list[str] = []
    for sent in sentences:
        for num in _NUM.findall(sent):
            if num not in allowed:
                mismatches.append(f"{num} in '{sent}'")
    return VerificationResult(ok=not mismatches, unsupported_sentences=[], numeric_mismatches=mismatches)


def verify_answer(sentences: list[str], records: list[FactRecord]) -> VerificationResult:
    a = verify_claim_support(sentences, records)
    b = verify_numeric_exact_match(sentences, records)
    return VerificationResult(
        ok=a.ok and b.ok,
        unsupported_sentences=a.unsupported_sentences,
        numeric_mismatches=b.numeric_mismatches,
    )
