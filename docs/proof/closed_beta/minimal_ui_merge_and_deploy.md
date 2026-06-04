# Minimal UI Merge And Deploy Proof

## Merge

- PR: `#39` - `https://github.com/keithtgrehan/vibe-signal/pull/39`
- Approved branch: `codex/minimal-human-product-ui`
- Approved commit: `3ffba2f Simplify web UI and humanize product copy`
- Merge method: squash merge
- Main commit after merge: `f814a8216f2d5e7435a2161a9f2fec8ba0cf274b`

## Validation Commands Run

Before merge on `codex/minimal-human-product-ui`:

```bash
python -m pytest -q
cd web && npm test && npm run build
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
git diff --check
git grep -ni "they like you|hidden intent|they are lying|cheating detector|manipulation detector|diagnose|attachment style|neurotype|make them respond|win them back|secret feelings|relationship truth|catch them" -- web docs README.md || true
```

After merge on `main`:

```bash
python -m pytest -q
cd web && npm test && npm run build
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
git diff --check
git status --short
```

Outcomes:

- Python tests passed.
- Web tests passed.
- Web build passed.
- Public-copy safety check passed with `23` allowlisted findings and `0` unallowlisted findings.
- No-raw-content leak check passed with `0` findings.
- `git diff --check` passed.
- `git status --short` was clean before creating this proof doc and the Replit plan doc.
- The exact requested blocked-copy grep returned no matches.

## Vercel Deployment Status

- Production frontend: `https://vibe-signal.vercel.app`
- GitHub commit status context: `Vercel`
- Status: `success`
- Description: `Deployment has completed`
- Vercel deployment details: `https://vercel.com/keith-grehans-projects/vibe-signal/AYb8EaQXVZfh1VwLBq1K14J4z7pN`

Checklist verified:

- Page loads with HTTP `200`.
- Minimal hero is visible.
- Demo flow works.
- Analyze text remains consent-gated.
- Result card order is:
  1. What stands out
  2. Evidence
  3. What it could mean
  4. Safer reply
  5. Limits
- Browser console check reported no warnings or errors during the production demo smoke test.

## Render Backend Smoke Status

Backend base URL: `https://vibe-signal.onrender.com`

Version verifier:

- Command: `python scripts/verify_deployed_version.py --base-url https://vibe-signal.onrender.com --expected-git-commit "$(git rev-parse HEAD)" || true`
- Result: `unverified`
- Reason: `health_or_status_endpoint_unavailable`
- Notes: this was not treated as a product failure because the merge is frontend-first and the backend deployment is intentionally unchanged.

Production analyze smoke:

```bash
python scripts/smoke_test_production_analyze.py --base-url https://vibe-signal.onrender.com
```

Result:

- `/healthz` PASS
- `/api/status` PASS
- `/api/analyze` PASS
- Summary: `3/3 production analyze smoke checks passed`

## Replit A/B Plan

- Plan doc: `docs/experiments/replit_friend_ab_test.md`
- Replit purpose: parallel friends feedback only.
- Replit is not production.
- Production remains Vercel + Render.
- Backend API remains `https://vibe-signal.onrender.com`.
- No Replit implementation was started in this repo.

## Known Limitations

- Vercel CLI is not installed locally, so deployment status was verified through GitHub commit status plus live-site HTTP/browser checks.
- Render version metadata could not be verified against the frontend merge commit, which is expected for a frontend-only change when the backend is unchanged.
- Friend feedback must avoid real private chats unless the tester has permission to use the text.
- Replit experiments need a separate branch and should not be treated as production evidence.

## Confirmations

- Backend contracts were not changed.
- Backend runtime logic was not changed.
- No analytics SDKs or tracking were added.
- No auth was added.
- No raw message persistence or raw message logging was added.
- n8n was not wired into production.
- Replit is not production.
