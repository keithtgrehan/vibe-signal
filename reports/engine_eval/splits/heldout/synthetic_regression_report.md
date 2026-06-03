# Synthetic Fixture API Regression Report

Status: synthetic API regression only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.

- API base URL: `http://localhost:5050`
- Endpoint: `/api/analyze`
- Seed: `20260603`
- Synthetic fixture pool: `500` conversations / `1000` messages
- Evaluated synthetic conversations: `500`
- API regression pass rate: `200/500`
- Cue contract pass rate: `200/500`
- Evidence completeness rate: `500/500`
- Unsafe-output block rate: `500/500`
- Fallback correctness rate: `300/500`
- API transport failures: `0`
- Missing expected cue count: `100`
- Unexpected cue count: `400`

## Evaluated Split Counts

- `heldout`: `500`

## Evaluated Conversation Counts

- `heldout_boundary_pressure`: `100`
- `heldout_clear_ask`: `100`
- `heldout_low_signal`: `100`
- `heldout_repair`: `100`
- `heldout_vague_timing`: `100`

## Notes

- `/api/analyze` returns deterministic cue evidence, not the full match result. Match-specific expected cues may appear as false negatives until the analyze route exposes equivalent evidence.
- `cheating_ambiguous` is private synthetic evaluation metadata only and must never be described as product capability.
- Reports store synthetic API responses separately from fixture definitions under `reports/engine_eval/`.
