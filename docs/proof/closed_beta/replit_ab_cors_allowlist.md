# Replit A/B CORS Allowlist

## Purpose

The Replit A/B frontend at `https://vibe-signal-ab.replit.app` is a draft-only experiment that needs browser access to the existing Render backend at `https://vibe-signal.onrender.com`.

The deployed backend already supports exact CORS origins through `VIBE_BACKEND_ALLOWED_ORIGINS`. This change documents the exact Render environment update and verifies the backend continues to allow only explicitly configured origins.

## Exact Allowed Origin

Add this exact origin to the Render backend environment:

```text
https://vibe-signal-ab.replit.app
```

Keep the production Vercel origin:

```text
https://vibe-signal.vercel.app
```

Expected Render value:

```text
VIBE_BACKEND_ALLOWED_ORIGINS=https://vibe-signal.vercel.app,https://vibe-signal-ab.replit.app
```

Local browser QA origins may remain in non-production examples as needed.

## Safety Boundaries

- No wildcard CORS.
- No `allow all origins` setting.
- No broad `.replit.app` or `.replit.dev` pattern.
- No backend API route or response contract changes.
- No frontend UI changes in this CORS-only branch.
- No analytics, tracking, auth, storage, n8n production wiring, or raw message logging.

## Replit Experiment Status

The Replit UI experiment remains isolated in draft PR #42. It should not be merged until A/B feedback is reviewed.

## Validation

Run:

```bash
python -m pytest tests/test_backend_deployment_readiness.py -q
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

## Render Deployment Note

After this PR is merged, Render must be updated or redeployed so the backend process has `VIBE_BACKEND_ALLOWED_ORIGINS` containing both:

```text
https://vibe-signal.vercel.app,https://vibe-signal-ab.replit.app
```

Do not remove the production Vercel origin.
