# Render / Vercel Deployment Runbook

Status: operations runbook for closed-beta verification. This document does not approve public launch, legal compliance, GDPR compliance, EU AI Act compliance, App Store release, or model quality.

## Vercel deployment flow

1. Merge frontend-safe changes to `main`.
2. Let Vercel build the `web/` Vite app.
3. Verify the primary domain:

```bash
curl -I https://www.vibe-signal.com
curl -I https://vibe-signal.com
curl -I https://vibe-signal.vercel.app
```

4. Confirm the web bundle is current enough for the change under review.
5. Run local web validation before treating the deploy as reviewable:

```bash
cd web
npm test
npm run build
```

Vercel serves the public frontend. It does not run the FastAPI backend. Same-origin `https://www.vibe-signal.com/api/analyze` is expected to fail unless a future proxy/rewrite is intentionally added.

## Render deployment flow

1. Deploy the backend from latest `main` only after repo validation passes.
2. Confirm Render uses the intended branch and commit.
3. Confirm Render installs the minimal backend runtime requirements, not the full local/research requirements file:

```bash
pip install -r requirements-render.txt
```

4. Confirm Render uses the backend start command:

```bash
PYTHONPATH=src uvicorn backend.app:app --host 0.0.0.0 --port $PORT --no-access-log
```

5. Keep access logs disabled or metadata-only. Do not log request bodies.
6. Verify health and status metadata:

```bash
curl -i https://vibe-signal.onrender.com/healthz
curl -i https://vibe-signal.onrender.com/api/status
```

7. Run the bounded custom-domain smoke script:

```bash
bash scripts/prod_smoke_custom_domain.sh
```

Render runs the backend separately from Vercel. A Vercel deploy can be current while Render is stale.

See [Render Backend Runtime Requirements](render_backend_runtime_requirements.md) for the hosted backend dependency boundary.

## Required Render environment variables

Use exact origins. Do not use wildcard CORS.

```text
PYTHON_VERSION=3.11.11
VIBE_BACKEND_ENV=production
VIBE_BACKEND_ALLOWED_ORIGINS=https://www.vibe-signal.com,https://vibe-signal.com,https://vibe-signal.vercel.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:19006,http://localhost:8081
VIBE_BACKEND_LOG_LEVEL=INFO
GIT_COMMIT=<non-secret commit sha or unknown>
DEPLOY_VERSION=<non-secret deploy label or unknown>
BUILD_TIMESTAMP=<non-secret timestamp or unknown>
SERVICE_REVISION=<non-secret Render revision label or unknown>
```

Do not put secrets, tokens, credentials, request bodies, submitted text, provider responses, or dashboard URLs in these variables.

## Required Vercel environment variables

The web app defaults to the Render backend when no API override is set. Setting the override explicitly is still useful for clarity:

```text
VITE_API_BASE_URL=https://vibe-signal.onrender.com
```

Do not configure `VITE_API_BASE_URL` with a path, query string, credential, fragment, or non-HTTPS production backend URL.

## CORS failure diagnosis

Symptom: the web UI shows `The app could not reach the backend. Check deployment configuration.`

Check direct backend access:

```bash
curl -i https://vibe-signal.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Alex: Are you still up for talking tonight?\n\nSam: Maybe, I am pretty drained."}'
```

Check browser preflight from the custom domain:

```bash
curl -i -X OPTIONS https://vibe-signal.onrender.com/api/analyze \
  -H "Origin: https://www.vibe-signal.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

Expected after Render is current:

- status `200`
- `access-control-allow-origin: https://www.vibe-signal.com`

If direct POST works but OPTIONS returns `Disallowed CORS origin`, Render is missing the custom-domain CORS config or has not deployed the latest backend code.

## Stale Render diagnosis

Known stale signs:

- `https://vibe-signal.onrender.com/api/legal/privacy` returns `404`
- `https://vibe-signal.onrender.com/legal/privacy` returns `200`
- `/readyz` reports the expected route list but CORS count or status metadata does not match the current repo
- custom-domain OPTIONS preflight fails while Vercel preview origin succeeds

Stale Render does not block public legal page display because the legal pages are static-first in the web bundle. It does block reliable private custom analysis when CORS or route parity is stale.

## No-Render-minute preflight mode

Use the default smoke script mode when deciding whether private analyze is ready to trust from the custom domain:

```bash
bash scripts/prod_smoke_custom_domain.sh
```

If Render latest-main deploy is intentionally being deferred, use pending mode to separate frontend/custom-domain health from known stale backend parity:

```bash
bash scripts/prod_smoke_custom_domain.sh --allow-pending-render
```

Pending mode is still synthetic-only. It keeps web domain, backend health, backend status, and direct `/api/analyze` checks strict. It only downgrades known pending custom-domain CORS and `/api/legal/*` parity gaps to warnings so the report can be used before spending Render deployment minutes.

## Custom domain DNS notes

- Primary web app: `https://www.vibe-signal.com`
- Apex domain: `https://vibe-signal.com`, expected to redirect to `www`
- Fallback/preview: `https://vibe-signal.vercel.app`
- Backend: `https://vibe-signal.onrender.com`

Vercel owns the public web domain. Render owns the backend origin. DNS changes for the frontend do not update Render CORS automatically.

## Exact smoke commands

Use the custom-domain smoke script for a bounded synthetic check:

```bash
bash scripts/prod_smoke_custom_domain.sh
```

Equivalent manual checks:

```bash
curl -I https://www.vibe-signal.com
curl -I https://vibe-signal.com
curl -i https://vibe-signal.onrender.com/healthz
curl -i https://vibe-signal.onrender.com/api/status
curl -i -X OPTIONS https://vibe-signal.onrender.com/api/analyze \
  -H "Origin: https://www.vibe-signal.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
curl -i https://vibe-signal.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Alex: Are you still up for talking tonight?\n\nSam: Maybe, I am pretty drained."}'
curl -i https://vibe-signal.onrender.com/legal/privacy
curl -i https://vibe-signal.onrender.com/api/legal/privacy
```

`/api/legal/privacy` may fail until Render deploys latest main. Frontend legal pages are static-first and should still render complete draft legal text from Vercel.

## Known symptoms and fixes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Legal page shows a fallback warning | Old frontend bundle | Deploy latest Vercel build; legal pages should now render from bundled content. |
| Custom analyze shows backend connectivity copy | Render CORS rejects the custom domain or backend is unavailable | Verify OPTIONS preflight and Render env vars, then redeploy Render when ready. |
| `/api/legal/privacy` returns 404 but `/legal/privacy` returns 200 | Stale Render backend | No frontend emergency; deploy Render latest main before backend parity verification. |
| `https://www.vibe-signal.com/api/analyze` returns 404 | No Vercel API proxy configured | Expected unless a future proxy is intentionally added. Frontend should call Render directly. |
| Synthetic demo works while private analyze fails | Backend/CORS issue | Synthetic demo is local; diagnose Render health, status, and CORS. |

## Safe operating rules

- Use synthetic smoke text only.
- Do not paste personal message content into shell commands, issues, PRs, screenshots, logs, or docs.
- Do not add analytics, cookies, tracking, storage, providers, account systems, or payment systems while debugging deploy plumbing.
- Keep legal pages marked `draft_requires_legal_review`.
- Do not claim legal approval, public-launch approval, real-world accuracy, or model quality from these checks.
