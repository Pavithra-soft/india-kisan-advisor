from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from app.agri.evaluation.report import format_accuracy_report
from app.agri.fertilizer import FertilizerEngine, FertilizerEngineError
from app.agri.retrieval import answer_question
from app.agri.retrieval.store import load_facts
from app.agri.schemas import FertilizerRecommendInput, GroundedAnswer, NotSureResponse, SoilTestInput
from app.agri.sync.freshness import freshness_badge
from app.agri.sync.phone_bundle import build_incremental_bundle
from app.config import get_settings
from app.agri.vision import diagnose_image_bytes

router = APIRouter(tags=["api"])


class SoilTestBody(BaseModel):
    n_kg_ha: Optional[float] = None
    p2o5_kg_ha: Optional[float] = None
    k2o_kg_ha: Optional[float] = None
    organic_carbon_pct: Optional[float] = None
    ph: Optional[float] = None
    ec_dsm: Optional[float] = None


class FertilizerRequest(BaseModel):
    crop_id: str
    region_id: str
    season: str
    target_yield_q_per_ha: float = Field(gt=0)
    soil_type: str = "unknown"
    irrigation_type: str = "unknown"
    previous_crop_id: Optional[str] = None
    soil_test: Optional[SoilTestBody] = None


class QuestionRequest(BaseModel):
    question: str
    crop_id: Optional[str] = None
    region_id: Optional[str] = None
    season: Optional[str] = None


def _serialize_answer(ans: GroundedAnswer | NotSureResponse) -> dict:
    if isinstance(ans, NotSureResponse):
        return {
            "not_sure": True,
            "message": ans.message,
            "suggested_next_step": ans.suggested_next_step,
            "confidence": ans.confidence.value,
        }
    last = ans.last_updated
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return {
        "not_sure": False,
        "sentences": ans.sentences,
        "citations": [c.__dict__ for c in ans.citations],
        "confidence": ans.confidence.value,
        "last_updated": ans.last_updated.isoformat(),
        "region_id": ans.region_id,
        "approximate": ans.approximate,
        "numbers": ans.numbers,
        "freshness": freshness_badge("default", last),
    }


@router.get("/health")
def health():
    return {"status": "up", "app": "india-kisan-advisor"}


@router.post("/qa")
def qa(body: QuestionRequest):
    ans = answer_question(body.question, crop_id=body.crop_id, region_id=body.region_id, season=body.season)
    return _serialize_answer(ans)


@router.post("/fertilizer/recommend")
def fertilizer_recommend(body: FertilizerRequest):
    st = SoilTestInput(**body.soil_test.model_dump()) if body.soil_test else None
    try:
        out = FertilizerEngine().recommend(
            FertilizerRecommendInput(
                crop_id=body.crop_id,
                region_id=body.region_id,
                season=body.season,
                target_yield_q_per_ha=body.target_yield_q_per_ha,
                soil_type=body.soil_type,
                irrigation_type=body.irrigation_type,
                previous_crop_id=body.previous_crop_id,
                soil_test=st,
            )
        )
    except FertilizerEngineError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "engine_version": out.engine_version,
        "parameter_version": out.parameter_version,
        "parameter_source": out.parameter_source,
        "nutrient_requirement": out.nutrient_requirement.__dict__,
        "applications": [a.__dict__ for a in out.applications],
        "cautions": out.cautions,
        "confidence": out.confidence.value,
        "approximate": out.approximate,
        "used_soil_test": out.used_soil_test,
        "sources": [s.__dict__ for s in out.sources],
    }


@router.post("/diagnose")
async def diagnose(file: UploadFile = File(...), crop_id: Optional[str] = None):
    data = await file.read()
    result = diagnose_image_bytes(data, crop_id=crop_id)
    if isinstance(result, NotSureResponse):
        return _serialize_answer(result)
    return {
        "not_sure": False,
        "prediction_set": result.prediction_set,
        "confidence": result.confidence.value,
        "calibrated_probs": result.calibrated_probs,
        "ood": result.ood,
        "quality_ok": result.quality_ok,
    }


@router.get("/sync/bundle")
def sync_bundle(
    region_id: str = Query(...),
    crop_ids: str = Query(..., description="Comma-separated crop IDs"),
    base_version: Optional[str] = None,
):
    settings = get_settings()
    crops = [c.strip() for c in crop_ids.split(",") if c.strip()]
    raw_facts = [
        {
            "record_id": r.record_id,
            "fact_type": r.fact_type.value,
            "title": r.title,
            "body": r.body,
            "crop_id": r.crop_id,
            "region_id": r.region_id,
            "season": r.season,
            "valid_from": r.valid_from.isoformat(),
            "valid_to": r.valid_to.isoformat() if r.valid_to else None,
            "source_name": r.source_name,
            "source_url": r.source_url,
            "numbers": r.numbers,
            "metadata": r.metadata,
        }
        for r in load_facts()
    ]
    bundle = build_incremental_bundle(
        raw_facts,
        region_id=region_id,
        crop_ids=crops,
        secret=settings.agri_bundle_secret,
        base_version=base_version,
    )
    return {
        "manifest": bundle.manifest,
        "signature": bundle.signature,
        "payload": json.loads(bundle.payload_json),
    }


@router.get("/accuracy-report")
def accuracy_report():
    settings = get_settings()
    if not settings.expose_accuracy_report:
        raise HTTPException(status_code=404, detail="disabled")
    return {"report_markdown": format_accuracy_report()}
