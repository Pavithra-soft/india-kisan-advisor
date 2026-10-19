from __future__ import annotations

from datetime import date

from app.agri.fertilizer import formulas_v1
from app.agri.fertilizer.products import kg_product_for_nutrient
from app.agri.schemas import (
    ENGINE_VERSION_FERTILIZER,
    ConfidenceLevel,
    FertilizerApplication,
    FertilizerRecommendInput,
    FertilizerRecommendOutput,
    NutrientPlan,
    SourceCitation,
    SoilTestInput,
)


class FertilizerEngineError(ValueError):
    pass


class FertilizerEngine:
    def recommend(self, inp: FertilizerRecommendInput) -> FertilizerRecommendOutput:
        params = formulas_v1.load_params()
        if inp.crop_id not in params["crops"]:
            raise FertilizerEngineError(f"Unsupported crop_id: {inp.crop_id}")

        cautions: list[str] = []
        used_soil_test = False
        approximate = False
        confidence = ConfidenceLevel.HIGH

        if inp.soil_test and _has_minimum_soil_test(inp.soil_test):
            used_soil_test = True
            st = {
                "n_kg_ha": inp.soil_test.n_kg_ha or 0,
                "p2o5_kg_ha": inp.soil_test.p2o5_kg_ha or 0,
                "k2o_kg_ha": inp.soil_test.k2o_kg_ha or 0,
            }
            nutrients = formulas_v1.recommend_from_soil_test(inp.crop_id, inp.target_yield_q_per_ha, st)
        else:
            approximate = True
            confidence = ConfidenceLevel.LOW_MEDIUM
            cautions.append("No soil test: using regional average range midpoint; get a soil test for a precise plan.")
            ra = params["crops"][inp.crop_id]["regional_average_without_soil_test"]
            nutrients = {
                "n": _mid(ra["n_kg_ha"]),
                "p2o5": _mid(ra["p2o5_kg_ha"]),
                "k2o": _mid(ra["k2o_kg_ha"]),
            }

        nutrients, cap_notes = formulas_v1.enforce_max_safe(inp.crop_id, nutrients)
        cautions.extend(cap_notes)

        if inp.soil_test and inp.soil_test.ph is not None and inp.soil_test.ph < 5.5:
            cautions.append("Soil pH below 5.5: consider liming per local extension guidance before heavy P application.")
        if inp.soil_test and inp.soil_test.ec_dsm is not None and inp.soil_test.ec_dsm > 2.0:
            cautions.append("High EC: leaching risk for N; split applications and monitor salinity.")

        applications = _build_splits(inp.crop_id, nutrients, params)
        sources = [
            SourceCitation(
                record_id=f"fertilizer-{params['version']}",
                title="Fertilizer parameter set",
                source_name=params["source"],
                source_url=params["source_url"],
                region_id=inp.region_id,
                as_of=date.today(),
            )
        ]

        return FertilizerRecommendOutput(
            engine_version=ENGINE_VERSION_FERTILIZER,
            parameter_source=params["source"],
            parameter_version=params["version"],
            nutrient_requirement=NutrientPlan(
                n_kg_ha=nutrients["n"],
                p2o5_kg_ha=nutrients["p2o5"],
                k2o_kg_ha=nutrients["k2o"],
            ),
            applications=applications,
            cautions=cautions,
            confidence=confidence,
            approximate=approximate,
            sources=sources,
            used_soil_test=used_soil_test,
        )


def _has_minimum_soil_test(st: SoilTestInput) -> bool:
    return st.n_kg_ha is not None and st.p2o5_kg_ha is not None and st.k2o_kg_ha is not None


def _mid(rng: dict[str, float]) -> float:
    return round((rng["min"] + rng["max"]) / 2.0, 2)


def _build_splits(crop_id: str, nutrients: dict[str, float], params: dict) -> list[FertilizerApplication]:
    splits = params["crops"][crop_id]["splits"]
    placement = params["crops"][crop_id]["placement"]
    apps: list[FertilizerApplication] = []
    for sp in splits:
        n_kg = round(nutrients["n"] * sp["n_frac"], 2)
        p_kg = round(nutrients["p2o5"] * sp["p_frac"], 2)
        k_kg = round(nutrients["k2o"] * sp["k_frac"], 2)
        products = []
        if p_kg > 0:
            products.append({"product_id": "dap", "kg_per_ha": kg_product_for_nutrient("dap", "p2o5", p_kg)})
        if n_kg > 0:
            products.append({"product_id": "urea", "kg_per_ha": kg_product_for_nutrient("urea", "n", n_kg)})
        if k_kg > 0:
            products.append({"product_id": "mop", "kg_per_ha": kg_product_for_nutrient("mop", "k2o", k_kg)})
        apps.append(
            FertilizerApplication(
                growth_stage=sp["stage"],
                timing=sp["timing"],
                products=products,
                placement=placement,
            )
        )
    return apps
