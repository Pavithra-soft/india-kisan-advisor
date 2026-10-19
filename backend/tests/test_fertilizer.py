import json
from pathlib import Path

from app.agri.fertilizer.engine import FertilizerEngine
from app.agri.schemas import FertilizerRecommendInput, SoilTestInput

PARAMS = Path(__file__).resolve().parents[1] / "app" / "agri" / "data" / "fertilizer_params_v1.json"


def test_worked_examples_match_engine():
    engine = FertilizerEngine()
    examples = json.loads(PARAMS.read_text(encoding="utf-8"))["worked_examples"]
    for ex in examples:
        inp = ex["input"]
        st = inp.get("soil_test")
        out = engine.recommend(
            FertilizerRecommendInput(
                crop_id=inp["crop_id"],
                region_id=inp["region_id"],
                season=inp["season"],
                target_yield_q_per_ha=inp["target_yield_q_per_ha"],
                soil_type=inp.get("soil_type", "unknown"),
                irrigation_type=inp.get("irrigation_type", "unknown"),
                previous_crop_id=inp.get("previous_crop_id"),
                soil_test=SoilTestInput(**st) if st else None,
            )
        )
        exp = ex["expected_nutrient_kg_ha"]
        assert out.nutrient_requirement.n_kg_ha == exp["n"]
        assert out.nutrient_requirement.p2o5_kg_ha == exp["p2o5"]
        assert out.nutrient_requirement.k2o_kg_ha == exp["k2o"]


def test_without_soil_test_is_approximate():
    out = FertilizerEngine().recommend(
        FertilizerRecommendInput(
            crop_id="rice",
            region_id="ap",
            season="kharif",
            target_yield_q_per_ha=50,
            soil_type="clay",
            irrigation_type="flood",
            previous_crop_id=None,
            soil_test=None,
        )
    )
    assert out.approximate is True
    assert out.used_soil_test is False
