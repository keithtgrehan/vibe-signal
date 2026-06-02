# Closed-Beta Readiness Checklist

Status: closed-beta operator checklist only. This document does not approve production launch, legal compliance, GDPR/CCPA compliance, model quality, commercial data use, or public marketing claims. The final gate summary is [final_closed_beta_launch_gate_report.md](final_closed_beta_launch_gate_report.md).

Use this checklist before inviting any closed-beta tester. Record the backend host label, mobile build label, git SHA, reviewer, and date outside this repo in the deployment tracker or approved release notes. Do not record real backend URLs, private chats, secrets, phone numbers, emails, provider responses, request bodies, vectors, checkpoints, or real tester account data in this repo.

## Prerequisites

- PR #5 through PR #12 are merged into the branch used for the beta build.
- The backend is deployed from a reviewed git SHA.
- `EXPO_PUBLIC_API_URL` is set to the backend base URL only.
- The backend URL has no path, query string, fragment, username, password, token, or credential.
- `VIBE_BACKEND_ALLOWED_ORIGINS` uses exact browser origins when Expo web or browser-based testing is in scope.
- Backend access logs are disabled or sanitized; safe metadata request logging remains enabled.
- Draft privacy, terms, deletion, export, and match-disclaimer URLs are reachable.
- Privacy/terms/deletion/export drafts are still marked as drafts requiring legal review.
- A beta incident owner, backup owner, and manual monitoring review path are recorded outside this repo.
- Beta tester instructions have been shared before any app access is granted.

## Deployed Backend Smoke Gate

