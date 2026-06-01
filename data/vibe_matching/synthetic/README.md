# Synthetic Vibe Matching Fixtures

This directory contains hand-authored synthetic match-pair fixtures for deterministic tests, research-only training scaffolds, and safety checks.

Rules:

- `source_type` must remain `synthetic_fixture`.
- Rows must not be copied from private chats, public datasets, provider responses, or external examples.
- Rows are not evidence of real behavior and cannot support production model-quality claims.
- Commercial model training remains blocked unless every selected source is explicitly commercial-safe.
