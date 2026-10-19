from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class PhoneBundle:
    manifest: dict
    signature: str
    payload_json: str


def build_incremental_bundle(
    records: list[dict],
    *,
    region_id: str,
    crop_ids: list[str],
    secret: str,
    base_version: str | None = None,
) -> PhoneBundle:
    filtered = [
        r
        for r in records
        if (not r.get("region_id") or r.get("region_id") in (region_id, "in"))
        and (not r.get("crop_id") or r.get("crop_id") in crop_ids)
    ]
    manifest = {
        "type": "incremental",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "region_id": region_id,
        "crop_ids": crop_ids,
        "base_version": base_version,
        "record_count": len(filtered),
    }
    payload_json = json.dumps({"manifest": manifest, "records": filtered}, sort_keys=True)
    sig = hmac.new(secret.encode("utf-8"), payload_json.encode("utf-8"), hashlib.sha256).hexdigest()
    return PhoneBundle(manifest=manifest, signature=sig, payload_json=payload_json)


def verify_bundle(bundle: PhoneBundle, secret: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), bundle.payload_json.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, bundle.signature)
