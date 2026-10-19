from __future__ import annotations

from datetime import date

from app.agri.retrieval.hybrid import ScoredRecord
from app.agri.retrieval.store import FactRecord
from app.agri.schemas import ConfidenceLevel


def calibrated_confidence(
    top: ScoredRecord | None,
    records: list[FactRecord],
    *,
    region_id: str | None,
    verification_ok: bool,
) -> ConfidenceLevel:
    if not top or not verification_ok:
        return ConfidenceLevel.NOT_SURE
    score = top.score
    region_match = 1.0 if region_id and top.record.region_id in (region_id, "in") else 0.5
    freshness = 1.0
    today = date.today()
    if top.record.valid_to:
        days_left = (top.record.valid_to - today).days
        freshness = 0.5 if days_left < 2 else 1.0
    agreement = min(1.0, len(records) / 3.0)
    # Placeholder calibration — thresholds tuned on tiny golden set in tests
    raw = 0.45 * min(score, 1.0) + 0.25 * region_match + 0.2 * freshness + 0.1 * agreement
    if raw >= 0.55:
        return ConfidenceLevel.HIGH
    if raw >= 0.4:
        return ConfidenceLevel.MEDIUM
    if raw >= 0.28:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.NOT_SURE
