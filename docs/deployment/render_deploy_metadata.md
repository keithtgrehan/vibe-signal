# Render Deploy Metadata

Status: deploy-version proof is available only when Render exposes safe metadata through `GET /api/status`.

When deploying a new merged release-candidate commit, set `GIT_COMMIT` to the final main commit SHA intended for Render. The production smoke and closed-beta gate wrappers default to the local `git rev-parse HEAD` value as the expected commit when run inside a git checkout.

## Render Environment Variables

Set these as non-secret Render environment variables for the backend service:

```text
GIT_COMMIT=<expected-main-sha>
DEPLOY_VERSION=main-20260603-2106
BUILD_TIMESTAMP=2026-06-03T21:06:52Z
SERVICE_REVISION=render-closed-beta-rc
```

If Render supplies `RENDER_GIT_COMMIT`, the backend also accepts it as a fallback for `git_commit`. Do not set or expose secrets, API keys, internal URLs, local paths, usernames, tokens, request bodies, or raw environment dumps.

## Verification Commands

```bash
python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com
python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com --expected-git-commit "$(git rev-parse HEAD)"
bash scripts/prod_smoke_all.sh https://vibe-signal.onrender.com
bash scripts/closed_beta_gate_all.sh https://vibe-signal.onrender.com
```

Expected statuses:

- `current`: `/healthz` and `/api/status` respond, and `git_commit` matches the expected SHA.
- `stale`: `/api/status.git_commit` is present but does not match the expected SHA.
- `unverified`: metadata is missing, endpoint is unavailable, or no expected SHA was supplied.

Missing metadata is not a product failure. It means deployed-version proof is incomplete until Render env vars are configured and the service is redeployed. A passing synthetic production smoke check does not override a `stale` or `unverified` deployed-version result.

Routine wrappers write generated gate reports to ignored automation output by default. Use `WRITE_REPORT=1 bash scripts/closed_beta_gate_all.sh` only when intentionally refreshing tracked gate evidence.
