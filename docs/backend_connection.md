# Backend Connection

VibeSignal uses a FastAPI backend. The current reviewed backend deployment is Render:

- `https://vibe-signal.onrender.com`

The mobile app will **not** send match requests, telemetry, or backend-bound verification requests unless `EXPO_PUBLIC_API_URL` is set to a reachable backend base URL. The standalone `web/` Vite frontend defaults to the Render backend, and can be pointed at another reviewed backend with `VITE_API_BASE_URL`, `VITE_API_URL`, or `EXPO_PUBLIC_API_URL`.

## What Is Already Wired

The mobile and web clients expect these routes under the configured base URL:

- `/healthz`
- `/readyz`
- `/api/match`
- `/api/analyze`
- `/api/feedback`
- `/legal/{slug}`
- `/api/events/analysis`
- `/api/events/quota`
- `/api/events/billing`
- `/api/events/state`

## Backend URL Shapes

Set `EXPO_PUBLIC_API_URL` to the backend base URL, not a route path:

- local simulator or same-machine development: `http://127.0.0.1:8000`
- Android emulator against a local backend: `http://10.0.2.2:8000`
- physical phone against a local backend: `http://<your-machine-lan-ip>:8000`
- current deployed Render backend: `https://vibe-signal.onrender.com`
- future reviewed backend: `https://<your-backend-host>`

Do not include a route path, query string, fragment, username, password, token, or credential in `EXPO_PUBLIC_API_URL`.

For the standalone web frontend, set the same backend base URL with:

```bash
VITE_API_BASE_URL=https://vibe-signal.onrender.com npm run dev
```

The Vite app also supports `VITE_API_URL` and `EXPO_PUBLIC_API_URL` for local preview parity, but `VITE_API_BASE_URL` is the clearest hosted-web name.

## CORS And Mobile URL Configuration

Native iOS and Android requests are not controlled by browser CORS. Expo web, browser-based testing, or future web/admin surfaces do need CORS. Configure exact allowed browser origins on the backend with:

- hosted web plus local QA:
  - `VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,http://localhost:19006,http://localhost:8081,http://localhost:5173`
- future hosted frontend examples:
  - `VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,https://app.example.com,https://admin.example.com`

Do not use wildcard origins in production-facing environments. The backend config parser rejects `*`, non-HTTP(S) origins, and origins with paths, query strings, or fragments.

The `web/` frontend can be hosted separately later. When that happens, add the exact hosted frontend origin to `VIBE_BACKEND_ALLOWED_ORIGINS`; do not broaden CORS to cover arbitrary origins.

See [backend deployment readiness](backend_deployment_readiness.md) for the deployment checklist and logging boundaries.

## Current Render Backend

The Render backend deployment remains the source of truth for backend QA. For hosted web and local browser QA, configure this exact Render environment value:

- `VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,http://localhost:19006,http://localhost:8081,http://localhost:5173`

The backend deploy itself does not need code changes for these frontend clients.

## How To Verify Connectivity

Full backend host smoke test from the repo root:

- `python scripts/smoke_test_deployed_backend.py --base-url https://<your-backend-host>`

Single route:

- `npm run verify:backend -- --api-url https://<your-backend-host> --event state`

All event routes:

- `npm run verify:backend -- --api-url https://<your-backend-host> --all`

Expected behavior:

- the command prints the request target and structured result
- each event route returns a success status if the backend accepts the payload
- failures are printed explicitly and do not fail silently

Backend liveness/readiness checks:

- `curl https://<your-backend-host>/healthz`
- `curl https://<your-backend-host>/readyz`

The Python smoke test checks liveness, readiness, static legal draft routes, and `/api/match` with synthetic toy messages. The mobile verifier checks event-route acceptance only.

## Device QA Notes

The standalone verifier needs only `--api-url` or `EXPO_PUBLIC_API_URL`.

The in-app mobile event pipeline needs both:

- `EXPO_PUBLIC_API_URL`
- `EXPO_PUBLIC_ENABLE_LOGGING`

The `/api/match` mobile flow needs `EXPO_PUBLIC_API_URL` but does not require `EXPO_PUBLIC_ENABLE_LOGGING`.

## If `EXPO_PUBLIC_API_URL` Is Missing

Current safe behavior:

- mobile logging becomes a no-op
- the backend verification helper returns `missing_api_url`
- no requests are attempted

## What This Does Not Prove

These checks confirm payload acceptance only. They do not prove:

- App Store purchase success
- RevenueCat entitlement correctness
- dashboard/admin rendering
- anomaly detection quality
- production compliance
- final privacy, terms, deletion, or export readiness
