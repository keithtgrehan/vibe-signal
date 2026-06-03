# Hard-Negative False-Positive Reduction

Status: bootstrap-only synthetic hard-negative report. This is not human-reviewed accuracy, model-quality proof, validation, or production-readiness evidence.

## Before

- Hard-negative conversations: `1000`
- Hard-negative pass count: `332/1000`
- Hard-negative unexpected cue count: `334`

## After

- Hard-negative conversations: `1000`
- Hard-negative pass count: `733/1000`
- Hard-negative unexpected cue count: `0`
- Hard-negative split precision/recall/F1: `1.0 / 1.0 / 1.0`

## Main Changes

- Removed cross-speaker `specificity_drop` false positives on acknowledgement replies.
- Prevented low-pressure softener commands such as `No rush, just send it when you can` from becoming `directness`.
- Added support for reassurance phrases such as `no stress`, `no worries`, and `if you can`.
- Kept urgency separate from pressure: deadline wording can be urgency, but pressure still requires obligation, constrained choice, or reduced response space.
- Patched hard-negative fixture expectations where an observed cue was legitimately supported by text, such as directness in explicit reply commitments.

## Remaining Risk

Hard negatives are still synthetic. They are useful for regression coverage and false-positive reduction, but they are not a substitute for human-reviewed labels.

