from __future__ import annotations

from datetime import datetime, timedelta, timezone

FRESHNESS_LIMITS_HOURS = {
    "price": 48,
    "scheme": 24 * 7,
    "weather": 24,
    "default": 24 * 7,
}


def freshness_badge(category: str, last_updated: datetime) -> dict[str, str]:
    limit_h = FRESHNESS_LIMITS_HOURS.get(category, FRESHNESS_LIMITS_HOURS["default"])
    now = datetime.now(timezone.utc)
    if last_updated.tzinfo is None:
        last_updated = last_updated.replace(tzinfo=timezone.utc)
    age = now - last_updated
    stale = age > timedelta(hours=limit_h)
    return {
        "last_updated": last_updated.isoformat(),
        "may_be_outdated": "true" if stale else "false",
        "category": category,
    }
