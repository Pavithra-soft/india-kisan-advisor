from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image

from app.agri.schemas import ConfidenceLevel, NotSureResponse
from app.agri.vision import conformal, ood, quality_gate

# Stub class centroids for OOD (no trained weights in repo)
_CLASS_MEAN = [0.2, 0.5, 0.3]
_INV_COV = [1.0, 1.0, 1.0]
_OOD_THRESHOLD = 2.5

_STUB_PROBS = {
    "bph_damage": 0.55,
    "blast_leaf": 0.25,
    "healthy": 0.20,
}


@dataclass
class DiagnosisResult:
    prediction_set: list[str]
    confidence: ConfidenceLevel
    calibrated_probs: dict[str, float]
    ood: bool
    quality_ok: bool


def diagnose_image_bytes(data: bytes, *, crop_id: str | None = None) -> DiagnosisResult | NotSureResponse:
    image = Image.open(BytesIO(data))
    q = quality_gate.check_image_quality(image)
    if not q.ok:
        return NotSureResponse(message="Not sure", suggested_next_step=q.reason)

    # Stub features from downscaled grayscale mean channels
    small = image.convert("RGB").resize((32, 32))
    pixels = list(small.getdata())
    r = sum(p[0] for p in pixels) / len(pixels) / 255.0
    g = sum(p[1] for p in pixels) / len(pixels) / 255.0
    b = sum(p[2] for p in pixels) / len(pixels) / 255.0
    features = [r, g, b]

    energy = ood.mahalanobis_energy(features, _CLASS_MEAN, _INV_COV)
    ood_res = ood.is_out_of_distribution(energy, _OOD_THRESHOLD)
    if ood_res.is_ood:
        return NotSureResponse(
            suggested_next_step="Image does not match known crop pest patterns; contact a plant protection officer.",
        )

    calibrated = dict(zip(_STUB_PROBS.keys(), ood.softmax_temperature(list(_STUB_PROBS.values()), 1.5)))
    pset = conformal.conformal_top_k(calibrated, coverage=0.85)
    top_p = max(calibrated.values())
    conf = ConfidenceLevel.HIGH if top_p >= 0.7 else ConfidenceLevel.MEDIUM if top_p >= 0.5 else ConfidenceLevel.LOW

    return DiagnosisResult(
        prediction_set=pset.labels,
        confidence=conf,
        calibrated_probs=calibrated,
        ood=False,
        quality_ok=True,
    )
