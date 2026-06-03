# Human Labeling Rubric V1

Status: seed rubric for synthetic Vibe Signal cue review. This is not a model-quality claim, accuracy claim, legal approval, or production readiness.

## Scope

Review observable wording only. Labels should describe visible text cues such as clarity, ambiguity, directness, reassurance, pressure wording, cognitive load, unanswered asks, boundary pressure, escalation risk, and repair opportunities.

## Do Not Label

- hidden intent
- cheating
- attraction
- diagnosis
- true emotion
- attachment style
- neurotype
- deception certainty
- personality labels
- whether someone will reply
- whether someone should be influenced or pressured

## Label Fields

| Field | Meaning |
| --- | --- |
| `fixture_id` | Synthetic conversation identifier. |
| `cue_id` | Observable cue being reviewed. |
| `cue_present` | Whether the visible wording supports the cue. |
| `evidence_text` | Short visible phrase supporting the cue; empty when cue is absent. |
| `evidence_supports_cue` | Whether the evidence phrase actually supports the selected cue. |
| `unsafe_wording_flag` | True if the candidate label would imply a blocked inference. |
| `low_signal_flag` | True if the visible text is too short or sparse for normal cue review. |
| `reviewer` | Human reviewer ID, or `synthetic_bootstrap` for generated seed labels. |
| `not_human_validated` | True for bootstrap labels and any row not reviewed by a human. |

## Bootstrap Labels

Rows with `reviewer: synthetic_bootstrap` and `not_human_validated: true` come from fixture expectations only. They are useful for evaluator plumbing and regression sanity checks, but they are not human-reviewed labels and must not be used for accuracy claims.

## Review Rule

If a cue requires context not visible in the synthetic text, mark the cue absent or low-signal. Do not fill missing context with assumptions.
