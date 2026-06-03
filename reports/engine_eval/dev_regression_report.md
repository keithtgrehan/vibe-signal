# Synthetic Fixture API Regression Report

Status: synthetic API regression only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, diagnosis, or production readiness.

- API base URL: `http://localhost:5050`
- Endpoint: `/api/analyze`
- Seed: `20260603`
- Synthetic fixture pool: `3000` conversations / `6000` messages
- Evaluated synthetic conversations: `3000`
- API regression pass rate: `1104/3000`
- Cue contract pass rate: `1183/3000`
- Evidence completeness rate: `2842/3000`
- Unsafe-output block rate: `3000/3000`
- Fallback correctness rate: `2684/3000`
- API transport failures: `0`
- Missing expected cue count: `1580`
- Unexpected cue count: `2686`

## Evaluated Split Counts

- `dev`: `3000`

## Evaluated Conversation Counts

- `answer_evasion_pattern`: `79`
- `blame_language`: `79`
- `boundary_pressure`: `79`
- `boundary_respecting_request`: `79`
- `cheating_ambiguous_private_eval_label`: `79`
- `clear_direct_answer`: `79`
- `clear_direct_ask`: `79`
- `cognitive_load`: `79`
- `commitment_mismatch`: `79`
- `conflict_escalation`: `79`
- `conflict_repair`: `79`
- `contextless_fine`: `79`
- `contradiction_against_prior_message`: `79`
- `emoji_only`: `78`
- `generic_greeting`: `78`
- `happy`: `79`
- `in_love`: `79`
- `indirect_ask`: `79`
- `mixed_signal`: `79`
- `new_in_love`: `79`
- `overloaded_message`: `79`
- `pressure_with_urgency`: `79`
- `repair_success`: `79`
- `repeated_request_after_no`: `79`
- `response_timing_delay`: `79`
- `response_timing_stacking`: `79`
- `short_hey`: `79`
- `short_lol_sure`: `79`
- `short_ok`: `79`
- `soft_yes_unclear_yes`: `79`
- `specificity_drop`: `79`
- `topic_shift`: `79`
- `unanswered_ask`: `79`
- `unclear_ask`: `79`
- `unsupported_claim_shift`: `79`
- `urgency_without_pressure`: `79`
- `vague_timing`: `79`
- `warm_reassurance`: `79`

## Notes

- `/api/analyze` returns deterministic cue evidence, not the full match result. Match-specific expected cues may appear as false negatives until the analyze route exposes equivalent evidence.
- `cheating_ambiguous` is private synthetic evaluation metadata only and must never be described as product capability.
- Reports store synthetic API responses separately from fixture definitions under `reports/engine_eval/`.
