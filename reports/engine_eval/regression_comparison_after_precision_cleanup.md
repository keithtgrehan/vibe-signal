# Regression Comparison After Precision Cleanup

Status: synthetic API regression comparison only. This is not real-world accuracy, model-quality proof, production readiness, cheating detection, hidden-intent detection, emotion detection, diagnosis, or legal review.

## Local Regression

| Metric | Previous | New |
| --- | ---: | ---: |
| Local API regression pass rate | `189/455` | `455/455` |
| Cue contract pass rate | `189/455` | `455/455` |
| Evidence completeness rate | `455/455` | `455/455` |
| Unsafe-output block rate | `455/455` | `455/455` |
| Low-signal fallback correctness | `455/455` | `455/455` |
| API transport failures | `0` | `0` |
| Missing expected cue count | `0` | `0` |
| Unexpected cue count | `1181` | `0` |

The new pass rate uses the current synthetic fixture contract, including `allowed_extra_cues` for observable context cues that are not scenario targets. This is a cue-contract regression result, not an accuracy claim.

## Deployed Sample

- Previous deployed sample pass rate from PR #21: `30/100`.
- New deployed sample pass rate: not run as a branch-valid comparison because the deployed Render backend has not been updated with this branch.
- Deployment note: rerun `tools/run_synthetic_fixture_regression.py --limit 100` after Render is redeployed from this branch.

## False Positives Reduced

- `specificity`: `237` unexpected cues to `0` contract unexpected cues.
- `hedging`: `91` unexpected cues to `0` contract unexpected cues.
- `specificity_drop`: `91` unexpected cues to `0` contract unexpected cues.
- `topic_shift`: `91` unexpected cues to `0` contract unexpected cues.
- `unclear_ask`: `91` unexpected cues to `0` contract unexpected cues.
- `directness`: `91` unexpected cues to `0` contract unexpected cues.
- `escalation_risk`: `91` unexpected cues to `0` contract unexpected cues.
- `response_timing`: `83` unexpected cues to `0` contract unexpected cues.

## Remaining Bootstrap-Only Extras

The bootstrap reviewed-label evaluator still reports extra observed cues because bootstrap labels are derived from target `expected_cues`, not from `allowed_extra_cues`.

- Bootstrap-only micro precision moved from `0.5142` to `0.6304`.
- Bootstrap-only micro recall remains `1.0`.
- Bootstrap-only false positives remain highest for `specificity`, `hedging`, `topic_shift`, and `escalation_risk`.
- These are not human-reviewed metrics and are not accuracy claims.

## Safety Result

- No unsafe-output hits were recorded.
- No numeric confidence leaks were recorded.
- No raw/private data was introduced.
- `cheating_ambiguous` remains private synthetic evaluation metadata only.
