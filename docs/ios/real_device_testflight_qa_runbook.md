# Real-Device TestFlight QA Runbook

Status: `NOT RUN`.

Use this runbook on the intended iPhone/TestFlight build before closed-beta tester invites. Use synthetic text only for evidence capture.

## Setup

- Install the TestFlight build.
- Confirm build label and backend host.
- Confirm `EXPO_PUBLIC_API_URL` or production config points to `https://vibe-signal.onrender.com`.
- Record only metadata: device model, iOS version, build label, backend deploy label, tester initials.

## Test Flow

- first launch
- onboarding
- synthetic demo
- private paste consent gate
- empty input
- low-signal fallback
- long synthetic input
- backend offline state
- slow backend state
- result evidence cards
- cannot-infer block
- safe next step
- feedback buttons
- privacy/support/legal links
- delete/data request links
- crash recovery
- accessibility/tap targets
- dark/light mode if applicable

## Evidence

Use [../proof/closed_beta/real_device_qa_evidence_template.md](../proof/closed_beta/real_device_qa_evidence_template.md). Screenshots must use synthetic content only.

