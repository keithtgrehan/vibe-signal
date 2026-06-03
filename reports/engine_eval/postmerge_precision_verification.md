# Post-Merge Engine Precision Verification

Status: verification-only report for updated `main` after PRs #22, #23, and #24. These are bootstrap-only synthetic regression results, not accuracy, model-quality, validation, production-readiness, cheating-detection, hidden-intent, attraction, deception-certainty, diagnosis, or therapy-support claims.

## Branch And Merge State

- Verification branch: `codex/postmerge-engine-verification-main`
- Local main commit verified: `f7bf447b42061f4e5667ff5f7a26ffffd88fc319`
- Latest observed merge commits:
  - `f7bf447` - Verify post-merge engine precision baseline (#24)
  - `22aa560` - Polish trust-first UI and synthetic demo flow (#23)
  - `8b13108` - Tighten synthetic cue precision regression (#22)
  - `ed583a8` - Add engine API regression and label seed workflow (#21)
  - `c5e27cb` - Harden closed-beta RC safety gates (#20)

## Artifact Presence Checked

- PR #22 engine precision artifacts: present
  - `reports/engine_eval/synthetic_regression_report.md`
  - `tools/run_synthetic_fixture_regression.py`
  - targeted cue precision tests
  - updated cue taxonomy/config/code paths
- PR #23 UI trust/demo artifacts: present
  - `docs/design/ui_style_notes.md`
  - `web/src/trustContent.js`
  - `mobile/tests/uiTrustDemo.test.js`
- PR #24 prior verification artifacts: present
  - `reports/engine_eval/postmerge_precision_verification.md`
  - `reports/engine_eval/deployed_postmerge_unverified/`

## Local Validation Results

Port note: local port `5000` is occupied by macOS Control Center, so the local backend was run on `5050`.

- `python -m py_compile $(git ls-files '*.py')`: passed
- `python -m pytest -q`: passed
- `python tools/generate_synthetic_whatsapp_fixtures.py --messages 1000 --no-api`: passed; generated `455` conversations / `1000` synthetic messages
- `VIBE_SIGNAL_API_URL=http://localhost:5050 python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/conversations.jsonl`: passed
- `python tools/analyze_cue_false_positives.py --results reports/engine_eval/synthetic_regression_results.jsonl`: passed
- `python scripts/check_public_copy_safety.py`: passed; `16` findings, `16` allowlisted, `0` unallowlisted
- `python scripts/check_no_raw_content_leaks.py`: passed; `0` findings
- `python scripts/check_vibe_restricted_artifacts.py --staged`: passed after staging report artifacts; `11` paths checked
- `git diff --check`: passed
- blocked-phrase `git grep`: returned expected safety-context matches, summarized below

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

## Blocked Phrase Grep Summary

The required blocked-phrase grep returned `694` matches. Review summary:

- `configs`: `3`
- `data`: `505`
- `docs`: `50`
- `mobile`: `34`
- `reports`: `2`
- `scripts`: `18`
- `src`: `25`
- `tests`: `37`
- `tools`: `5`
- `web`: `15`

Observed matches are in safety policies, blocked-copy tests/registries, guardrail code, synthetic review metadata, and copy that explicitly states what Vibe Signal cannot infer. The public-copy scanner found `0` unallowlisted public-copy findings, so no unsafe public/user-facing claim was identified in this verification pass.

## Deployed Backend Verification

- `https://vibe-signal.onrender.com/healthz`: HTTP `200`; body reported `{"status":"ok","service":"vibe-signal-backend"}`
- `https://vibe-signal.onrender.com/api/status`: HTTP `200`; body reported service `vibe-signal-backend`, version `0.1.0`, environment `production`, and disabled raw-message persistence, raw-message logging, analytics tracking, and training.
- Deployed version confidence: `unverified`
- Reason: `/api/status` does not expose a commit SHA or deploy identifier that can be compared to local main commit `f7bf447b42061f4e5667ff5f7a26ffffd88fc319`.

## Deployed Sample

The deployed sample was run as bounded, version-unverified evidence only.

Initial run:

- Command: `VIBE_SIGNAL_API_URL=https://vibe-signal.onrender.com python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/conversations.jsonl --limit 100 --engine-report-dir reports/engine_eval/deployed_main_unverified`
- Evaluated synthetic conversations: `100`
- Synthetic API regression: `99/100`
- API transport failures: `1`
- Failed fixture: `synthetic_whatsapp_00001`, category `happy`, error `api_request_failed`
- Evidence missing cases: `0`
- Unsafe-output hits: `0`
- Low-signal failures: `0`

Warm retry:

- Command: `VIBE_SIGNAL_API_URL=https://vibe-signal.onrender.com python tools/run_synthetic_fixture_regression.py --input data/synthetic/whatsapp/conversations.jsonl --limit 100 --engine-report-dir reports/engine_eval/deployed_main_unverified_warm_retry`
- Evaluated synthetic conversations: `100`
- Synthetic API regression: `100/100`
- API transport failures: `0`
- Evidence missing cases: `0`
- Unsafe-output hits: `0`
- Low-signal failures: `0`
- Missing expected cues: none
- Unexpected cues: none

Because the deployed commit is unverified, these samples are not proof that production is on PR #22/#23/#24 main.

## Human-Reviewed Status

- Human-reviewed labels: not human-reviewed
- Current reviewed-label comparison remains bootstrap-only.
- Human review is still required before any accuracy, quality, validation, or production-readiness claim.

## Next Step Recommendation

1. Expose a comparable commit or deploy identifier in `/api/status`, then redeploy main to Render.
2. Rerun the bounded deployed sample after redeploy or after commit identity can be verified.
3. Start the 10k hard-negative eval sprint only after deployed version confidence is current.
