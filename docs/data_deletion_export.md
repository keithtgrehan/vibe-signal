# Data Deletion And Export

Status: draft for closed-beta readiness only. This document is not legal advice, does not claim production compliance, and requires legal review before public launch.

## Current Local Backend Behavior

- `/api/match` does not persist raw chats by default.
- `/api/analyze` does not persist raw chats by default.
- `/api/feedback` requires explicit consent and stores metadata only.
- `/api/events/*` stores bounded event metadata only.
- `GET /legal/data-deletion` and `GET /legal/data-export` return static draft route metadata only.

## Draft Request Documents

- [Data deletion request draft](data_deletion_request_draft.md)
- [Data export request draft](data_export_request_draft.md)

## User Submission Boundaries

Users should not include sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission in deletion or export requests.

## Production Requirement

Before launch, production must provide:

- export endpoint for stored metadata
- deletion endpoint for stored metadata
- documented user-facing URLs for privacy, terms, deletion, and export
- retention policy for feedback/event metadata
- legal-reviewed support channel, identity checks, response timelines, and deployment-specific data-flow review

## Blocked Storage

- raw private chats
- raw external datasets
- provider responses
- secrets
- model binaries
- vectors, embeddings, checkpoints

## Closed-Beta Limits

Closed beta is not production launch. The current static legal routes are review artifacts and do not create a complete deletion/export workflow.
