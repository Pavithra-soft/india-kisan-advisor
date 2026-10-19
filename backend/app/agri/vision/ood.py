from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class OodResult:
    is_ood: bool
    energy_score: float


def mahalanobis_energy(features: list[float], mean: list[float], inv_cov_diag: list[float]) -> float:
    """Diagonal-covariance Mahalanobis distance squared (energy score)."""
    if len(features) != len(mean):
        raise ValueError("feature dimension mismatch")
    d2 = 0.0
    for x, m, iv in zip(features, mean, inv_cov_diag):
        diff = x - m
        d2 += diff * diff * iv
    return d2


def is_out_of_distribution(energy: float, threshold: float) -> OodResult:
    return OodResult(is_ood=energy > threshold, energy_score=energy)


def softmax_temperature(probs: list[float], temperature: float) -> list[float]:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    scaled = [p / temperature for p in probs]
    m = max(scaled)
    exps = [math.exp(p - m) for p in scaled]
    s = sum(exps)
    return [e / s for e in exps]
