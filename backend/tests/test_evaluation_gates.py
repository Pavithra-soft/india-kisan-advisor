from pathlib import Path

from app.agri.evaluation.harness import run_all, run_release_gates


GOLDEN = Path(__file__).resolve().parent / "golden"


def test_fertilizer_golden_exact_match():
    m = run_all(GOLDEN)
    assert m.values["fertilizer_manual_match"] == 1.0


def test_release_gates_fail_until_vision_and_scale_ready():
    ok, m = run_release_gates(GOLDEN)
    assert m.values["fertilizer_manual_match"] == 1.0
    # Baseline: vision + calibration gates not met; document failures
    assert not ok
    assert any("vision" in f for f in m.failures)
