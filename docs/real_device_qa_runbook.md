# Real-Device QA Runbook

Real-device QA is required before closed-beta tester invites. This runbook uses synthetic-only examples and metadata-only evidence.

## Setup

1. Install Expo Go or the reviewed beta build on the iPhone.
2. From `mobile/`, install dependencies if needed:

```bash
npm install
```

3. Start Expo against the deployed backend:

```bash
EXPO_PUBLIC_API_URL="https://vibe-signal.onrender.com" npx expo start --web --clear
```

For a physical iPhone using Expo Go, use the QR flow from the same network. For a packaged/TestFlight build, confirm the build label and configured backend URL outside this repo.

## Synthetic Test Case

Use only:

```text
self: Can you confirm Friday at 3pm?
other: Yes, Friday at 3pm works. No pressure if we need to adjust.
```

Do not paste real private chats, tester messages, provider responses, secrets, medical/legal/financial content, copied dataset rows, or raw external examples.

## Required Flow Checks

| Area | Expected result |
| --- | --- |
| Home | Polished Vibe Signal UI renders and legal entry is visible. |
| Backend URL | Missing/invalid URL state is safe and does not send traffic. |
| Analyze input | Empty input cannot submit. |
| Consent | Permission/legal boundary copy is visible before submit. |
| Loading | Submit shows bounded loading text and no raw backend details. |
| Success | Result renders score, fit band, positive factors, risk factors, evidence safe phrases, and cautious explanation. |
| Empty arrays | Missing/null/empty factors and evidence render empty states, not crashes. |
| Error | Backend/CORS/timeout errors show safe user copy only. |
| Feedback | Duplicate `Useful` or `Not useful` taps are not double-submitted after success. |
| Legal | Privacy, terms, deletion, export, and match-disclaimer draft routes are reachable or fallback copy is clearly draft-scoped. |
| Disclosure | UI states that Vibe Signal is communication-support only and not a truth or hidden-state machine. |

## Evidence Capture

Record only:

- device model and OS version if not tied to a tester identity.
- app build label.
- backend host label.
- route names.
- pass/fail status.
- coarse issue notes.
- date and reviewer role/initials.

Do not record:

- raw chats.
- screenshots containing private content.
- request or response bodies.
- tester names, emails, phone numbers, or account identifiers.
- secrets, auth headers, cookies, tokens, provider responses, vectors, checkpoints, model files, or raw datasets.

## Current Status

Real-device iPhone QA is pending. Tester invites remain blocked until this runbook passes against the intended beta build and deployed backend.
