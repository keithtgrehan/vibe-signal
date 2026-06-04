# Render Deploy Metadata

Status: deploy-version proof is available only when Render exposes safe metadata through `GET /api/status`.

Current known `origin/main` SHA before this release-gate branch:

```text
b5b4606c9d4842121046c1c3644941fa6ae115fa
```

When deploying a new merged release-candidate commit, replace `GIT_COMMIT` with the final main commit SHA intended for Render.

## Render Environment Variables

Set these as non-secret Render environment variables for the backend service:

```text
GIT_COMMIT=b5b4606c9d4842121046c1c3644941fa6ae115fa
DEPLOY_VERSION=main-20260603-2106
BUILD_TIMESTAMP=2026-06-03T21:06:52Z
SERVICE_REVISION=render-closed-beta-rc
```

If Render supplies `RENDER_GIT_COMMIT`, the backend also accepts it as a fallback for `git_commit`. Do not set or expose secrets, API keys, internal URLs, local paths, usernames, tokens, request bodies, or raw environment dumps.

## Verification Commands

```bash
python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com
python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com --expected-git-commit b5b4606c9d4842121046c1c3644941fa6ae115fa
```

Expected statuses:

- `current`: `/healthz` and `/api/status` respond, and `git_commit` matches the expected SHA.
- `stale`: `/api/status.git_commit` is present but does not match the expected SHA.
- `unverified`: metadata is missing, endpoint is unavailable, or no expected SHA was supplied.

Missing metadata is not a product failure. It means deployed-version proof is incomplete until Render env vars are configured and the service is redeployed.

