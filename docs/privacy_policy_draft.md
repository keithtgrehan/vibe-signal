# Privacy Policy Draft

Status: draft for closed-beta readiness only. This document is not legal advice, does not claim production compliance, and requires legal review before public launch.

Vibe Signal is a communication-support product. It reviews observable wording patterns and returns pattern-based suggestions, not truth claims about another person.

## What Data Is Processed

When a user submits text to local analysis or `/api/match`, the backend processes the submitted message text long enough to return deterministic pattern results.

The matching flow may process:

- message text supplied by the user
- message author labels such as `self`, `other`, or `unknown`
- optional message timestamps
- user preferences such as directness, low pressure, explicit plans, and message-load preference

The backend may also process bounded metadata for:

- health checks
- event acceptance routes
- consented feedback
- quota or billing event contracts when configured

## What Is Not Stored By Default

- Raw chats are not persisted by the local backend by default.
- `/api/match` returns deterministic communication-fit results without storing raw messages.
- `/api/analyze` returns deterministic cue evidence without storing raw messages.
- Feedback storage requires explicit consent.
- Consented feedback stores metadata only by default, including IDs, rating, comment length, and comment hash.
- Provider/LLM outputs are optional and never canonical.

## What Users Should Not Submit

Users should not submit:

- sensitive personal data
- secrets, passwords, tokens, or API keys
- medical data
- legal documents
- financial data
- third-party private messages without permission
- material they do not have the right to process

## Data Not Collected By Default

- private chats for training
- external dataset rows
- provider responses
- secrets or API keys
- model vectors, checkpoints, or embeddings
- analytics or tracking data added by this draft
- account profiles or account storage added by this draft
- training use added by this draft

## Deletion And Export

Local matching and analysis routes do not persist raw messages by default, so there may be no raw message content to delete or export from those routes.

Deletion and export handling applies to stored metadata such as consented feedback, event metadata, device-scoped identifiers, or support records when those systems are enabled.

Draft request documents:

- [Data deletion request draft](data_deletion_request_draft.md)
- [Data export request draft](data_export_request_draft.md)

Production deployment must expose final reviewed deletion and export paths before launch.

## Closed-Beta Limits

Closed beta is not production launch. Before public launch, Vibe Signal needs final reviewed privacy URLs, terms URLs, deletion/export workflow, retention policy, support contact, and deployment-specific data-flow review.
