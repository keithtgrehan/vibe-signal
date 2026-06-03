# Closed-Beta Go / No-Go

Date: 2026-06-03.

Final tester invite decision: `BLOCKED`.

## Gate Matrix

| Gate | Status | Notes |
| --- | --- | --- |
| Backend readiness | `PARTIAL` | Production backend is live, but hardened smoke finds deployed `/api/feedback` still returns a comment hash. Branch code removes it; Render needs redeploy after merge. |
| Web readiness | `PASS` | Hosted web is live; web tests and build pass on this branch. |
| Mobile config readiness | `PARTIAL` | Expo config exists; real-device iPhone/TestFlight QA not run. |
| Safe output blocker | `PASS` | Public-copy scanner, red-line blocker, and blocked-inference tests added/hardened. |
| Consent gate | `PASS` | PR #19 implemented consent/sensitive-input gates; this PR did not weaken them. |
| Dataset rights gate | `PASS` | External datasets remain disabled by default; commercial validation remains fail-closed. |
| Synthetic regression | `PASS` | 1,000 synthetic messages, 455 conversations, 455/455 local deterministic evaluations passing. |
| Real-device iPhone QA | `NOT RUN` | Required before invites. |
| Legal/privacy review | `NOT RUN` | Required before invites. |

## Decision

Tester invites remain `BLOCKED` until:

- real-device iPhone/TestFlight QA passes on the intended build
- legal/privacy review approves privacy, terms, deletion/export, support, disclaimer, App Store metadata, and beta tester copy
- Render redeploys the branch fix so hardened backend smoke clears `/api/feedback`

## Non-Claims

This gate does not claim production readiness, legal/GDPR/EU AI Act compliance, App Store approval, model accuracy, hidden-intent detection, attraction prediction, deception certainty, diagnosis, relationship outcome prediction, or manipulation capability.
