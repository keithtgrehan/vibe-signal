# Post-Merge Precision Verification

Status: post-merge synthetic engine verification only. These are bootstrap-only synthetic regression results, not accuracy, model-quality, validation, production-readiness, cheating-detection, hidden-intent, attraction, deception-certainty, diagnosis, or therapy-support claims.

## Branch And Merge State

- Verification branch: `codex/engine-cue-precision-postmerge-verify`
- Updated local main commit verified: `8b13108e23a4b2cf9dd2d33a5df7074b63059f73`
- PR #22: merged
- PR #22 title: `Tighten deterministic cue precision regression`
- PR #22 merge commit observed: `8b13108e23a4b2cf9dd2d33a5df7074b63059f73`

## PR #22 Artifacts Checked

- `reports/engine_eval/synthetic_regression_report.md`: present
- `tools/run_synthetic_fixture_regression.py`: present
- `tests/test_specificity_precision.py`: present
- `tests/test_hedging_precision.py`: present
- `tests/test_topic_shift_precision.py`: present
- `tests/test_answer_evasion_pattern.py`: present
- `tests/test_commitment_contradiction_without_deception.py`: present
- `tests/test_response_timing_context.py`: present
- `configs/vibe_cue_taxonomy.yml`: present
- `src/vibesignal_ai/features/cue_taxonomy.py`: present
- `src/vibesignal_ai/matching/features.py`: present

## Local Validation Results

Port note: local port `5000` is occupied by macOS Control Center, so the local backend was run on `5050`.

- `python -m py_compile $(git ls-files '*.py')`: passed
- `python -m pytest -q`: passed
- `python tools/generate_synthetic_whatsapp_fixtures.py --messages 1000 --no-api`: passed; generated `455` conversations / `1000` synthetic messages
- `VIBE_SIGNAL_API_URL=http://localhost:5050 python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/conversations.jsonl`: passed
- `python tools/analyze_cue_false_positives.py --results reports/engine_eval/synthetic_regression_results.jsonl`: passed
- `python scripts/check_public_copy_safety.py`: passed; `16` findings, `16` allowlisted, `0` unallowlisted
- `python scripts/check_no_raw_content_leaks.py`: passed; `0` findings
- `python scripts/check_vibe_restricted_artifacts.py --staged`: passed after staging verification artifacts; `6` paths checked
- `git diff --check`: passed
- blocked-phrase `git grep`: returned no matches

## Local Synthetic API Regression

- Synthetic API regression: `455/455`
- Cue contract pass rate: `455/455`
- Evidence completeness: `455/455`
- Unsafe-output block rate: `455/455`
- Low-signal fallback correctness: `455/455`
- API transport failures: `0`
- Missing expected cue count: `0`
- Unexpected cue count: `0`

## False-Positive Analysis Summary

- Result rows: `455`
- Top missing expected cues: none
- Top unexpected cues: none
- Low-signal failures: `0`
- Evidence missing cases: `0`
- Unsafe-output hits: `0`

## Deployed Backend Verification

- `https://vibe-signal.onrender.com/healthz`: HTTP `200`; body reported `{"status":"ok","service":"vibe-signal-backend"}`
- `https://vibe-signal.onrender.com/api/status`: HTTP `200`; body reported service `vibe-signal-backend`, version `0.1.0`, environment `production`, and disabled raw-message persistence, raw-message logging, analytics tracking, and training.
- Deployed version confidence: `unverified`
- Reason: `/api/status` does not expose a commit SHA or deploy identifier that can be compared to local main commit `8b13108e23a4b2cf9dd2d33a5df7074b63059f73`.

## Deployed Sample

The deployed sample was run as a bounded, version-unverified sample only:

- Command: `VIBE_SIGNAL_API_URL=https://vibe-signal.onrender.com python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/conversations.jsonl --limit 100 --engine-report-dir reports/engine_eval/deployed_postmerge_unverified`
- Evaluated synthetic conversations: `100`
- Synthetic API regression: `100/100`
- API transport failures: `0`
- Evidence missing cases: `0`
- Unsafe-output hits: `0`
- Low-signal failures: `0`
- Missing expected cues: none
- Unexpected cues: none

Because the deployed commit is unverified, this sample is not proof that production is on PR #22/main.

## Human-Reviewed Status

- Human-reviewed labels: not human-reviewed
- Current reviewed-label comparison remains bootstrap-only.
- Human review is still required before any accuracy, quality, or validation claim.

## Next Step

Run the deployed sample again after Render exposes a comparable commit/deploy identifier or after Keith confirms the deployed backend was redeployed from `8b13108e23a4b2cf9dd2d33a5df7074b63059f73`. After that, start the 10k hard-negative eval sprint.
