# Synthetic Fixture API Regression Report

Status: synthetic API regression only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.

- API base URL: `https://vibe-signal.onrender.com`
- Endpoint: `/api/analyze`
- Seed: `20260603`
- Synthetic fixture pool: `455` conversations / `1000` messages
- Evaluated synthetic conversations: `100`
- API regression pass rate: `100/100`
- Cue contract pass rate: `100/100`
- Evidence completeness rate: `100/100`
- Unsafe-output block rate: `100/100`
- Fallback correctness rate: `100/100`
- API transport failures: `0`
- Missing expected cue count: `0`
- Unexpected cue count: `0`

## Evaluated Conversation Counts

- `boundary_pressure`: `10`
- `cheating_ambiguous`: `10`
- `conflict_repair`: `10`
- `happy`: `10`
- `in_love`: `10`
- `low_signal`: `10`
- `new_in_love`: `10`
- `overloaded_message`: `10`
- `scared`: `10`
- `unhappy`: `10`

## Notes

- `/api/analyze` returns deterministic cue evidence, not the full match result. Match-specific expected cues may appear as false negatives until the analyze route exposes equivalent evidence.
- `cheating_ambiguous` is private synthetic evaluation metadata only and must never be described as product capability.
- Reports store synthetic API responses separately from fixture definitions under `reports/engine_eval/`.
