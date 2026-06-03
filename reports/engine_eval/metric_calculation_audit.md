# Metric Calculation Audit

Status: bootstrap-only synthetic metric audit. These values are not human-reviewed accuracy, model-quality proof, validation, or production-readiness claims.

## Formula Review

- Micro precision/recall/F1 are computed from total true positives, false positives, and false negatives across all cue labels.
- Per-cue precision/recall/F1 are computed from each cue's true positives, false positives, and false negatives.
- Macro precision is the arithmetic mean of per-cue precision values where precision is defined.
- Macro recall is the arithmetic mean of per-cue recall values where recall is defined.
- Macro F1 is the arithmetic mean of per-cue F1 values where F1 is defined.

Because macro F1 is averaged independently from per-cue F1 values, it is not expected to equal the harmonic mean of macro precision and macro recall. This explains why the PR #27 macro F1 could be higher than a harmonic calculation from macro precision and macro recall.

## Test Coverage

- `tests/test_reviewed_label_evaluator_fail_closed.py::test_macro_f1_is_average_of_per_cue_f1_not_harmonic_of_macro_precision_recall`
- Existing evaluator tests still cover fail-closed behavior, bootstrap-only reporting, split metrics, and scenario metrics.

## Result

No formula bug was found in the current evaluator semantics. The audit clarified the macro F1 definition with a controlled test so future readers do not treat independent macro averages as contradictory.

