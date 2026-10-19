from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class QuarantineEntry:
    source: str
    reason: str
    payload: dict
    quarantined_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class QuarantineStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, entry: QuarantineEntry) -> None:
        rows = self._load()
        rows.append(
            {
                "source": entry.source,
                "reason": entry.reason,
                "payload": entry.payload,
                "quarantined_at": entry.quarantined_at,
            }
        )
        self.path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))
