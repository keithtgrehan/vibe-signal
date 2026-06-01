# Privacy Policy Draft

Vibe Signal is designed for local-first communication-pattern analysis.

## Data Handling

- Raw chats are not persisted by the local backend by default.
- `/api/match` returns deterministic communication-fit results without storing raw messages.
- Feedback storage requires explicit consent.
- Consented feedback stores metadata only by default, including IDs, rating, comment length, and comment hash.
- Provider/LLM outputs are not required and are never canonical.

## Data Not Collected By Default

- private chats for training
- external dataset rows
- provider responses
- secrets or API keys
- model vectors, checkpoints, or embeddings

## User Rights

Production deployment must expose final export and deletion paths before launch.
