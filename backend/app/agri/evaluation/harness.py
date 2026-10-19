from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.agri.evaluation.gates import RELEASE_GATES, gate_passes
from app.agri.fertilizer.engine import FertilizerEngine
from app.agri.retrieval.qa import answer_question
from app.agri.schemas import FertilizerRecommendInput, GroundedAnswer, NotSureResponse, SoilTestInput

GOLDEN_DIR = Path(__file__).resolve().parents[3] / "tests" / "golden"


@dataclass
class EvalMetrics:
    values: dict[str, float] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)


def run_all(golden_dir: Path | None = None) -> EvalMetrics:
    root = golden_dir or GOLDEN_DIR
    metrics = EvalMetrics()
    metrics.values.update(_eval_qa(root / "qa_questions.jsonl"))
    metrics.values.update(_eval_fertilizer(root / "fertilizer_scenarios.json"))
    # Vision / price gates: not met in baseline — explicit placeholders
    metrics.values.setdefault("vision_top1", 0.0)
    metrics.values.setdefault("vision_ood_rejection", 0.0)
    metrics.values.setdefault("calibration_ece", 0.25)
    metrics.values.setdefault("price_error_rate", 0.0)

    for gate in RELEASE_GATES:
        if not gate_passes(gate, metrics.values):
            metrics.failures.append(f"gate failed: {gate.name} ({gate.metric})")
    return metrics


def run_release_gates(golden_dir: Path | None = None) -> tuple[bool, EvalMetrics]:
    m = run_all(golden_dir)
    return (not m.failures, m)


def _eval_qa(path: Path) -> dict[str, float]:
    if not path.exists():
        return {"qa_correctness": 0.0, "citation_faithfulness": 0.0, "numeric_exact_match": 0.0}
    total = 0
    correct = 0
    faithful = 0
    numeric_checks = 0
    numeric_ok = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            total += 1
            ans = answer_question(
                row["question"],
                crop_id=row.get("crop_id"),
                region_id=row.get("region_id"),
                season=row.get("season"),
            )
            if isinstance(ans, NotSureResponse):
                if row.get("expect_not_sure"):
                    correct += 1
                continue
            if not isinstance(ans, GroundedAnswer):
                continue
            text = " ".join(ans.sentences)
            if row.get("must_contain_record_id") and row["must_contain_record_id"] in text:
                correct += 1
            if ans.citations and all(c.record_id in text for c in ans.citations):
                faithful += 1
            for num in row.get("must_include_numbers", []):
                numeric_checks += 1
                if str(num) in text:
                    numeric_ok += 1
    return {
        "qa_correctness": correct / total if total else 0.0,
        "citation_faithfulness": faithful / total if total else 0.0,
        "numeric_exact_match": (numeric_ok / numeric_checks) if numeric_checks else 1.0,
    }


def _eval_fertilizer(path: Path) -> dict[str, float]:
    if not path.exists():
        return {"fertilizer_manual_match": 0.0}
    data = json.loads(path.read_text(encoding="utf-8"))
    engine = FertilizerEngine()
    ok = 0
    total = 0
    for scenario in data.get("scenarios", []):
        total += 1
        inp = scenario["input"]
        st = inp.get("soil_test")
        soil = SoilTestInput(**st) if st else None
        out = engine.recommend(
            FertilizerRecommendInput(
                crop_id=inp["crop_id"],
                region_id=inp["region_id"],
                season=inp["season"],
                target_yield_q_per_ha=inp["target_yield_q_per_ha"],
                soil_type=inp.get("soil_type", "unknown"),
                irrigation_type=inp.get("irrigation_type", "unknown"),
                previous_crop_id=inp.get("previous_crop_id"),
                soil_test=soil,
            )
        )
        exp = scenario["expected_nutrient_kg_ha"]
        if (
            out.nutrient_requirement.n_kg_ha == exp["n"]
            and out.nutrient_requirement.p2o5_kg_ha == exp["p2o5"]
            and out.nutrient_requirement.k2o_kg_ha == exp["k2o"]
        ):
            ok += 1
    return {"fertilizer_manual_match": ok / total if total else 0.0}
