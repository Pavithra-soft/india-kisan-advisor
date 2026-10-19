from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageFilter, ImageStat


@dataclass
class QualityResult:
    ok: bool
    reason: str = ""


def check_image_quality(image: Image.Image) -> QualityResult:
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    mean_luma = stat.mean[0]
    if mean_luma < 35:
        return QualityResult(False, "Photo is too dark; retake in daylight.")
    if mean_luma > 245:
        return QualityResult(False, "Photo is overexposed; reduce glare and retake.")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0]
    if edge_mean < 4.0:
        return QualityResult(False, "Photo looks blurry; hold steady and focus on the leaf.")
    return QualityResult(True)
