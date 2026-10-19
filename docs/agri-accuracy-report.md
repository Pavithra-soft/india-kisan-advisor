# Agricultural accuracy report (baseline)

Generated from `app/agri/evaluation/harness.py` against seed golden data in `tests/agri/golden/`. Re-run via `GET /agri/accuracy-report` or `pytest tests/agri/test_evaluation_gates.py`.

## Measured metrics (seed set)

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| `fertilizer_manual_match` | 1.00 | ≥ 1.00 | Pass |
| `qa_correctness` | ~0.67–1.00 (3 items) | ≥ 0.85 | Marginal / insufficient N |
| `citation_faithfulness` | ~0.67+ | ≥ 0.95 | Fail (small set) |
| `numeric_exact_match` | 1.00 (when numbers cited) | 1.00 | Pass on tested rows |
| `vision_top1` | 0.00 (no trained model) | ≥ 0.75 | **Fail** |
| `vision_ood_rejection` | 0.00 (not evaluated on 500+ images) | ≥ 0.80 | **Fail** |
| `calibration_ece` | 0.25 (placeholder) | ≤ 0.12 | **Fail** |
| `price_error_rate` | 0.00 (no live feed in CI) | — | Not gated |

## Targets not met — improvement plan

1. **Vision**: Fine-tune 2–3 models on licensed + field photos; add TTA ensemble; measure top-1/top-3/OOD on 500+ golden images; enable gates per class.
2. **Q&A scale**: Expand golden set to 500+ expert-verified questions; deploy multilingual dense retrieval + cross-encoder reranker; replace template answers with schema-constrained LLM behind verifier.
3. **Calibration**: Fit isotonic regression on labeled confidence data; report ECE each release.
4. **Fertilizer**: Agronomist sign-off on `fertilizer_params_v1.json`; add 100+ regional scenarios from official manuals.
5. **Sync**: Wire Agmarknet/official scheme adapters; production quarantine review UI; cron at 02:00 local.

## Known limitations

- Parameter set is **draft** (ICAR/state placeholder text in JSON).
- Image diagnosis uses **stub** probabilities and simple OOD on RGB means — not for field use.
- Phone sync HMAC requires `AGRI_BUNDLE_SECRET` in production.

## Agronomist sign-off

- [ ] Fertilizer formulas v1  
- [ ] Pest class list and thresholds  
- [ ] Release gate thresholds for production  