Run these from the repo root against the deployed backend host:

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://YOUR_BACKEND_HOST
```

If mobile event logging is in scope for the beta build, also run:

```bash
python scripts/smoke_test_deployed_backend.py --base-url https://YOUR_BACKEND_HOST --include-events
```

Go only if:

- `/healthz` passes.
- `/readyz` passes and does not report unsafe logging, persistence, analytics, tracking, or training flags.
- legal draft routes pass.
- synthetic `/api/analyze`, `/api/match`, and consented `/api/feedback` pass.
- optional event routes pass when event logging is enabled.
- smoke output contains only method, path, status, allowlisted request ID, and coarse detail.
- request IDs are present and match the allowlisted `req_<32-hex>` shape.
- no request bodies, raw message text, provider responses, headers, cookies, tokens, secrets, vectors, checkpoints, model files, or credentials appear in logs or smoke output.

If a smoke check fails, do not invite testers. Follow the triage table in [deployment_smoke_tests.md](deployment_smoke_tests.md), fix the deploy or configuration, and rerun the full smoke command.

## Mobile Backend URL Verification

Before a real-device run, confirm the mobile runtime uses the same backend base URL that passed smoke tests.

For a deployed backend:

```bash
cd mobile
EXPO_PUBLIC_API_URL=https://YOUR_BACKEND_HOST npm start -- --clear
```

For Android emulator against a local backend:

```bash
cd mobile
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000 npm start -- --clear
```

For a physical phone against a local backend:

```bash
cd mobile
EXPO_PUBLIC_API_URL=http://YOUR_MACHINE_LAN_IP:8000 npm start -- --clear
```

These `npm start` commands are Expo dev-runtime checks. If the beta distribution target is TestFlight or another packaged build, install that build on the target device, record the build label outside the repo, and rerun the real-device QA script against the deployed backend before tester invites.

Optional event-route verifier:

```bash
cd mobile
npm run verify:backend -- --api-url https://YOUR_BACKEND_HOST --event state
```

Go only if the verifier uses a clean base URL, prints no payload body or response body, and returns a success status for the intended route.

## Real-Device QA

Run the detailed script in [device_qa_script.md](device_qa_script.md). At minimum, verify on the target beta device class:

- app opens without a backend URL and shows safe no-backend behavior.
- empty match input does not submit.
- missing backend URL state is safe and points operators to `EXPO_PUBLIC_API_URL`.
- loading state appears during `/api/match`; the expected status text is `Checking communication fit...`.
- network/backend error state is user-facing and does not expose traces, request bodies, or raw backend errors.
- synthetic happy-path input renders score, band, positive factors, risk factors, evidence safe phrases, and explanation.
- consent/disclaimer copy is visible near match submission.
- privacy and terms links are visible wherever the build exposes them.
- no screen claims attraction prediction, hidden intent, cheating detection, diagnosis, neurotype inference, attachment-style inference, emotional truth, manipulation, or relationship success prediction.

Use only synthetic toy messages during QA:

```text
self: Can you confirm Friday at 3pm?
other: Yes, Friday at 3pm works. No pressure if we need to adjust.
```

## Consent And Disclaimer QA

Confirm the match submission surface says or links to the same boundaries as [match_usage_consent_disclaimer.md](match_usage_consent_disclaimer.md):

- Vibe Signal is communication-support only.
- Outputs are pattern-based suggestions, not truth claims.
- Users should submit only messages they have permission to analyze.
- Users should not submit sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.
- Closed beta is not production launch.
- Privacy and terms drafts require legal review before public launch.

## Privacy And Legal URL QA

Open each route in the deployed environment:

- `/legal/privacy`
- `/legal/terms`
- `/legal/data-deletion`
- `/legal/data-export`
- `/legal/match-disclaimer`

Go only if each response:

- clearly says draft or closed-beta readiness copy.
- does not claim production compliance.
- does not claim GDPR/CCPA compliance is complete.
- does not promise account deletion/export functionality that is not implemented.
- accurately states that raw chat persistence, analytics/tracking, training use, and account storage are not added by this scaffold.

## No-Raw-Log And Monitoring QA

Run the checks in [monitoring_no_raw_logs.md](monitoring_no_raw_logs.md) before testers receive access.

Go only if:

- request IDs appear in responses and metadata logs.
- logs use endpoint names, status codes, latency buckets, and coarse error categories.
- platform/proxy/server logs do not include raw request bodies, message text, query strings with secrets, auth headers, cookies, provider responses, credentials, vectors, checkpoints, model files, or cached artifacts.
- monitoring dashboard and alert routing are documented for the beta operator, even if still manual.

## Rollback Checklist

Pause tester invites or roll back the beta build when any trigger below occurs:

- `/healthz` or `/readyz` fails repeatedly.
- the backend is unreachable because of DNS, TLS, gateway, firewall, hosting, or repeated `transport_error` failures.
- 5xx responses are sustained on any beta route, not only match or analysis routes.
- any smoke-test endpoint returns an unexpected status after retry.
- request IDs are missing from smoke responses or reviewed error responses.
- `/readyz` reports unsafe logging, raw persistence, analytics/tracking, or training flags.
- `/api/match` returns unsafe wording or blocked claims.
- any legal draft URL returns `404`, `5xx`, redirects unexpectedly, or is unreachable.
- raw message text, request bodies, credentials, provider responses, vectors, checkpoints, or model artifacts appear in logs or artifacts.
- platform logs expose arbitrary paths, query strings, headers, cookies, or request bodies.
- error responses expose stack traces or raw backend details.
- privacy/terms/deletion/export copy is contradicted by deployed behavior.
- synthetic smoke tests fail after a deploy.
- mobile event verification fails while event ingestion is included in beta scope.
- no beta incident owner is available for a user-impacting issue.
- mobile build cannot reach the deployed backend through the configured base URL.

Rollback steps:

1. Stop sending new beta invitations.
2. Capture only request IDs, endpoint names, status codes, timestamps, latency buckets, and coarse error categories.
3. Do not copy tester messages or private content into incident notes.
4. Revert to the last backend/mobile build that passed smoke and device QA, or disable the affected route if rollback is not immediate.
5. Rerun deployment smoke tests and the affected device QA path.
6. Document the fix, validation, remaining risk, and whether testers need a follow-up notice.

## Go/No-Go Table

| Area | Go | No-go |
| --- | --- | --- |
| Backend smoke | Default smoke passes on deployed host | Any default smoke check fails |
| Request IDs | Smoke responses and reviewed errors include safe request IDs | Missing or unsafe request IDs |
| Event routes | `--include-events` passes when logging is enabled | Event route fails while logging is enabled |
| Mobile URL | Clean base URL configured and verified | Missing URL, path/query/fragment, credentials, or wrong host |
| Device QA | Empty, loading, error, and result states verified | Any state crashes or leaks raw backend detail |
| Consent copy | Sensitive-data and permission warnings visible | Users can submit without seeing boundaries |
| Legal drafts | Draft routes reachable and clearly marked | Routes missing or imply final legal compliance |
| Logs | Metadata only, no raw content | Raw messages, bodies, secrets, headers, provider responses, or artifacts logged |
| Monitoring and incidents | Beta incident owner, backup, and manual/dashboard review path documented | No incident owner or monitoring review path |
| Claims | Observable communication-pattern wording only | Attraction, hidden intent, cheating, diagnosis, neurotype, attachment-style, emotional-truth, manipulation, or relationship-success claim |
| Data rights | Commercial gates still fail closed | Any commercial training path opens without explicit rights |

## Remaining Blockers To Record

Before tester invites, the beta operator should record whether each blocker below is resolved or accepted as still blocking:

- final deployed backend host and git SHA have not been smoke-verified until the commands above pass.
- final deployed privacy, terms, deletion, export, and match-disclaimer URLs still require legal review.
- release tracker entry for backend host, git SHA, mobile build, smoke result, log review, device QA result, incident owner, and reviewer is still required.
- monitoring provider, dashboard, alert routing, and incident owner assignment remain manual unless separately configured.
- backend/admin event ingestion and dashboard gaps remain outside this checklist unless event logging is explicitly included in beta scope.
- reviewed labels are still required before model-quality claims.
- commercial-safe training rights are still required before commercial training use.
- real-device/TestFlight QA remains required for every beta build and backend host.

## Known Limitations

- Closed beta is not production launch.
- Draft legal/privacy copy still requires legal review.
- Deletion/export workflow still requires reviewed support handling, identity checks, retention policy, and response timelines.
- Synthetic-only metrics do not support public model-quality claims.
- Commercial training remains blocked until rights are explicitly reviewed and approved.
- Real-device QA must still be run for each beta build and backend host.
- Monitoring provider, alert routing, and incident owner assignment remain manual unless separately configured.
