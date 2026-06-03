# NLP Fixture Regression Report

Date: 2026-06-03.

Status: local deterministic regression report. This is not an accuracy, validation, model-quality, or production-readiness report.

## Scope

Covered by local tests:

- deterministic matcher safe phrasing
- low-signal fallback behavior
- evidence phrase propagation
- signal-strength and cannot-infer result fields
- safer specificity-drop and contradiction false-positive handling
- backend `/api/match` contract tests
- mobile/web UX copy safety scans

## Metrics Names

- regression pass rate
- cue contract checks
- evidence completeness checks
- unsafe-output block checks

Do not interpret these as precision, recall, accuracy, or real-world validation.

## Latest Local Focused Run

- `python -m pytest -q tests/test_cue_taxonomy_fixtures.py`: passed `2/2`.
- `python -m pytest -q`: passed after updating the synthetic opt-out fixture rule so `we can stop anytime` counts as explicit consent/opt-out wording.
- `mobile && npm test`: passed `130/130`.
- `web && npm test`: passed `5/5`.

Record only command names and pass/fail summaries here; do not paste raw private content or response bodies.

## Remaining Coverage Gaps

- Human-reviewed labels are not available.
- Real-device iOS QA is pending.
- Edge cases from external benchmark datasets are metadata-only and not downloaded.
- Synthetic fixtures should be expanded for indirect asks, unanswered asks, topic shifts, pressure after boundaries, and sensitive-content caution.
