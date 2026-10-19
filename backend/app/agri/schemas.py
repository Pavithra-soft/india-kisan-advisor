from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

ENGINE_VERSION_FERTILIZER = "fertilizer_v1"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW_MEDIUM = "low_medium"
    LOW = "low"
    NOT_SURE = "not_sure"


class FactType(str, Enum):
    CROP = "crop"
    NUTRIENT = "nutrient"
    FERTILIZER = "fertilizer"
    PEST = "pest"
    SCHEME = "scheme"
    PRICE = "price"
    EXPLANATORY = "explanatory"


@dataclass(frozen=True)
class FactRecord:
    record_id: str
    fact_type: FactType
    title: str
    body: str
    crop_id: str | None
    region_id: str | None
    season: str | None
    valid_from: date
    valid_to: date | None
    source_name: str
    source_url: str
    numbers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceCitation:
    record_id: str
    title: str
    source_name: str
    source_url: str
    region_id: str | None
    as_of: date


@dataclass
class NotSureResponse:
    message: str = "Not sure"
    suggested_next_step: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.NOT_SURE


@dataclass
class GroundedAnswer:
    sentences: list[str]
    citations: list[SourceCitation]
    confidence: ConfidenceLevel
    last_updated: datetime
    region_id: str | None
    approximate: bool = False
    numbers: dict[str, str] = field(default_factory=dict)


@dataclass
class SoilTestInput:
    n_kg_ha: float | None = None
    p2o5_kg_ha: float | None = None
    k2o_kg_ha: float | None = None
    organic_carbon_pct: float | None = None
    ph: float | None = None
    ec_dsm: float | None = None


@dataclass
class FertilizerRecommendInput:
    crop_id: str
    region_id: str
    season: str
    target_yield_q_per_ha: float
    soil_type: str
    irrigation_type: str
    previous_crop_id: str | None
    soil_test: SoilTestInput | None = None
    variety_type: str | None = None


@dataclass
class NutrientPlan:
    n_kg_ha: float
    p2o5_kg_ha: float
    k2o_kg_ha: float


@dataclass
class FertilizerApplication:
    growth_stage: str
    timing: str
    products: list[dict[str, Any]]
    placement: str


@dataclass
class FertilizerRecommendOutput:
    engine_version: str
    parameter_source: str
    parameter_version: str
    nutrient_requirement: NutrientPlan
    applications: list[FertilizerApplication]
    cautions: list[str]
    confidence: ConfidenceLevel
    approximate: bool
    sources: list[SourceCitation]
    used_soil_test: bool


@dataclass
class CropSuitabilityInput:
    crop_id: str
    latitude: float
    longitude: float
    soil_ph: float | None
    soil_texture: str | None
    rainfall_mm_annual: float | None
