# Manual QA Required

Date: 2026-06-03.

Status: `NOT_RUN`.

Manual QA must use synthetic or permissioned toy text only. Do not capture private screenshots, raw request/response bodies, tester identities, secrets, or real chats in proof artifacts.

## Required Runs

- iPhone real-device Expo/TestFlight flow.
- Hosted web flow from landing page to synthetic example to result screen.
- Consent-gated pasted-text flow with blocked submit until consent is checked.
- Low-signal input flow.
- API error/offline flow.
- Feedback duplicate-submit flow.
- Legal/privacy/support/delete/export link visibility.

## Evidence Rules

- Record metadata only: device, OS version, build identifier, route/screen names, pass/fail, and blocker summary.
- Do not record raw message text unless it is one of the committed synthetic fixtures.
- Do not include screenshots containing private messages.
