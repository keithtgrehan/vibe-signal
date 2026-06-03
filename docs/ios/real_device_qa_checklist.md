# iOS Real-Device QA Checklist

Use synthetic examples only. Do not paste real private chats, tester content, secrets, screenshots with private content, raw request bodies, raw responses, provider outputs, external dataset rows, vectors, checkpoints, or model artifacts into QA notes.

## Setup

- Device: iPhone target for beta.
- Build: record build label outside the repo.
- Backend: `https://vibe-signal.onrender.com`.
- Network: normal mobile/Wi-Fi network, then one offline/error check.

## Required Flow

1. Open app and confirm the first screen says Vibe Signal reviews observable message patterns, not motives.
2. Tap the synthetic example path and confirm it works without private input.
3. Try pasted/private analysis without consent; confirm the app does not submit and does not consume quota.
4. Confirm consent copy says: only submit messages you have permission to analyze.
5. Confirm sensitive-input warning covers names, phone numbers, addresses, minors, medical/legal/financial/workplace-sensitive content, and highly sensitive third-party content.
6. Submit the synthetic match example.
7. Confirm result hierarchy shows summary, signal strength, pattern labels, evidence phrases, uncertainty/limits, cannot-infer content, and safe next steps.
8. Confirm low-signal short text returns insufficient/low-signal fallback and no overconfident result.
9. Confirm network error states do not show stack traces, raw backend bodies, request bodies, or private text.
10. Confirm feedback duplicate-submit behavior prevents repeated submission from the same result screen.
11. Confirm legal/disclaimer links are visible and draft-scoped.
12. Confirm no screen claims private feelings, hidden motives, deception certainty, diagnosis, relationship-style labels, manipulation guidance, or production readiness.

## Synthetic QA Inputs

Clear direct ask:

```text
self: Can you confirm Friday at 3pm?
other: Yes, Friday at 3pm works. No pressure if we need to adjust.
```

Low signal:

```text
self: ok
```

Boundary-pressure check:

```text
self: I cannot talk tonight.
other: You need to answer now, I already asked three times.
```

## Evidence Capture

Record only metadata:

- date
- tester role or initials
- device model
- OS version
- build label
- backend host label
- pass/fail by checklist item
- request ID if shown by a tool
- coarse error category

Real-device QA remains a blocker until this checklist is completed on the target beta build.
