# Final Closed-Beta Launch Gate Report

Status: final closed-beta launch gate report only. This document does not approve production launch, legal compliance, GDPR/CCPA compliance, model quality, App Store readiness, or commercial training/data use.

## Executive Status

Current recommended status: `BLOCKED_ON_REAL_DEVICE_QA_AND_LEGAL_REVIEW`

Status meanings:

| Status | Meaning |
| --- | --- |
| `CLOSED_BETA_NOT_READY` | Repo or docs have unresolved safety, contract, privacy, deployment, or readiness gaps that block even manual deploy QA. |
| `READY_FOR_MANUAL_DEPLOY_QA` | Repo-side implementation and runbooks are in place; Keith must run deployed backend smoke tests, legal URL checks, monitoring/no-raw-log checks, and real-device QA before inviting testers. |
| `BLOCKED_ON_REAL_DEVICE_QA_AND_LEGAL_REVIEW` | Backend and hosted web are live, but tester invites remain blocked until real-device QA, legal review, and P0 monitoring gates pass. |
| `READY_FOR_TESTER_INVITES` | All manual gates in this report have passed, metadata-only evidence has been captured, and no no-go or rollback trigger is active. |

The repo is currently `BLOCKED_ON_REAL_DEVICE_QA_AND_LEGAL_REVIEW`. Backend and hosted web are live, the Render backend smoke checks passed with synthetic payloads, and Render CORS is configured for the exact Vercel web origin. It is not `READY_FOR_TESTER_INVITES` because real-device iPhone QA, legal review, backup incident ownership, and final metadata-only P0 monitoring evidence are still pending.

## Current Target Status

| Area | Current status |
| --- | --- |
| Backend | Green: Render/FastAPI at `https://vibe-signal.onrender.com` |
| Web frontend | Deployed: Vercel at `https://vibe-signal.vercel.app` |
| CORS | Configured for exact hosted web origin; wildcard origins remain blocked |
| Mobile/browser preview | Repo tests and Expo web preview path covered; physical real-device QA pending |
| Real-device QA | Pending |
| Legal review | Pending |
| Tester invites | Blocked until P0 gates pass |
| Production readiness | No |

## Current Gate Decision Table

| Area | Current gate state | Reason |
| --- | --- | --- |
| Deterministic matching engine | Pass in repo | Engine, schemas, safe phrasing, and backend route are implemented. |
| Synthetic corpus and validators | Pass in repo | Synthetic-only corpus and validation gates exist. |
| Research-only baseline | Pass in repo | Research-only flow is gated to synthetic fixtures. |
| Commercial training | Not claimed | Commercial mode must continue to fail closed until rights are approved. |
| Backend routes | Pass in repo | Health, readiness, legal, analyze, match, feedback, and event routes exist. |
| Deployed backend host | Pass for closed-beta smoke | Render smoke status is green with synthetic payloads. |
| Hosted web frontend | Pass for closed-beta web smoke | Vercel frontend is live and wired to the Render backend. |
| CORS | Pass for hosted web | Exact Vercel origin is configured; wildcard CORS remains prohibited. |
| Mobile backend connection | Blocked until real-device QA | Final `EXPO_PUBLIC_API_URL` and device behavior must be verified on the target device/build. |
| Legal/privacy URLs | Draft route reachable; legal review blocked | Draft routes exist, but legal review remains open. |
| Monitoring/no-raw-log review | Partial | Metadata-only logging scaffold exists and Keith is primary incident owner; backup owner and final manual evidence remain pending. |
| Real-device/TestFlight QA | Blocked until live validation | Device QA script exists, but final beta build evidence is not recorded. |
| Model-quality claims | Not claimed | Synthetic-only checks do not support model-quality claims. |
| Production readiness | Not claimed | This report is closed-beta operational gating only. |
| GDPR/CCPA/legal compliance | Not claimed | Draft legal/privacy docs require legal review. |

## Green / Implemented

