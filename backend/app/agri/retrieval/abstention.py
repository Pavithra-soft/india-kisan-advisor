from __future__ import annotations

from dataclasses import dataclass

from app.agri.schemas import ConfidenceLevel, NotSureResponse


@dataclass(frozen=True)
class AbstentionThresholds:
    min_retrieval_score: float = 0.08
    require_verification: bool = True


def decide(
    *,
    top_score: float,
    verification_ok: bool,
    confidence: ConfidenceLevel,
    thresholds: AbstentionThresholds | None = None,
) -> NotSureResponse | None:
    th = thresholds or AbstentionThresholds()
    if top_score < th.min_retrieval_score:
        return NotSureResponse(
            suggested_next_step="Try a soil test, local extension officer, or state agri helpline.",
        )
    if th.require_verification and not verification_ok:
        return NotSureResponse(
            suggested_next_step="We could not verify this against our records; contact an extension officer.",
        )
    if confidence == ConfidenceLevel.NOT_SURE:
        return NotSureResponse(
            suggested_next_step="Share crop, season, and district for a better match, or call the helpline.",
        )
    return None
