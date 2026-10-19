# Agricultural accuracy add-on — design document

This add-on implements farmer-facing accuracy rules as **deterministic code + verified data**, with the LLM limited to formatting and explanation of retrieved, cited records. Priority order: accuracy, safety, simplicity, speed.

## Scope in this repository

| Deliverable | Location | Status |
|-------------|----------|--------|
| Design (this doc) | `docs/agri-accuracy-design.md` | Draft v1 |
| Fertilizer engine | `app/agri/fertilizer/` | v1 formulas + unit tests |
| Retrieval + verification | `app/agri/retrieval/` | Hybrid search, NLI-style rules, abstention |
| Vision pipeline | `app/agri/vision/` | Interfaces + quality gate + OOD; no trained weights in repo |
| Daily sync + phone bundle | `app/agri/sync/` | Server pipeline, quarantine, versioning, freshness |
| Evaluation | `app/agri/evaluation/` + `tests/agri/golden/` | Harness + release gates |
| Measured report | `docs/agri-accuracy-report.md` | Baseline run (targets mostly not met for ML) |

HTTP API (optional integration): `/agri/*` via `app/routes/agri.py`.

---

## 1. Core accuracy principles (implementation)

- **Facts**: `FactRecord` rows in `app/agri/data/facts_seed.json` (production: Postgres tables). Q&A never invents facts.
- **Numbers**: Fertilizer outputs come only from `FertilizerEngine` (`formulas_v1`). Q&A numbers are regex-extracted and compared to cited records (`verify_numeric_exact_match`).
- **Traceability**: Every answer sentence must cite `record_id`s; `verify_claim_support` checks overlap with record text.
- **Abstention**: `abstention.decide()` when retrieval score, verification, or confidence is below threshold → `"Not sure"` + `suggested_next_step`.
- **Gates**: `evaluation/gates.py` blocks release when metrics fail (`evaluation.harness.run_release_gates`).

---

## 2. Knowledge retrieval and Q&A

### Methods chosen

| Step | Choice | Why | Alternatives considered |
|------|--------|-----|-------------------------|
| Structured routing | Keyword + entity IDs from synonym graph | Zero hallucination path for doses, prices, schemes | Pure LLM routing (rejected: unreliable) |
| Text retrieval | BM25 + bag-of-character n-gram cosine | No extra ML deps; deterministic; multilingual-ish via char n-grams | Dense multilingual embeddings (planned: `e5-multilingual` + pgvector) |
| Rerank | Cross-encoder stub: weighted BM25 + metadata match | Placeholder until `ms-marco-MiniLM` cross-encoder in worker | LLM rerank (rejected for cost/latency) |
| Filtering | Hard filters on crop, region, season, `valid_from`/`valid_to` **before** rank | Wrong-region never in candidate set | Soft penalties only (rejected) |
| Entity resolution | Curated `synonyms.json` → canonical IDs | Auditable, fast | Open NER (rejected without labeled data) |
| Grounded generation | Template assembly from records (no free generation in v1) | Guarantees citation alignment | LLM with JSON schema (phase 2 behind verifier) |
| Verification | Rule-based token overlap + numeric exact match | Testable without NLI model | DeBERTa NLI (planned when GPU worker exists) |
| Confidence | Weighted score → bucket via calibrated thresholds on golden set | Transparent factors | Raw softmax (rejected: uncalibrated) |

### Pipeline

```
Question → entity_resolve → structured_query (if applicable)
        → hybrid_retrieve (metadata filter → BM25 → char cosine → rerank)
        → assemble_answer(records)
        → verify_claim_support + verify_numbers
        → abstention OR publish with confidence badge
```

---

## 3. Fertilizer recommendation engine

- **Not chat**: `POST /agri/fertilizer/recommend` calls `FertilizerEngine` only.
- **Method v1**: Soil-test rating classes (low/medium/high) for N and P₂O₅, K₂O from farmer input or regional default; nutrient need from published uptake/removal for **rice** (kharif) per `fertilizer_params_v1.json` (sourced to ICAR/state guideline placeholders — agronomist sign-off required before production).
- **Outputs**: kg/ha N, P, K; split applications; product mapping from `products.py`; cautions when pH/EC out of range.
- **No soil test**: Regional average band, `confidence=low_medium`, explicit soil-test CTA.
- **Versioning**: `ENGINE_VERSION = "fertilizer_v1"`; parameters file hash in response metadata.

---

## 4. Crop suitability

- **v1**: Rule engine in `schemas.CropSuitabilityInput` / future `suitability/rules.py` (not fully wired in API yet).
- **Learned model**: Not shipped until it beats rules on held-out regional data (gate in evaluation harness).

---

## 5. Pest and disease diagnosis

- **v1 in repo**: Image quality gate (blur/luminance), stub classifier returning calibrated probabilities, Mahalanobis-style OOD on feature vectors, conformal prediction set helper.
- **Not in repo**: Fine-tuned EfficientNet weights, field-photo golden set at scale — see accuracy report.

---

## 6. Prices and market data

- Normalization helpers in `sync/validators.py`; seed facts for wholesale rows with date + market.
- Outlier flag: robust z-score vs market median in sync validation.

---

## 7. Government schemes

- Structured `FactRecord` type `scheme` with `valid_to`; eligibility via rule matcher in `retrieval/structured.py` (partial — missing fields → conditional message).

---

## 8. Daily sync

- **Server**: `sync/pipeline.run_daily_sync` — adapters (stub), diff, validate, quarantine, publish low-risk, queue high-risk.
- **Versioning**: `sync/versioning.DatasetVersion` immutable snapshots under `data/agri/datasets/`.
- **Phone**: `sync/phone_bundle.build_incremental_bundle` — signed JSON manifest (HMAC with `AGRI_BUNDLE_SECRET`), atomic apply with rollback pointer.
- **Freshness**: `sync/freshness.freshness_badge` per data category.

Cron: call `run_daily_sync` at 02:00 local (Render cron / systemd); not auto-started from FastAPI lifespan.

---

## 9. Evaluation framework

- Golden files under `tests/agri/golden/`.
- `evaluation.harness.run_all` produces metrics; `gates.RELEASE_GATES` enforced in CI via `tests/agri/test_evaluation_gates.py`.

---

## 10. Transparency

API responses include: `confidence`, `sources[]` (id, title, date, region), `last_updated`, `approximate` flags, and `not_sure` payloads.

---

## Configuration

| Variable | Purpose |
|----------|---------|
| `AGRI_DATA_DIR` | Override seed data directory |
| `AGRI_BUNDLE_SECRET` | HMAC for phone sync bundles |
| `AGRI_SYNC_HOUR` | Documented default 2 (local) for ops |

---

## Open items (agronomist + ML)

1. Replace placeholder ICAR/state numbers in `fertilizer_params_v1.json` with signed-off regional tables.
2. Deploy dense embeddings + cross-encoder in a sidecar worker.
3. Train vision ensemble on licensed + field datasets; pass per-class gates.
4. Expand golden set to 500+ Q&A, 100+ fertilizer scenarios, 500+ images.
