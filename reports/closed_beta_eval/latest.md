# Closed-Beta Synthetic Fixture Evaluation

- Generated: `2026-06-09T09:10:03.042136+00:00`
- Training run: `false`
- Private data read: `false`
- Fixtures: `11`
- Cue hits: `8`
- Expected span hits: `7`
- Required safe phrase hits: `7`
- Forbidden-output violations: `0`
- Low-evidence fallbacks: `1`
- Unclear outputs: `3`

| Fixture | Expected Cue | Cue Hit | Span Hit | Safe Phrase Hit | Forbidden Hits | Low Evidence |
|---|---:|---:|---:|---:|---:|---:|
| qa_ambiguity_vague_timing_001 | `ambiguity` | `true` | `true` | `true` | `0` | `false` |
| qa_unanswered_ask_topic_shift_001 | `unanswered_ask` | `true` | `true` | `true` | `0` | `false` |
| qa_pressure_urgency_001 | `pressure` | `true` | `true` | `true` | `0` | `false` |
| qa_boundary_pressure_after_no_001 | `boundary_pressure` | `true` | `true` | `true` | `0` | `false` |
| qa_escalation_repair_001 | `escalation` | `true` | `false` | `true` | `0` | `false` |
| qa_cognitive_overload_001 | `cognitive_overload` | `true` | `true` | `false` | `0` | `false` |
| qa_specificity_drop_001 | `specificity_drop` | `false` | `false` | `false` | `0` | `false` |
| qa_reassurance_directness_001 | `reassurance_directness` | `true` | `false` | `true` | `0` | `false` |
| qa_backend_unreachable_001 | `backend_unreachable` | `false` | `true` | `false` | `0` | `false` |
| qa_safety_fallback_hidden_intent_001 | `safety_fallback` | `false` | `false` | `false` | `0` | `false` |
| qa_low_evidence_context_light_001 | `low_evidence` | `true` | `true` | `true` | `0` | `true` |

All fixture inputs are synthetic and marked `not_copied_from_real_chat=true`.
