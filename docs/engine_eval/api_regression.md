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
python tools/generate_synthetic_whatsapp_fixtures.py \
  --messages 1000 \
  --api-url http://localhost:5000
```

If port `5000` is occupied by macOS Control Center/AirTunes or another local service, use a free port and keep the same API base URL in Terminal B:

```bash
PYTHONPATH=src python -m uvicorn backend.app:app --host 0.0.0.0 --port 5050

VIBE_SIGNAL_API_URL=http://localhost:5050 \
python tools/generate_synthetic_whatsapp_fixtures.py \
  --messages 1000 \
  --api-url http://localhost:5050
```

The command writes:

- `data/synthetic/whatsapp/conversations.jsonl`
- `reports/engine_eval/api_responses.jsonl`
- `reports/engine_eval/api_regression_results.jsonl`
- `reports/engine_eval/api_regression_report.md`

## Deployed Sample

Use a bounded sample against production:

```bash
VIBE_SIGNAL_API_URL=https://vibe-signal.onrender.com \
python tools/generate_synthetic_whatsapp_fixtures.py \
  --messages 1000 \
  --api-url https://vibe-signal.onrender.com \
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

## Current Seed Results

The first local run on this branch used port `5050` because port `5000` was occupied by macOS Control Center/AirTunes.

- Local API regression: `455` synthetic conversations, `1000` messages, `0` transport errors.
- Local strict API regression pass rate: `189/455`.
- Local evidence completeness rate: `455/455`.
- Local unsafe-output block rate: `455/455`.
- Local fallback correctness rate: `455/455`.
- Deployed sample: `100` synthetic conversations, `0` transport errors, strict pass rate `30/100`.

The deployed sample appears to be behind the branch route hardening because it still misses match-specific `/api/analyze` cues and low-signal fallback cases.
