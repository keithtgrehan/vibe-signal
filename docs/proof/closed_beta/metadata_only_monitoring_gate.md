# Metadata-Only Monitoring Gate

Status: `PARTIAL`.

The backend accepts metadata-only event payloads through existing event routes. This release-gate pass hardens the event contract with an allowlisted `monitoring_event_type` and continues to store only bounded metadata.

## Allowed Monitoring Event Types

- `analysis_started`
- `analysis_succeeded`
- `analysis_failed`
- `safety_blocked`
- `low_signal_fallback`
- `synthetic_demo_started`
- `synthetic_demo_completed`
- `user_feedback_useful`
- `user_feedback_too_strong`
- `user_feedback_missed_context`
- `user_feedback_unsafe_wording`
- `user_feedback_confusing`

Unknown event types are stored as `unspecified`, not as raw custom strings.

## Data That Must Never Be In Events

- raw input text
- evidence quote text
- private message body
- names, phone numbers, email addresses, physical addresses, or third-party identifiers from user input
- raw backend response bodies
- crash reports containing pasted text

## Stored Fields

The backend stores:

- event id
- route-level event category
- allowlisted monitoring event type
- bounded client timestamp
- stored timestamp
- payload field count
- synthetic flag
- duplicate marker for repeated event ids

The backend does not persist the raw event payload.

## Gate Status

This gate is P0-ready only after:

- event/feedback tests pass
- no-raw-content scanner passes
- public-copy scanner passes
- backend event endpoints are included in deployed smoke where in beta scope
- monitoring review confirms the operational dashboard/log process is metadata-only

No analytics SDKs are added by this gate.

