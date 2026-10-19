from __future__ import annotations

from datetime import datetime

from app.agri.retrieval import abstention, confidence, hybrid, verify
from app.agri.retrieval.entities import resolve_crop_from_question
from app.agri.retrieval.store import filter_valid, last_updated, load_facts
from app.agri.schemas import ConfidenceLevel, GroundedAnswer, NotSureResponse, SourceCitation


def answer_question(
    question: str,
    *,
    crop_id: str | None = None,
    region_id: str | None = None,
    season: str | None = None,
) -> GroundedAnswer | NotSureResponse:
    crop_id = crop_id or resolve_crop_from_question(question)
    pool = filter_valid(load_facts(), crop_id=crop_id, region_id=region_id, season=season)
    if not pool:
        return NotSureResponse(
            suggested_next_step="No verified records for this crop/region/season; check official portal or helpline.",
        )

    ranked = hybrid.hybrid_retrieve(question, pool, top_k=3)
    top = ranked[0] if ranked else None
    top_score = top.score if top else 0.0
    records = [s.record for s in ranked]

    sentences = [_sentence_from_record(r) for r in records[:2]]
    v = verify.verify_answer(sentences, records)
    conf = confidence.calibrated_confidence(top, records, region_id=region_id, verification_ok=v.ok)

    abst = abstention.decide(top_score=top_score, verification_ok=v.ok, confidence=conf)
    if abst:
        return abst

    citations = [
        SourceCitation(
            record_id=r.record_id,
            title=r.title,
            source_name=r.source_name,
            source_url=r.source_url,
            region_id=r.region_id,
            as_of=r.valid_from,
        )
        for r in records[:2]
    ]
    numbers = {}
    for r in records:
        numbers.update(r.numbers)

    return GroundedAnswer(
        sentences=sentences,
        citations=citations,
        confidence=conf,
        last_updated=last_updated(records),
        region_id=region_id,
        approximate=conf in (ConfidenceLevel.LOW, ConfidenceLevel.LOW_MEDIUM),
        numbers=numbers,
    )


def _sentence_from_record(record) -> str:
    cite = f"[{record.record_id}]"
    return f"{record.body} {cite}"
