# Hosted Web Deployment

The backend remains the Render/FastAPI service. The browser frontend is a separate Vercel/Vite app under `web/`.

## Current Hosts

| Component | URL |
| --- | --- |
| Render backend | `https://vibe-signal.onrender.com` |
| Vercel web frontend | `https://vibe-signal.vercel.app` |

## Vercel Settings

| Setting | Value |
| --- | --- |
| Root directory | `web` |
| Framework | Vite |
| Build command | `npm run build` |
| Output directory | `dist` |
| Backend env var | `VITE_API_BASE_URL=https://vibe-signal.onrender.com` |

`VITE_API_URL` is also supported for backwards compatibility, but `VITE_API_BASE_URL` is the preferred hosted-web variable. Values must be clean `http(s)` origins with no path, query, fragment, username, password, token, or credential.

## Render CORS

Configure exact browser origins in Render:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,http://localhost:19006,http://localhost:8081,http://localhost:5173
```

Do not use wildcard origins. The backend parser rejects `*`, non-HTTP(S) origins, and origins with paths, query strings, or fragments.

When a future web host is added, append that exact origin only:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,https://future-reviewed-web.example
```

## Smoke Tests

From the repo root:

```bash
export VIBE_BACKEND_HOST="https://vibe-signal.onrender.com"
python scripts/smoke_test_deployed_backend.py --base-url "$VIBE_BACKEND_HOST"
python scripts/smoke_test_deployed_backend.py --base-url "$VIBE_BACKEND_HOST" --include-events
curl -i -X OPTIONS "https://vibe-signal.onrender.com/api/match" \
  -H "Origin: https://vibe-signal.vercel.app" \
  -H "Access-Control-Request-Method: POST"
```

From `web/`:

```bash
npm install
VITE_API_BASE_URL=https://vibe-signal.onrender.com npm run build
VITE_API_BASE_URL=https://vibe-signal.onrender.com npm run dev
```

Use only synthetic or permissioned text for manual browser checks.

## Rollback

1. Disable tester invites.
2. Revert the Vercel deployment to the previous known-good frontend deployment.
3. If backend behavior regressed, redeploy the previous Render backend commit.
4. Re-run backend smoke, event smoke, CORS preflight, legal-route checks, and hosted-web synthetic `/api/match` before resuming.

## Limits

- Hosted web deployment does not prove production readiness.
- Hosted web deployment does not prove legal/GDPR compliance.
- Synthetic `/api/match` success does not prove model quality.
- No analytics/tracking, raw message persistence, old Replit backend/admin/database logic, external datasets, embeddings, vectors, checkpoints, or model files are part of this frontend deployment.
