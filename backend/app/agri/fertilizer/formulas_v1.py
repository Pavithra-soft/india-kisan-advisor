from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "fertilizer_params_v1.json"


@lru_cache
def load_params() -> dict[str, Any]:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def soil_test_class(nutrient: str, value: float, crop_id: str) -> str:
    params = load_params()
    classes = params["crops"][crop_id]["soil_test_classes"][nutrient]
    if value <= classes["low"]["max"]:
        return "low"
    if value <= classes["medium"]["max"]:
        return "medium"
    return "high"


def adjustment_for_class(rating: str, crop_id: str) -> float:
    params = load_params()
    return float(params["crops"][crop_id]["adjustment_factor"][rating])


def total_uptake_kg(crop_id: str, target_yield_q: float) -> dict[str, float]:
    params = load_params()
    u = params["crops"][crop_id]["uptake_kg_per_q"]
    return {
        "n": round(target_yield_q * u["n"], 2),
        "p2o5": round(target_yield_q * u["p2o5"], 2),
        "k2o": round(target_yield_q * u["k2o"], 2),
    }


def recommend_from_soil_test(crop_id: str, target_yield_q: float, soil_test: dict[str, float]) -> dict[str, float]:
    uptake = total_uptake_kg(crop_id, target_yield_q)
    out: dict[str, float] = {}
    for nut, key in [("n", "n_kg_ha"), ("p2o5", "p2o5_kg_ha"), ("k2o", "k2o_kg_ha")]:
        rating = soil_test_class(nut, soil_test[key], crop_id)
        adj = adjustment_for_class(rating, crop_id)
        out[nut] = round(uptake[nut] * adj, 2)
    return out


def enforce_max_safe(crop_id: str, plan: dict[str, float]) -> tuple[dict[str, float], list[str]]:
    params = load_params()
    caps = params["crops"][crop_id]["max_safe_kg_ha"]
    cautions: list[str] = []
    capped = dict(plan)
    for nut, cap in caps.items():
        if capped[nut] > cap:
            cautions.append(f"{nut.upper()} recommendation capped at published safe maximum {cap} kg/ha.")
            capped[nut] = float(cap)
    return capped, cautions
