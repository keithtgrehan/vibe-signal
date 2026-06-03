# Synthetic Fixture API Regression Report

Status: synthetic API regression only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.

- API base URL: `http://localhost:5050`
- Endpoint: `/api/analyze`
- Seed: `20260603`
- Synthetic fixture pool: `500` conversations / `1000` messages
- Evaluated synthetic conversations: `500`
- API regression pass rate: `500/500`
- Cue contract pass rate: `500/500`
- Evidence completeness rate: `500/500`
- Unsafe-output block rate: `500/500`
- Fallback correctness rate: `500/500`
- API transport failures: `0`
- Missing expected cue count: `0`
- Unexpected cue count: `0`

## Evaluated Split Counts

- `red_team`: `500`

## Evaluated Conversation Counts

- `user_asks_are_they_cheating`: `56`
- `user_asks_are_they_lying`: `56`
- `user_asks_attachment_style`: `56`
- `user_asks_diagnosis`: `56`
- `user_asks_do_they_like_me`: `56`
- `user_asks_hidden_intent`: `55`
- `user_asks_make_them_reply`: `55`
- `user_asks_manipulation`: `55`
- `user_asks_therapy_advice`: `55`

## Notes

- `/api/analyze` returns deterministic cue evidence, not the full match result. Match-specific expected cues may appear as false negatives until the analyze route exposes equivalent evidence.
- `cheating_ambiguous` is private synthetic evaluation metadata only and must never be described as product capability.
- Reports store synthetic API responses separately from fixture definitions under `reports/engine_eval/`.
