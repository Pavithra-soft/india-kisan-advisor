from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from app.agri.sync.quarantine import QuarantineEntry, QuarantineStore
from app.agri.sync.validators import validate_price_record
from app.agri.sync.versioning import publish_version

HIGH_RISK_TYPES = {"fertilizer", "pesticide", "eligibility_interpretation"}


@dataclass
class SyncReport:
    started_at: str
    finished_at: str = ""
    new_count: int = 0
    changed_count: int = 0
    rejected_count: int = 0
    quarantined_count: int = 0
    published_version: str | None = None
    review_queue: list[dict] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


def run_daily_sync(
    *,
    data_dir: Path,
    adapters: list[Callable[[], list[dict[str, Any]]]] | None = None,
) -> SyncReport:
    started = datetime.now(timezone.utc).isoformat()
    report = SyncReport(started_at=started)
    quarantine = QuarantineStore(data_dir / "quarantine.json")
    existing_path = data_dir / "published_facts.json"
    existing: list[dict] = []
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))

    incoming: list[dict] = []
    for adapter in adapters or []:
        try:
            incoming.extend(adapter())
        except Exception as e:
            report.messages.append(f"adapter failed: {e}")

    by_id = {r["record_id"]: r for r in existing}
    merged = dict(by_id)
    for row in incoming:
        rid = row.get("record_id")
        if not rid:
            report.rejected_count += 1
            continue
        risk = row.get("risk_class", "low")
        if row.get("fact_type") in HIGH_RISK_TYPES or risk == "high":
            report.review_queue.append(row)
            report.messages.append(f"queued for review: {rid}")
            continue
        issues = validate_price_record(row) if row.get("fact_type") == "price" else []
        if issues:
            report.quarantined_count += 1
            quarantine.add(QuarantineEntry(source=row.get("source_name", "unknown"), reason=";".join(i.message for i in issues), payload=row))
            continue
        if rid not in by_id:
            report.new_count += 1
        elif by_id[rid] != row:
            report.changed_count += 1
        merged[rid] = row

    published = list(merged.values())
    version = publish_version(published, data_dir / "datasets", changelog="daily sync")
    existing_path.write_text(json.dumps(published, indent=2), encoding="utf-8")
    report.published_version = version.version_id
    report.finished_at = datetime.now(timezone.utc).isoformat()
    return report
