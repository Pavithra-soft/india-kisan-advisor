from __future__ import annotations

import json
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from app.agri.schemas import FactRecord, FactType

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache
def load_facts() -> list[FactRecord]:
    path = DATA_DIR / "facts_seed.json"
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    records: list[FactRecord] = []
    for row in raw:
        records.append(
            FactRecord(
                record_id=row["record_id"],
                fact_type=FactType(row["fact_type"]),
                title=row["title"],
                body=row["body"],
                crop_id=row.get("crop_id"),
                region_id=row.get("region_id"),
                season=row.get("season"),
                valid_from=date.fromisoformat(row["valid_from"]),
                valid_to=date.fromisoformat(row["valid_to"]) if row.get("valid_to") else None,
                source_name=row["source_name"],
                source_url=row["source_url"],
                numbers=row.get("numbers") or {},
                metadata=row.get("metadata") or {},
            )
        )
    return records


def filter_valid(
    records: Iterable[FactRecord],
    *,
    crop_id: str | None,
    region_id: str | None,
    season: str | None,
    as_of: date | None = None,
) -> list[FactRecord]:
    today = as_of or date.today()
    out: list[FactRecord] = []
    for r in records:
        if r.valid_from > today:
            continue
        if r.valid_to and r.valid_to < today:
            continue
        if crop_id and r.crop_id and r.crop_id != crop_id:
            continue
        if region_id and r.region_id and r.region_id not in (region_id, "in"):
            continue
        if season and r.season and r.season != season:
            continue
        out.append(r)
    return out


def last_updated(records: list[FactRecord]) -> datetime:
    if not records:
        return datetime.min
    return datetime.combine(max(r.valid_from for r in records), datetime.min.time())