- Deterministic Vibe matching engine v0 exists.
- Mobile `/api/match` integration exists and is environment-driven through `EXPO_PUBLIC_API_URL`.
- Backend `/healthz`, `/readyz`, `/api/analyze`, `/api/match`, `/api/feedback`, `/api/events/*`, and legal draft routes exist.
- Deployment smoke-test script exists and uses synthetic payloads only.
- Request logging is metadata-only in the backend helper and includes request IDs.
- Closed-beta monitoring/no-raw-log policy exists.
- Draft privacy, terms, deletion, export, and match-disclaimer docs and routes exist.
- Synthetic matching corpus, validator, research-only baseline, and source-rights gates exist.
- Commercial training mode fails closed unless rights explicitly allow commercial training.
- Closed-beta readiness checklist, tester instructions, and device QA script exist.

## Blocked Items

These block tester invites until resolved or explicitly marked not in beta scope:

- Real-device iPhone QA has not been completed against the intended beta build.
- Legal review has not approved privacy, terms, deletion, export, or match-disclaimer drafts.
- No platform/proxy/server access-log sanitization evidence has been captured.
- No backup incident owner, upgraded alert route, or final manual monitoring evidence has been recorded.
- No final beta build label has been recorded.
- No reviewed-label set supports model-quality claims.
- No commercial-safe training rights are approved.
- No production compliance, GDPR/CCPA compliance, App Store readiness, or public-launch readiness is claimed.

## Manual Verification Required

Before tester invites, Keith must verify:

- deployed backend connectivity and response shape.
- deployed `/readyz` safety flags.
- deployed legal draft routes.
- mobile backend URL configuration.
- real-device `/api/match` happy path, loading state, empty state, error states, and result rendering.
- consent/disclaimer copy in the beta build.
- no raw request bodies, raw message text, provider responses, credentials, secrets, vectors, checkpoints, or model artifacts in logs or artifacts.
- incident owner, backup owner, and monitoring review path.

## Exact Runbook Before Tester Invites

Use placeholder URLs only in repo notes and commands. Replace `https://YOUR_BACKEND_HOST` locally when running commands. Do not commit real deployment URLs, credentials, tokens, tester data, private chats, screenshots with private content, or raw logs.

### 1. Record Release Metadata

Record these outside the repo or in an approved metadata-only release tracker:

```text
backend_host_label:
backend_git_sha:
mobile_build_label:
mobile_git_sha:
operator:
reviewer:
primary_incident_owner:
backup_incident_owner:
monitoring_review_path:
date:
```

Do not record real user/tester contact details, raw messages, request bodies, response bodies, provider responses, credentials, secrets, vectors, checkpoints, or model artifacts.

### 2. Local Backend Smoke Test

From the repo root, start the backend with access logs disabled:

```bash
PYTHONPATH=src python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 --no-access-log
```

In another terminal:

```bash
python scripts/smoke_test_deployed_backend.py --base-url http://127.0.0.1:8000
```

Go only if all `10/10` default checks pass and output contains no raw request/response body content.

### 3. Deployed Backend Smoke Test

Run against the deployed backend base URL only. Do not include a path, query string, fragment, username, password, token, or credential.

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://YOUR_BACKEND_HOST
```

If mobile event logging is in beta scope:

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://YOUR_BACKEND_HOST --include-events
```

Go only if:

- `/healthz` passes.
- `/readyz` passes and reports no unsafe hard flags.
- legal draft routes pass.
- synthetic `/api/analyze`, `/api/match`, and consented `/api/feedback` pass.
- optional event routes pass when event logging is enabled.
- request IDs are present and match the expected safe shape.
- output prints only method, endpoint, status, request ID, and coarse detail.

Optional synthetic match spot check for transient local inspection only:

```bash
curl -sS https://YOUR_BACKEND_HOST/api/match \
  -H 'Content-Type: application/json' \
  -d '{
    "conversation_id": "synthetic_closed_beta_smoke",
    "messages": [
      {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?"},
      {"id": "m2", "author": "other", "text": "Yes, Friday at 3pm works. No pressure if we need to adjust."}
    ]
  }'
```

Use only this synthetic payload. Do not paste real tester chats, private messages, provider responses, credentials, secrets, request bodies from real users, or copied dataset rows into commands, screenshots, logs, or notes.
Do not paste, screenshot, save, or commit the curl response body; use the smoke-test summary and request ID as the metadata-only evidence.

