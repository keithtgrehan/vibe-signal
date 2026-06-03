# Engine API Regression

Status: synthetic-only regression workflow. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.

## Local Backend Run

Terminal A:

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 5000
```

Terminal B:

```bash
VIBE_SIGNAL_API_URL=http://localhost:5000 \
python tools/run_synthetic_fixture_regression.py \
  --input data/synthetic/whatsapp/conversations.jsonl
```

If port `5000` is occupied by macOS Control Center/AirTunes or another local service, use a free port and keep the same API base URL in Terminal B:

```bash
PYTHONPATH=src python -m uvicorn backend.app:app --host 0.0.0.0 --port 5050

VIBE_SIGNAL_API_URL=http://localhost:5050 \
python tools/run_synthetic_fixture_regression.py \
  --input data/synthetic/whatsapp/conversations.jsonl
```

The command writes:

- `reports/engine_eval/synthetic_regression_api_responses.jsonl`
- `reports/engine_eval/synthetic_regression_results.jsonl`
- `reports/engine_eval/synthetic_regression_report.md`

## Deployed Sample

Use a bounded sample against production:

```bash
VIBE_SIGNAL_API_URL=https://vibe-signal.onrender.com \
python tools/run_synthetic_fixture_regression.py \
  --input data/synthetic/whatsapp/conversations.jsonl \
  --limit 100
```

Do not run large deployed sweeps by default.

## Metrics Names

Use regression terms only:

- API regression pass rate
- cue contract pass rate
- evidence completeness rate
- unsafe-output block rate
- fallback correctness rate

Do not call these accuracy, model quality, or validation.

## Current Precision-Cleanup Results

The local run on this branch used port `5050` because port `5000` was occupied by macOS Control Center/AirTunes.

- Local API regression: `455` synthetic conversations, `1000` messages, `0` transport errors.
- Local synthetic API regression pass rate: `455/455`.
- Local evidence completeness rate: `455/455`.
- Local unsafe-output block rate: `455/455`.
- Local fallback correctness rate: `455/455`.
- Deployed sample: not rerun as a branch-valid comparison because the hosted backend has not been redeployed from this branch.

The previous deployed sample from PR #21 was `30/100`; rerun the bounded sample after Render is updated.
