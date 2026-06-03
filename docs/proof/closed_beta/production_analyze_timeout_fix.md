# Production Analyze Timeout Fix

Date: 2026-06-03.

Branch: `codex/fix-production-analyze-timeout`.

## Finding

The hosted web app was already built with `VITE_API_BASE_URL=https://vibe-signal.onrender.com`, and the Render backend already accepted the Vercel origin for `/api/analyze`. The production failure came from client-side timeout handling:

- old browser timeout: 15 seconds
- old retry count: zero
- old timeout copy: pointed users toward backend URL and CORS configuration

That path is too brittle for a Render service that may need to wake before handling the first browser request.

## Fix

- Web API timeout increased to 30 seconds.
- One retry added for timeout or network/CORS-shaped fetch failures only.
- HTTP validation and backend responses are not retried.
- `VITE_API_BASE_URL` now takes precedence over legacy web aliases.
- User-facing error copy is safe and does not include raw transport details.
- The analyze form shows `The backend may be waking up. Trying once more...` during the bounded retry.

No cue logic, evaluation reports, model behavior, datasets, analytics SDKs, raw-message logging, consent gate, or safety blockers were changed.

## Production Smoke

Command:

```bash
python scripts/smoke_test_production_analyze.py --base-url https://vibe-signal.onrender.com
```

Result:

```text
[PASS] GET /healthz status=200 request_id=req_6da716beef294a768c51b603d7568a72 detail=ok
[PASS] GET /api/status status=200 request_id=req_dd0586fe4f8c42b09a5bd1a1f8a694be detail=ok
[PASS] POST /api/analyze status=200 request_id=req_5473ded347774424931f79061b8075dc detail=ok
Summary: 3/3 production analyze smoke checks passed.
```

Final post-staging run:

```text
[PASS] GET /healthz status=200 request_id=req_05ad48da9d0f4761bb7bf73e02c458c8 detail=ok
[PASS] GET /api/status status=200 request_id=req_37927d5507324122b838cd4846f3c71a detail=ok
[PASS] POST /api/analyze status=200 request_id=req_751f5deb0e064f22aa02fec53ec2f5db detail=ok
Summary: 3/3 production analyze smoke checks passed.
```

The smoke check uses only this synthetic text:

```text
self: Are we still on for Friday?
other: maybe later, not sure yet
```

The script output is metadata-only and does not print request bodies or response bodies.

## Deployed Backend Metadata

`GET /api/status` on `https://vibe-signal.onrender.com` returned:

- `environment=production`
- `git_commit=b5b4606c9d4842121046c1c3644941fa6ae115fa`
- `service_revision=vibe-signal`
- raw message persistence/logging disabled
- analytics/training disabled

`deploy_version` and `build_timestamp` were `unknown`, so those optional metadata env vars are not currently verified in the deployed backend response.

## Required Settings

Vercel:

```text
VITE_API_BASE_URL=https://vibe-signal.onrender.com
```

Render:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app
```

Optional Render metadata:

```text
GIT_COMMIT
DEPLOY_VERSION
BUILD_TIMESTAMP
SERVICE_REVISION
```

## Validation Recorded

- `cd web && npm test`: pass, 22 tests
- `cd web && npm run build`: pass
- `python -m py_compile $(git ls-files '*.py')`: pass
- `python -m pytest -q`: pass
- `python scripts/check_public_copy_safety.py`: pass, 23 allowlisted findings and 0 unallowlisted
- `python scripts/check_no_raw_content_leaks.py`: pass, 0 findings
- `python scripts/check_vibe_restricted_artifacts.py --staged`: pass, 10 staged paths checked
- `git diff --check && git diff --cached --check`: pass
- static grep for restricted claim phrases: hits are safety registries, tests, red-line docs, existing boundary copy, and synthetic review metadata
- local browser Evidence flow against `http://127.0.0.1:5050`: pass, rendered 5 observable cues
- production analyze smoke against Render: pass, 3/3

## Manual Deployment Steps

1. Deploy the merged web changes to Vercel.
2. Confirm the Vercel production env var above is present, then rebuild if it changed.
3. Confirm the Render CORS value includes the Vercel origin.
4. Re-run the production analyze smoke command.
5. Re-test the hosted web synthetic Evidence flow and the Pattern flow.
