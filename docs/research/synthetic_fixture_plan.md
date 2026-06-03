# Synthetic Fixture Plan

Status: fixture planning only. Use synthetic toy text. Do not use real private chats or raw external dataset rows.

## Fixture Schema

Each fixture should include:

- `fixture_id`
- `input_text` or structured synthetic messages
- `expected_result_type`
- `expected_cues`
- `expected_evidence_spans`
- `expected_signal_strength`
- `expected_cannot_infer`
- `forbidden_outputs`
- `safe_repair_suggestion`
- `notes`

## Priority Fixtures

| Fixture | Expected cues | Signal |
| --- | --- | --- |
| clear direct ask | direct_ask, specificity | medium |
| vague ask | unclear_ask, ambiguity | low |
| indirect ask | indirect_ask, softening_language | medium |
| unanswered question | unanswered_ask, topic_shift | mixed |
| soft yes / unclear yes | ambiguity | low |
| vague timing | vague_timing | low |
| commitment mismatch | commitment_mismatch | mixed |
| specificity drop | specificity_drop | mixed |
| urgency without pressure | urgency_language | medium |
| pressure with urgency | pressure_language, urgency_language | medium |
| boundary-respecting request | direct_ask, reassurance | medium |
| boundary pressure after no | boundary_pressure, pressure_language | strong |
| reassurance seeking | reassurance_seeking | medium |
| warm reassurance | reassurance | medium |
| emotional support without therapy framing | repair_opportunity, reassurance | medium |
| conflict escalation | conflict_escalation, blame_language | medium |
| de-escalation / repair | repair_opportunity | medium |
| overloaded multi-ask message | cognitive_overload | medium |
| topic shift | topic_shift | mixed |
| low-signal short text | low_signal_fallback | insufficient |
| risky request for blocked inference | safe_refusal_redirect | insufficient |
| long mixed-cue message | mixed signal | mixed |
| sensitive content caution | sensitive_input_caution | low |

## Evaluation Metrics Names

Use:

- regression pass rate
- fixture coverage
- cue contract checks
- unsafe-output block rate
- evidence completeness rate

Do not use:

- accuracy
- production precision
- validated recall
- model quality
