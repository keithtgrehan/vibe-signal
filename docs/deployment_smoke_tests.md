# Deployment Smoke Tests

Status: closed-beta deployment verification scaffold only. These smoke tests prove backend connectivity and response-shape expectations for a specific host. They do not prove production compliance, legal readiness, model quality, mobile App Store readiness, monitoring completeness, or commercial data-rights readiness.

## What The Script Checks

Run `scripts/smoke_test_deployed_backend.py` against a local or deployed backend base URL. The script checks:

- `GET /healthz`
- `GET /readyz`
- `GET /legal/privacy`
- `GET /legal/terms`
- `GET /legal/data-deletion`
- `GET /legal/data-export`
- `GET /legal/match-disclaimer`
- `POST /api/match`

The `/api/match` check uses only a synthetic toy exchange:

- `self: Can you confirm Tuesday at 10am?`
- `other: Yes, Tuesday at 10am works. No pressure if we need to adjust.`

The script prints only safe status summaries: method, endpoint, HTTP status, request-ID presence, and coarse validation detail. It does not print request bodies, response bodies, raw chat text, provider responses, secrets, headers, cookies, vectors, model artifacts, or credentials.

When mobile event ingestion is in scope for the deploy, include bounded metadata event routes:

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://<your-backend-host> --include-events
```

This adds:

- `POST /api/events/analysis`
- `POST /api/events/quota`
- `POST /api/events/billing`
- `POST /api/events/state`

## Local Backend Smoke Test

From the repo root, start the backend with access logs disabled:

```bash
PYTHONPATH=src python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 --no-access-log
```

In another terminal:

```bash
python scripts/smoke_test_deployed_backend.py --base-url http://127.0.0.1:8000
```

Expected shape:

```text
[PASS] GET /healthz status=200 request_id=yes detail=ok
[PASS] GET /readyz status=200 request_id=yes detail=ok
[PASS] GET /legal/privacy status=200 request_id=yes detail=ok
[PASS] GET /legal/terms status=200 request_id=yes detail=ok
[PASS] GET /legal/data-deletion status=200 request_id=yes detail=ok
[PASS] GET /legal/data-export status=200 request_id=yes detail=ok
[PASS] GET /legal/match-disclaimer status=200 request_id=yes detail=ok
[PASS] POST /api/match status=200 request_id=yes detail=ok
Summary: 8/8 deployment smoke checks passed.
```

## Deployed Backend Smoke Test

Use the deployed backend base URL only. Do not include a route path, query string, fragment, username, password, token, or real credential in the URL.

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://<your-backend-host>
```

Before beta traffic, also verify that server, proxy, and platform access logs are disabled or sanitized. The backend safe request logger is metadata-only, but default platform access logs may include raw request lines unless configured.

## Mobile URL Verification

After the backend smoke test passes, set the mobile app backend base URL:

```bash
cd mobile
EXPO_PUBLIC_API_URL=https://<your-backend-host> npm start
```

For physical device testing against a local backend, use your machine LAN address instead of `127.0.0.1`:

```bash
cd mobile
EXPO_PUBLIC_API_URL=http://<your-machine-lan-ip>:8000 npm start
```

Native iOS and Android requests are not controlled by browser CORS. Expo web, browser-based testing, or future web/admin surfaces require exact origins in `VIBE_BACKEND_ALLOWED_ORIGINS`; do not use wildcard origins.

Optional mobile event acceptance check:

```bash
cd mobile
npm run verify:backend -- --api-url https://<your-backend-host> --event state
```

The mobile verifier prints generated event payload and response text for operator inspection. Use it only with the built-in synthetic event payloads and a clean base URL. Do not paste private text, credentials, tokens, route paths, query strings, or fragments into the URL.

Use `--all` only when the deployed event routes are intentionally in scope for that verification pass:

```bash
cd mobile
npm run verify:backend -- --api-url https://<your-backend-host> --all
```

## Failure Triage

- `invalid base url`: pass only a base `http://` or `https://` URL with no credentials, path, query string, or fragment.
- `unexpected_status`: confirm the host is deployed, the route exists, and no gateway/auth layer is blocking the route.
- `empty_json_body` or `invalid_json_body`: confirm the request reaches the FastAPI backend and not a static hosting error page.
- `readyz_status_not_ready`: inspect `/readyz` for hard safety flags and route registration.
- `readyz_unsafe_flag_enabled`: stop beta traffic until raw persistence/logging, analytics/tracking, or training flags are disabled.
- `legal_*`: confirm PR #7 legal draft routes are deployed.
- `match_*`: confirm PR #5 matching contracts and PR #8/#9 backend hardening are deployed.

Do not paste private chats, provider responses, credentials, or sensitive user data into smoke tests or incident notes. Use request IDs, endpoint names, status codes, and coarse failure categories for triage.

## What This Does Not Prove

- legal compliance
- GDPR/CCPA readiness
- model quality
- commercial training rights
- production monitoring completeness
- deletion/export workflow readiness
- mobile runtime behavior on a real device
- App Store/TestFlight readiness
