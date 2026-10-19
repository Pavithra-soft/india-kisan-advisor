from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DatasetVersion:
    version_id: str
    created_at: str
    changelog: str
    record_count: int
    content_hash: str


def publish_version(records: list[dict], datasets_dir: Path, changelog: str) -> DatasetVersion:
    datasets_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(records, sort_keys=True)
    content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    version_id = f"v-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{content_hash}"
    out = datasets_dir / f"{version_id}.json"
    out.write_text(payload, encoding="utf-8")
    meta = DatasetVersion(
        version_id=version_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        changelog=changelog,
        record_count=len(records),
        content_hash=content_hash,
    )
    (datasets_dir / "latest.json").write_text(json.dumps(meta.__dict__, indent=2), encoding="utf-8")
    return meta


def rollback(datasets_dir: Path, version_id: str) -> Path:
    target = datasets_dir / f"{version_id}.json"
    if not target.exists():
        raise FileNotFoundError(version_id)
    records = json.loads(target.read_text(encoding="utf-8"))
    publish_version(records, datasets_dir, f"rollback to {version_id}")
    return target
