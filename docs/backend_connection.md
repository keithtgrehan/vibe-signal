# Backend Connection

VibeSignal mobile does not connect to a backend automatically. The app will **not** send telemetry or backend-bound verification requests unless `EXPO_PUBLIC_API_URL` is set to a reachable deployed base URL.

## What Is Already Wired

The mobile app is environment-driven and expects these routes under the configured base URL:

- `/healthz`
- `/readyz`
- `/api/match`
- `/api/events/analysis`
- `/api/events/quota`
- `/api/events/billing`
- `/api/events/state`

## How To Obtain The Deployed Replit URL

This repo does not contain a committed `.replit` file, `replit.nix`, or a hardcoded deployment hostname.

To get the correct live URL:

1. Open the actual Replit deployment/project settings for VibeSignal.
2. Copy the deployed public backend base URL.
3. Set that exact value in:
   - `EXPO_PUBLIC_API_URL`

Do not guess the hostname and do not infer it from the Replit workspace slug alone.

## CORS And Mobile URL Configuration

Set `EXPO_PUBLIC_API_URL` to the deployed backend base URL, not a route path.

Native iOS and Android requests are not controlled by browser CORS. Expo web, browser-based testing, or future web/admin surfaces do need CORS. Configure exact allowed browser origins on the backend with:

- `VIBE_BACKEND_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com`

Do not use wildcard origins in production-facing environments. The backend config parser rejects `*`, non-HTTP(S) origins, and origins with paths, query strings, or fragments.

See [backend deployment readiness](backend_deployment_readiness.md) for the deployment checklist and logging boundaries.

## How To Verify Connectivity

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
