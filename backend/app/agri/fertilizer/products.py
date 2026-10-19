from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FertilizerProduct:
    product_id: str
    name: str
    n_pct: float
    p2o5_pct: float
    k2o_pct: float


PRODUCTS: dict[str, FertilizerProduct] = {
    "urea": FertilizerProduct("urea", "Urea", n_pct=46.0, p2o5_pct=0.0, k2o_pct=0.0),
    "dap": FertilizerProduct("dap", "DAP", n_pct=18.0, p2o5_pct=46.0, k2o_pct=0.0),
    "mop": FertilizerProduct("mop", "MOP", n_pct=0.0, p2o5_pct=0.0, k2o_pct=60.0),
}


def kg_product_for_nutrient(product_id: str, nutrient: str, kg_nutrient: float) -> float:
    p = PRODUCTS[product_id]
    if nutrient == "n" and p.n_pct:
        return round(kg_nutrient * 100.0 / p.n_pct, 2)
    if nutrient == "p2o5" and p.p2o5_pct:
        return round(kg_nutrient * 100.0 / p.p2o5_pct, 2)
    if nutrient == "k2o" and p.k2o_pct:
        return round(kg_nutrient * 100.0 / p.k2o_pct, 2)
    return 0.0
