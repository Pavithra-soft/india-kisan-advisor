from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseGate:
    name: str
    metric: str
    min_value: float | None = None
    max_value: float | None = None


RELEASE_GATES: list[ReleaseGate] = [
    ReleaseGate("qa_correctness", "qa_correctness", min_value=0.85),
    ReleaseGate("citation_faithfulness", "citation_faithfulness", min_value=0.95),
    ReleaseGate("numeric_exact_match", "numeric_exact_match", min_value=1.0),
    ReleaseGate("fertilizer_manual_match", "fertilizer_manual_match", min_value=1.0),
    ReleaseGate("vision_top1_field", "vision_top1", min_value=0.75),
    ReleaseGate("vision_ood_rejection", "vision_ood_rejection", min_value=0.8),
    ReleaseGate("calibration_ece", "calibration_ece", max_value=0.12),
]


def gate_passes(gate: ReleaseGate, metrics: dict[str, float]) -> bool:
    val = metrics.get(gate.metric)
    if val is None:
        return False
    if gate.min_value is not None and val < gate.min_value:
        return False
    if gate.max_value is not None and val > gate.max_value:
        return False
    return True
