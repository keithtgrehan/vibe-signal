# Validation Results - 2026-06-03

Status: `COMPLETE_WITH_DEPLOYED_BACKEND_REDEPLOY_BLOCKER`.

This file is updated during the RC hardening run. Final validation results are reported in the PR body and final Codex handoff.

## Completed During Focused Hardening

| Command | Result |
| --- | --- |
| `python -m py_compile $(git ls-files '*.py')` | PASS |
| `python -m pytest -q` | PASS |
| `python tools/validate_training_sources.py configs/vibe_training_sources.example.yml` | PASS |
| `python scripts/check_vibe_restricted_artifacts.py --staged` | PASS |
| `python tools/check_restricted_artifacts.py --dry-run` | PASS |
| `python scripts/check_public_copy_safety.py` | PASS |
| `python scripts/check_no_raw_content_leaks.py` | PASS |
| `python tools/generate_synthetic_whatsapp_fixtures.py --messages 1000 --no-api` | PASS: 1,000 messages, 455 conversations, 455/455 evaluations |
| `python -m pytest -q tests/test_low_signal_fallback.py tests/test_blocked_inference_requests.py tests/test_nlp_cue_contracts.py tests/test_synthetic_fixture_regression.py tests/test_synthetic_whatsapp_harness.py tests/test_public_copy_safety.py tests/test_no_raw_content_leaks.py tests/test_backend_feedback_consent.py tests/test_redline_output_blocker.py` | PASS |
| `python scripts/validate_vibe_training_sources.py --config configs/vibe_training_sources.example.yml --project-mode research_only` | PASS |
| `python scripts/validate_vibe_training_sources.py --config configs/vibe_training_sources.example.yml --project-mode commercial` | EXPECTED FAIL-CLOSED |
| `cd web && npm test` | PASS |
| `cd web && npm run build` | PASS |
| `cd mobile && npm test` | PASS: 130/130 |
| `cd mobile && npx expo config --type public` | PASS |
| `git diff --check` | PASS |
| `PYENV_VERSION=3.11.3 python scripts/smoke_test_deployed_backend.py --base-url https://vibe-signal.onrender.com --retries 3 --retry-delay-seconds 2` | PARTIAL: 9/10, `/api/feedback` returned `feedback_comment_hash_returned` |
| `PYENV_VERSION=3.11.3 python scripts/smoke_test_deployed_backend.py --base-url https://vibe-signal.onrender.com --include-events --retries 3 --retry-delay-seconds 2` | PARTIAL: 13/14, same `/api/feedback` failure |
| Vercel-origin CORS preflight for `/api/match` | PASS: `HTTP/2 200`, `access-control-allow-origin: https://vibe-signal.vercel.app` |

## Skipped

- Web lint/typecheck: no package scripts are defined.
- Mobile lint/typecheck: no package scripts are defined.
- EAS build/TestFlight upload: credentials and physical-device QA are not available in this run.
