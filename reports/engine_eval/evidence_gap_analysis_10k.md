# 10k Evidence Gap Analysis

Status: synthetic API regression analysis only. This is not real-world accuracy, model-quality proof, validation, or production-readiness evidence.

## Before

- Evidence completeness: `4574/5000`
- Evidence gap count: `426`
- Likely weak areas: contradiction-style cues, overloaded/cognitive-load fixtures, response timing expectations, and unsupported claim shifts.

## After

- Evidence completeness: `5000/5000`
- Evidence gap count: `0`
- Unsafe-output block rate: `5000/5000`

## Fixes

- Added observable contradiction evidence for `already sent` versus `not sent` statements without any deception claim.
- Added unsupported-claim-shift evidence for approved/not-approved style claim changes.
- Tightened `specificity_drop` so it requires same-speaker concrete-to-vague change or a direct concrete ask followed by a vague non-answer.
- Expanded dense list detection for `cognitive_load` and `overloaded_message` while retaining evidence spans.
- Calibrated synthetic expectations where labels contradicted cue preconditions.

## Remaining Notes

- `contradiction_against_prior_message` still has bootstrap false negatives in scenarios where the two-message fixture cannot support all expected private-eval labels simultaneously.
- Human-reviewed labels are still required before treating any metric as validation.

