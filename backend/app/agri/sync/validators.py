from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationIssue:
    field: str
    message: str


def validate_price_record(row: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    price = row.get("price_inr_per_quintal")
    if price is None:
        issues.append(ValidationIssue("price_inr_per_quintal", "missing"))
    else:
        try:
            p = float(price)
            if p <= 0 or p > 100000:
                issues.append(ValidationIssue("price_inr_per_quintal", "out of range"))
        except (TypeError, ValueError):
            issues.append(ValidationIssue("price_inr_per_quintal", "not numeric"))
    if not row.get("market"):
        issues.append(ValidationIssue("market", "missing"))
    if not row.get("as_of"):
        issues.append(ValidationIssue("as_of", "missing"))
    return issues


def robust_z_outlier(values: list[float], value: float, z_thresh: float = 3.5) -> bool:
    if len(values) < 5:
        return False
    med = statistics.median(values)
    mad = statistics.median([abs(v - med) for v in values]) or 1e-6
    z = 0.6745 * (value - med) / mad
    return abs(z) > z_thresh
