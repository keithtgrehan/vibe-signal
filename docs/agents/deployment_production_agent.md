# Deployment Production Agent

## Agent Name
Deployment Production Agent

## Goal
Verify Render/Vercel configuration, CORS, deploy metadata, production analyze path, and bounded deployed regression.

## Purpose
Keep deployment checks repeatable without increasing production load or hiding backend failures.

## When To Run
Run before or after Render/Vercel deploys, CORS changes, API client changes, smoke-test updates, or hosted demo QA.

## Inputs
Deployment URLs, env var names, `/healthz`, `/api/status`, smoke-test outputs, Vercel config notes, and Render CORS settings.

## Branch Naming Convention
Use `codex/deployment-<short-scope>`.

## Tasks
- Verify frontend API base URL and backend allowed origins.
- Run metadata-only deployed version and analyze smoke checks.
- Check timeout/retry behavior when web API client changes.
- Document manual deployment steps and unresolved deploy metadata.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, production load-heavy automation, or user/tester training data

## Files Usually Touched
`web/src/api.js`, `scripts/smoke_test_production_analyze.py`, `scripts/verify_deployed_version.py`, `docs/deployment/`, `.github/workflows/production-smoke-manual.yml`.

## Files Not To Touch
Engine cue logic, evaluation reports unrelated to deploy, raw logs, secrets, analytics SDKs.

## Validation Commands
```bash
bash scripts/prod_smoke_all.sh
cd web && npm test
python -m pytest -q tests/test_verify_deployed_version.py tests/test_production_analyze_smoke.py
```

## Expected Outputs
Deployment status, smoke results, required env vars, CORS requirements, and manual deploy checklist.

## Final Output
Backend URL, Vercel env var, Render CORS setting, smoke result, deploy metadata confidence, and hosted demo expectation.

## PR Body Checklist
- Env vars required
- CORS origins
- Timeout/retry impact
- Smoke-test result
- Manual deploy steps

## Failure Conditions
Fake local results, hidden backend failure, production load-heavy checks, wildcard credentialed CORS, or raw request/response logging.

## Example Prompt
Run the Deployment Production Agent for Vibe Signal. Verify Render/Vercel envs, CORS, smoke tests, deploy metadata, and production analyze path while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