### 4. Legal URL Check

Open or request each deployed route:

```bash
curl -i https://YOUR_BACKEND_HOST/legal/privacy
curl -i https://YOUR_BACKEND_HOST/legal/terms
curl -i https://YOUR_BACKEND_HOST/legal/data-deletion
curl -i https://YOUR_BACKEND_HOST/legal/data-export
curl -i https://YOUR_BACKEND_HOST/legal/match-disclaimer
```

Go only if each route is reachable, clearly draft/closed-beta scoped, and does not claim production compliance, GDPR/CCPA compliance, legal review completion, account deletion/export capability that is not implemented, or model quality.

### 5. Mobile Backend URL Verification

For deployed backend verification:

```bash
cd mobile
npm run verify:backend -- --api-url https://YOUR_BACKEND_HOST --event state
```

If event logging is in beta scope:

```bash
cd mobile
npm run verify:backend -- --api-url https://YOUR_BACKEND_HOST --all
```

Go only if the verifier uses a clean base URL and prints only event type, target URL, status, payload field count, and response-body presence/length.

### 6. Real-Device QA

Follow [device_qa_script.md](device_qa_script.md). At minimum, verify on the actual beta distribution target.

For Expo dev-runtime rehearsal:

```bash
cd mobile
EXPO_PUBLIC_API_URL=https://YOUR_BACKEND_HOST npm start -- --clear
```

If the beta distribution target is TestFlight or another packaged build, install that build on the target device, confirm the build label and backend host label outside the repo, and rerun the device QA script against the deployed backend. Do not treat `npm start` as final TestFlight or packaged-build proof.

For physical-phone local backend testing only:

```bash
ipconfig getifaddr en0 || ipconfig getifaddr en1
PYTHONPATH=src python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 --no-access-log
```

Confirm the phone can open:

```text
http://YOUR_MACHINE_LAN_IP:8000/healthz
```

Use only this synthetic match example:

```text
self: Can you confirm Friday at 3pm?
other: Yes, Friday at 3pm works. No pressure if we need to adjust.
```

Go only if missing-backend, empty, loading, error, and result states pass without raw backend details, private text, unsafe claims, or crashes.

### 7. Monitoring / No-Raw-Log Check

Run the checks in [monitoring_no_raw_logs.md](monitoring_no_raw_logs.md). Minimum command checks:

```bash
curl -i https://YOUR_BACKEND_HOST/healthz
curl -i https://YOUR_BACKEND_HOST/readyz
curl -i https://YOUR_BACKEND_HOST/legal/match-disclaimer
```

Manual log review must confirm:

- request IDs are present.
- endpoint names, status codes, latency buckets, and coarse error categories are visible.
- platform/proxy/server access logs are disabled or sanitized.
- query strings, auth headers, cookies, request bodies, raw messages, provider responses, credentials, tokens, secrets, vectors, checkpoints, model files, and cached artifacts are absent.

## Go/No-Go Checklist

| Gate | Go | No-go |
| --- | --- | --- |
| Executive status | All manual gates passed, then update to `READY_FOR_TESTER_INVITES` | Current state remains `BLOCKED_ON_REAL_DEVICE_QA_AND_LEGAL_REVIEW` |
| Backend host | Concrete backend host label and git SHA recorded outside repo | No concrete host or guessed host |
| Local smoke | `10/10` default checks pass locally | Any local smoke failure |
| Deployed smoke | Default deployed smoke passes | Any deployed smoke failure |
| Event routes | `--include-events` passes when event logging is in beta scope | Event route failure while event logging is enabled |
| `/readyz` | Ready and no unsafe flags | Not ready, unsafe hard flag, or sensitive config echo |
| Legal routes | All five draft routes reachable and scoped as draft | `404`, `5xx`, unexpected redirect, unreachable, or final-compliance claim |
| Mobile URL | Clean base URL only | Path, query, fragment, credential, token, or wrong host |
| Real-device QA | Missing, empty, loading, error, and result states pass | Crash, raw debug detail, unsafe claim, or unreachable backend |
| Consent copy | Permission and sensitive-data warnings visible | Users can submit without seeing boundaries |
| Logs | Metadata only | Raw messages, bodies, secrets, provider responses, vectors, checkpoints, or model artifacts |
| Incidents | Primary owner, backup owner, and monitoring review path recorded | No incident owner or review path |
| Commercial rights | Commercial gates still fail closed | Any commercial training path opens without approved rights |
| Model claims | No model-quality claims | Model-quality claim from synthetic-only metrics |

