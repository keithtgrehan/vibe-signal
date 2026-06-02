# Backend Deployment Readiness

Status: deployment-readiness scaffold only. This document does not claim production compliance, legal compliance, security certification, GDPR completion, or public-launch readiness.

## Implemented Backend Surface

- `GET /healthz`: minimal liveness check.
- `GET /readyz`: readiness metadata for route registration, CORS count, and hard safety flags.
- Backend request logging emits metadata-only operational events with request IDs, endpoint path, status code, status category, latency bucket, and coarse error category.
- `POST /api/analyze`: deterministic local cue evidence, no raw message persistence by default.
- `POST /api/match`: deterministic communication-fit matching, no raw message persistence by default.
- `POST /api/feedback`: requires explicit consent and stores metadata only by default.
- `POST /api/events/*`: accepts bounded event metadata only.
- `GET /legal/*`: static draft legal/readiness copy, not a complete legal workflow.

## Local Run

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Check liveness and readiness:

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
```

## Deployment Command Shape

Use the platform-provided port when available:

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port "${PORT:-8000}"
```

This repo does not commit a provider-specific deployment target, hostname, `.replit`, Dockerfile, Procfile, or secret-bearing config.

## Backend Environment Variables

See [backend/deployment.env.example](../backend/deployment.env.example).

| Variable | Purpose | Safe default |
| --- | --- | --- |
| `VIBE_BACKEND_ENV` | Labels `/readyz` as `local`, `staging`, or `production`. | `local` |
| `VIBE_BACKEND_VERSION` | Release/version label surfaced by `/readyz`. | `0.1.0` |
| `VIBE_BACKEND_ALLOWED_ORIGINS` | Comma-separated exact browser origins for CORS. | unset / no CORS middleware |
| `VIBE_BACKEND_LOG_LEVEL` | Logging level label for deployment config. | `INFO` |

Unsupported environment labels default to `local` and appear as a `/readyz` config warning. Unsupported log levels default to `INFO`.

Unsafe or unsupported CORS values are rejected from the parsed config:

- wildcard origins such as `*`
- non-HTTP(S) origins
- origins that include paths, query strings, or fragments

`/readyz` reports only the count of accepted CORS origins. It does not echo origin values or other environment variable values.

## Mobile And CORS Notes

Set the mobile app backend base URL with:

```bash
EXPO_PUBLIC_API_URL=https://<your-backend-host>
```

Native iOS/Android requests are not governed by browser CORS. Expo web, browser-based testing, or future web/admin surfaces do require CORS, so set `VIBE_BACKEND_ALLOWED_ORIGINS` to exact deployed origins when those surfaces are used.

Do not hardcode a production host into source. Keep `EXPO_PUBLIC_API_URL` environment-driven for local, staging, and production builds.

## Safe Logging Guidance

Deployment logs must stay metadata-only. See [monitoring and no-raw-log readiness](monitoring_no_raw_logs.md) for the closed-beta monitoring checklist and incident-response triggers.

Do not log:

- raw chat text
- request bodies for `/api/analyze` or `/api/match`
- provider responses
- API keys, bearer tokens, secrets, or credentials
- private support messages
- model vectors, embeddings, checkpoints, or generated artifacts

Allowed operational log examples:

- route name
- status code
- request duration
- request ID
- deployment environment label
- bounded error category
- latency bucket
- explicit false flags for raw body, raw message, provider response, and secret logging

This PR does not add analytics, tracking, account storage, raw message persistence, training, embeddings, datasets, model files, vectors, checkpoints, cached artifacts, or provider calls.

## Deployment Checklist

Before deploying:

- Confirm the branch is based on reviewed `main`.
- Run `python -m py_compile $(git ls-files '*.py')`.
- Run `python -m pytest -q`.
- Run `git diff --check`.
- Run `python scripts/check_vibe_restricted_artifacts.py --staged`.
- Confirm no secrets, raw chats, external datasets, provider responses, model binaries, vectors, checkpoints, or cached embeddings are staged.
- Set `VIBE_BACKEND_ENV`, `VIBE_BACKEND_VERSION`, and any exact `VIBE_BACKEND_ALLOWED_ORIGINS`.
- Set the mobile build/runtime `EXPO_PUBLIC_API_URL` to the deployed backend base URL.
- Keep `EXPO_PUBLIC_ENABLE_LOGGING` disabled unless bounded event metadata ingestion has been reviewed for that environment.

After deploying:

- Check `GET /healthz`.
- Check `GET /readyz`.
- Check `GET /legal/match-disclaimer`.
- Send one synthetic `/api/match` request; do not use private chats for smoke tests.
- Run `cd mobile && npm run verify:backend -- --api-url https://<your-backend-host> --event state` if event routes are in scope.
- Confirm logs do not contain raw message text, secrets, provider responses, or request bodies.

## Remaining Launch Blockers

- Final reviewed privacy, terms, deletion, and export URLs.
- Legal-reviewed deletion/export support flow, identity checks, retention policy, and response timelines.
- Live deployment monitoring and incident-response process.
- Real reviewed labels before public model-quality claims.
- Commercial-safe training rights before any commercial training use.
- App Store/TestFlight or production-device verification for mobile builds.
