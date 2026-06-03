# Engine API Regression Report

Status: synthetic API regression only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.

- API base URL: `http://localhost:5050`
- Endpoint: `/api/analyze`
- Seed: `20260603`
- Synthetic fixture pool: `455` conversations / `1000` messages
- Evaluated synthetic conversations: `455`
- API regression pass rate: `189/455`
- Cue contract pass rate: `189/455`
- Evidence completeness rate: `455/455`
- Unsafe-output block rate: `455/455`
- Fallback correctness rate: `455/455`
- API transport failures: `0`
- Missing expected cue count: `0`
- Unexpected cue count: `1181`

## Evaluated Conversation Counts

- `boundary_pressure`: `45`
- `cheating_ambiguous`: `45`
- `conflict_repair`: `45`
- `happy`: `46`
- `in_love`: `46`
- `low_signal`: `45`
- `new_in_love`: `46`
- `overloaded_message`: `45`
- `scared`: `46`
- `unhappy`: `46`

## Notes

- `/api/analyze` returns deterministic cue evidence, not the full match result. Match-specific expected cues may appear as false negatives until the analyze route exposes equivalent evidence.
- `cheating_ambiguous` is private synthetic evaluation metadata only and must never be described as product capability.
- Reports store synthetic API responses separately from fixture definitions under `reports/engine_eval/`.
