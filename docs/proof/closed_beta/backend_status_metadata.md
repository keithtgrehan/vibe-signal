# Backend Status Deploy Metadata

Status: closed-beta verification support only. This metadata helps compare a deployed backend with the Git commit under review. It is not a production-readiness, security, privacy, legal, GDPR, EU AI Act, or App Store compliance claim.

## Route

`GET /api/status` returns the existing safe service metadata plus these deploy identity fields:

- `git_commit`
- `deploy_version`
- `build_timestamp`
- `service_revision`

Each field returns a sanitized value when configured or `"unknown"` when missing or unsafe-looking.

## Allowed Sources

The backend only reads allowlisted environment variables:

- `git_commit`: `GIT_COMMIT`, `RENDER_GIT_COMMIT`, `VERCEL_GIT_COMMIT_SHA`
- `deploy_version`: `DEPLOY_VERSION`, `VIBE_DEPLOY_VERSION`, `RENDER_DEPLOY_VERSION`
- `build_timestamp`: `BUILD_TIMESTAMP`, `VIBE_BUILD_TIMESTAMP`, `RENDER_BUILD_TIMESTAMP`
- `service_revision`: `SERVICE_REVISION`, `RENDER_SERVICE_NAME`, `RENDER_SERVICE_ID`

It does not expose arbitrary environment variables.

## Safety Rules

Do not configure these fields with:

- secrets, API keys, tokens, passwords, cookies, or authorization values
- internal URLs
- usernames
- local filesystem paths
- raw user/private message content
- raw provider responses
- private tester data

Values that look unsafe or unsupported are returned as `"unknown"`.

## Render Setup

Recommended Render environment variables:

```text
GIT_COMMIT=<commit-sha-being-deployed>
DEPLOY_VERSION=<release-label>
BUILD_TIMESTAMP=<UTC-build-time>
SERVICE_REVISION=<safe-render-service-or-revision-label>
```

If Render exposes `RENDER_GIT_COMMIT`, the backend can use that without setting `GIT_COMMIT` separately. Future deployed verification should compare `/api/status.git_commit` with the local `git rev-parse HEAD` for the commit intended to be deployed.
