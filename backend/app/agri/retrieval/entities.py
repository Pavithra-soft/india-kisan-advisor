from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "synonyms.json"


@lru_cache
def _synonyms() -> dict[str, dict[str, str]]:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_entity(kind: str, text: str) -> str | None:
    text_n = text.strip().lower()
    table = _synonyms().get(kind, {})
    return table.get(text_n)


def resolve_crop_from_question(question: str) -> str | None:
    q = question.lower()
    for alias, cid in _synonyms().get("crops", {}).items():
        if alias in q:
            return cid
    return None