## Rollback Triggers

Pause tester invites, roll back, or disable the affected route if any of these occur:

- backend is unreachable because of DNS, TLS, gateway, firewall, hosting, or repeated `transport_error`.
- `/healthz` or `/readyz` fails repeatedly.
- `/readyz` reports unsafe logging, raw persistence, analytics/tracking, or training flags.
- sustained 5xx responses appear on any beta route.
- request IDs are missing from smoke responses or reviewed error responses.
- any legal draft route returns `404`, `5xx`, redirects unexpectedly, is unreachable, or contradicts the app copy.
- `/api/match` emits attraction, hidden-intent, cheating, diagnosis, neurotype, attachment-style, emotional-truth, manipulation, relationship-success, deception, or pressure-optimization claims.
- raw messages, request bodies, provider responses, credentials, tokens, secrets, vectors, checkpoints, model files, or cached artifacts appear in logs or committed artifacts.
- mobile missing/invalid backend URL states send network traffic.
- real-device QA crashes or exposes raw backend details.
- no primary incident owner or backup owner is reachable for a user-impacting issue.

## Incident Owner Placeholders

Fill these outside the repo before tester invites:

```text
primary_incident_owner: TODO_NAME_OR_ROLE
backup_incident_owner: TODO_NAME_OR_ROLE
monitoring_review_path: TODO_DASHBOARD_OR_MANUAL_REVIEW_PATH
escalation_window: TODO_RESPONSE_WINDOW
rollback_authority: TODO_NAME_OR_ROLE
support_contact_path: TODO_SUPPORT_PATH
```

Do not commit personal phone numbers, emails, private tester data, credentials, tokens, or real dashboard secrets.

## Evidence Capture Checklist

Capture metadata only:

- backend host label, not a secret-bearing URL.
- backend git SHA.
- mobile build label.
- smoke command names and pass/fail summaries.
- request IDs.
- route names.
- status codes.
- latency buckets or coarse latency observations.
- readiness status and safe flags.
- reviewer initials or role.
- date.
- device model and OS version if not tied to a real tester identity.
- incident owner role and backup role.

Do not capture:

- raw private chats.
- tester names, emails, phone numbers, or account identifiers.
- request bodies.
- response bodies.
- screenshots containing real messages.
- provider responses.
- credentials, tokens, secrets, auth headers, or cookies.
- raw logs with query strings or private content.
- vectors, checkpoints, model files, embeddings, cached artifacts, or raw external dataset rows.

## Boundary Separation

Closed beta readiness:

- This report can move the project to `READY_FOR_TESTER_INVITES` only after all manual gates pass and metadata-only evidence is captured.
- Closed beta remains limited, reversible, and manually monitored.

Production readiness:

- Not claimed.
- Requires production deployment, production monitoring, legal review, platform review, support process, retention policy, incident response, and broader operational proof.

Legal review:

- Not claimed.
- Privacy, terms, deletion, export, and match-disclaimer docs remain drafts until legal review approves them.

Commercial training rights:

- Not claimed.
- Commercial training remains blocked until every training source explicitly passes commercial-use, training-use, consent, privacy, provenance, and harm review gates.

Model-quality evidence:

- Not claimed.
- Synthetic-only metrics are harness checks only.
- Reviewed labels and documented evaluation thresholds are required before public model-quality claims.

## Final Decision Rule

Do not invite testers while the status is `BLOCKED_ON_REAL_DEVICE_QA_AND_LEGAL_REVIEW`.

Update the status to `READY_FOR_TESTER_INVITES` only after:

1. deployed backend smoke passes.
2. optional event smoke passes when event logging is enabled.
3. legal draft routes pass.
4. monitoring/no-raw-log review passes.
5. real-device QA passes.
6. incident owner placeholders are filled outside the repo.
7. metadata-only evidence is captured.
8. no rollback trigger is active.
