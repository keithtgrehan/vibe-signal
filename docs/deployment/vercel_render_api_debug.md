# Vercel / Render Analyze Timeout Debug

Date: 2026-06-03.

## Root Cause

The deployed Vercel bundle was pointed at the correct Render backend, and Render accepted the hosted web origin. The failure was in the browser client resilience path: production used a 15 second fetch timeout, did not retry transient wake-up or network failures, and showed timeout copy that implied a CORS/config problem.

Evidence gathered on 2026-06-03:

- Vercel served a Vite bundle containing `VITE_API_BASE_URL=https://vibe-signal.onrender.com`.
- Render `GET /healthz` returned `200`.
- Render `GET /api/status` returned `200` with `git_commit=b5b4606c9d4842121046c1c3644941fa6ae115fa`.
- Render CORS preflight for `Origin: https://vibe-signal.vercel.app` and `POST /api/analyze` returned `200` with `access-control-allow-origin: https://vibe-signal.vercel.app`.
- Direct Render `POST /api/analyze` with safe synthetic text returned `200`.

This means the observed hosted-web timeout is most consistent with Render wake-up latency exceeding the old client timeout, not an engine, payload, or CORS contract failure.

## Required Vercel Settings

Use the hosted web env var below for production Vercel builds:

```text
VITE_API_BASE_URL=https://vibe-signal.onrender.com
```

The web app still accepts `VITE_API_URL` and `EXPO_PUBLIC_API_URL` as legacy fallbacks, but `VITE_API_BASE_URL` is now the primary hosted-web setting. The value must be a clean `http(s)` origin with no route path, query string, fragment, username, password, token, or credential.

`NEXT_PUBLIC_API_URL`, `VIBE_SIGNAL_API_URL`, and `EXPO_PUBLIC_API_URL` are not the required Vercel setting for the standalone Vite web app. `EXPO_PUBLIC_API_URL` remains useful for mobile/Expo parity.

## Required Render Settings

Render must allow the exact hosted web origin:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app
```

Keep local browser origins when local browser QA is needed:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,http://localhost:5173,http://127.0.0.1:5173
```

Do not use wildcard CORS in production-facing environments. The backend should keep `allow_credentials=False` unless a future reviewed flow explicitly needs credentials.

Optional safe deploy metadata env vars:

```text
GIT_COMMIT=<safe commit sha>
DEPLOY_VERSION=<safe version label>
BUILD_TIMESTAMP=<safe timestamp label>
SERVICE_REVISION=<safe service revision label>
```

`/api/status` returns only sanitized metadata values.

## Client Behavior

The web API client now:

- resolves `VITE_API_BASE_URL` before legacy aliases
- uses a 30 second request timeout
- retries once for timeout or network/CORS-shaped fetch failures
- does not retry HTTP validation or backend responses
- reports safe classifications: `backend_waking`, `timeout`, `cors_or_network`, `backend_error`, and `validation_error`

User-facing copy:

- first retry: `The backend may be waking up. Trying once more...`
- final timeout: `The backend did not respond in time. Please try again in a moment.`
- network/CORS-shaped failure: `The app could not reach the backend. Check deployment configuration.`
- validation failure: `The request could not be analyzed. Please try the synthetic example or shorten the text.`

Raw transport details are not shown to normal users.

## How To Verify Production

Run the minimal analyze smoke check:

```bash
python scripts/smoke_test_production_analyze.py --base-url https://vibe-signal.onrender.com
```

Expected metadata-only output:

```text
[PASS] GET /healthz status=200 request_id=<safe request id> detail=ok
[PASS] GET /api/status status=200 request_id=<safe request id> detail=ok
[PASS] POST /api/analyze status=200 request_id=<safe request id> detail=ok
Summary: 3/3 production analyze smoke checks passed.
```

Manual browser check after Vercel deploy:

1. Open `https://vibe-signal.vercel.app`.
2. Open the pattern review form.
3. Use `Load synthetic text`.
4. Check the permission checkbox.
5. Run Evidence mode to exercise `/api/analyze`.
6. Confirm cue evidence renders from the backend.

## Remaining Manual Deployment Steps

1. Merge and deploy this branch to Vercel.
2. Confirm Vercel production env has `VITE_API_BASE_URL=https://vibe-signal.onrender.com`.
3. Confirm Render has `VIBE_BACKEND_ALLOWED_ORIGINS` including `https://vibe-signal.vercel.app`.
4. Re-run `python scripts/smoke_test_production_analyze.py --base-url https://vibe-signal.onrender.com`.
5. Re-test the hosted web synthetic Evidence and Pattern flows.
