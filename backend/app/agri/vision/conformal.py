from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PredictionSet:
    labels: list[str]
    coverage_level: float


def conformal_top_k(probs: dict[str, float], *, coverage: float = 0.9, max_k: int = 3) -> PredictionSet:
    """Simplified split-conformal: include labels until cumulative prob >= coverage."""
    ordered = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    labels: list[str] = []
    cum = 0.0
    for label, p in ordered[:max_k]:
        labels.append(label)
        cum += p
        if cum >= coverage:
            break
    if not labels and ordered:
        labels = [ordered[0][0]]
    return PredictionSet(labels=labels, coverage_level=coverage)
