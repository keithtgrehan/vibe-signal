# Closed-Beta Go / No-Go

Date: 2026-06-05.

Final tester invite decision: `BLOCKED`.

## Gate Matrix

| Gate | Status | Notes |
| --- | --- | --- |
| Web custom domain | `PASS` | `https://www.vibe-signal.com` is the primary live web app. `https://vibe-signal.vercel.app` remains the fallback/preview host. |
| Static legal pages | `PASS` | Public legal tabs render from the Vercel web bundle without Render. Status remains `draft_requires_legal_review`; legal review still required. |
| Synthetic demo path | `PASS` | Public demo results are local and do not require Render. |
| Private analyze path | `PARTIAL` | Frontend calls the Render backend for custom analysis; backend availability and CORS still need deployed verification. |
| Backend custom-domain CORS | `PENDING_RENDER_REDEPLOY` | PR #53 added custom-domain CORS config in repo. Verify after the next Render deploy before relying on custom-domain private analysis. |
| Backend legal API parity | `PENDING_RENDER_REDEPLOY` | Static web legal pages work now; `/api/legal/*` parity should be verified after Render deploys latest main. |
| Mobile config readiness | `PARTIAL` | Expo config exists; real-device iPhone/TestFlight QA not run. |
| Safe output blocker | `PASS` | Public-copy scanner, red-line blocker, and blocked-inference tests remain required. |
| Consent gate | `PASS` | Private input remains consent-gated and feedback remains metadata-only. |
| Dataset rights gate | `PASS` | External datasets remain disabled by default; commercial validation remains fail-closed. |
| Real-device iPhone/TestFlight QA | `NOT RUN` | Required before invites. |
| Legal/privacy review | `NOT RUN` | Required before invites. |

## Current Operating Notes After PR #48-#55

- PR #48 shipped the Scanner-style web redesign with evidence-first copy and no Receipts concept.
- PR #49 and follow-up legal work created draft legal pages, all still marked `draft_requires_legal_review`.
- PR #51 hardened custom analyze timeout/loading recovery.
- PR #52 made public legal pages static-first and backend-independent.
- PR #53 added production API/CORS routing fixes in repo; Render still needs a deploy before those backend changes can be verified live.
- PR #54 added no-Render deployment hardening docs, the custom-domain smoke script, and no-backend demo verification.
- PR #55 hardened the custom-domain smoke script output handling.

## Decision

Tester invites remain `BLOCKED` until:

- real-device iPhone/TestFlight QA passes on the intended build
- legal/privacy review approves privacy, terms, data request/delete, support, disclaimer, App Store metadata, and beta tester copy
- Render deploys latest main and custom-domain CORS is verified with synthetic smoke checks
- metadata-only monitoring/no-raw-log review is accepted

## Non-Claims

This gate does not claim production readiness, legal/GDPR/EU AI Act compliance, App Store approval, model accuracy, hidden-intent detection, attraction prediction, deception certainty, diagnosis, relationship outcome prediction, or manipulation capability.
