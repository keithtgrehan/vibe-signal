# Data Deletion And Export

## Current Local Backend Behavior

- `/api/match` does not persist raw chats by default.
- `/api/analyze` does not persist raw chats by default.
- `/api/feedback` requires explicit consent and stores metadata only.
- `/api/events/*` stores bounded event metadata only.

## Production Requirement

Before launch, production must provide:

- export endpoint for stored metadata
- deletion endpoint for stored metadata
- documented user-facing URLs for privacy, terms, deletion, and export
- retention policy for feedback/event metadata

## Blocked Storage

- raw private chats
- raw external datasets
- provider responses
- secrets
- model binaries
- vectors, embeddings, checkpoints
