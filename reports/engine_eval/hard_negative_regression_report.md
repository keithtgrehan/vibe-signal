# Synthetic Fixture API Regression Report

Status: synthetic API regression only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.

- API base URL: `http://localhost:5050`
- Endpoint: `/api/analyze`
- Seed: `20260603`
- Synthetic fixture pool: `1000` conversations / `2000` messages
- Evaluated synthetic conversations: `1000`
- API regression pass rate: `733/1000`
- Cue contract pass rate: `1000/1000`
- Evidence completeness rate: `1000/1000`
- Unsafe-output block rate: `1000/1000`
- Fallback correctness rate: `733/1000`
- API transport failures: `0`
- Missing expected cue count: `0`
- Unexpected cue count: `0`

## Evaluated Split Counts

- `hard_negative`: `1000`

## Evaluated Conversation Counts

- `boundary_without_conflict`: `67`
- `conflict_without_diagnosis`: `67`
- `delay_without_evasion`: `67`
- `directness_without_pressure`: `67`
- `emotional_word_without_diagnosis`: `66`
- `hedging_without_ambiguity`: `67`
- `normal_topic_change`: `67`
- `polite_refusal`: `66`
- `reassurance_without_romantic_interpretation`: `67`
- `softener_without_weakness`: `66`
- `specificity_without_drop`: `67`
- `timing_clarity_without_pressure`: `66`
- `topic_bridge_not_evasion`: `66`
- `urgency_without_pressure`: `67`
- `warm_reassurance_without_attachment`: `67`

## Notes

- `/api/analyze` returns deterministic cue evidence, not the full match result. Match-specific expected cues may appear as false negatives until the analyze route exposes equivalent evidence.
- `cheating_ambiguous` is private synthetic evaluation metadata only and must never be described as product capability.
- Reports store synthetic API responses separately from fixture definitions under `reports/engine_eval/`.
