# Unsafe Output Regression Report

Date: 2026-06-03.

Status: local blocked-output regression report. This is not production proof, legal compliance proof, or model-quality proof.

## Guardrails Checked

- forbidden-claim registry
- blocked phrase YAML
- backend redline fixtures
- deterministic matcher safe summary/explanation tests
- web result-card copy scan
- mobile result-card and provider copy scan
- local provider summary guardrail replacements

## Blocked Categories

- private-feeling certainty
- hidden-motive certainty
- attraction prediction
- deception verdicts
- diagnosis/person labels
- neurotype inference
- relationship-style labeling
- manipulation/coercive persuasion
- shame, scarcity, streak, and compulsive engagement copy
- overconfident proof/guarantee wording

## Latest Local Focused Run

- `tests/test_vibe_matching_safe_phrasing.py`: covered by full pytest pass.
- `tests/test_redline_output_blocker.py`: covered by full pytest pass.
- `tests/test_redline_output_fixtures.py`: covered by full pytest pass.
- `mobile/tests/uxCopySafety.test.js`: covered by `mobile && npm test` pass.
- `web/tests/uxCopySafety.test.mjs`: covered by `web && npm test` pass.

Keep raw content out of reports.

## Remaining Risks

- New copy can still introduce unsafe phrasing if tests are bypassed.
- Provider/BYOK outputs must remain sanitized before display.
- Manual legal review is still required before tester invites.
