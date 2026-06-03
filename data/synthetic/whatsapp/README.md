# Synthetic WhatsApp Fixture Splits

Status: bootstrap-only synthetic evaluation fixtures. These fixtures are not human-reviewed labels, real chats, external datasets, accuracy proof, model-quality proof, or production-readiness proof.

All examples are hand-authored synthetic text for deterministic regression coverage. Private scenario labels, including any cheating-ambiguous metadata, are evaluation metadata only and must never be surfaced as product capability.

- Seed: `20260603`
- Total messages: `10000`
- Total conversations: `5000`

## Splits

- `dev`: `6000` messages / `3000` conversations
- `hard_negative`: `2000` messages / `1000` conversations
- `heldout`: `1000` messages / `500` conversations
- `red_team`: `1000` messages / `500` conversations

## Regeneration

`python tools/generate_synthetic_whatsapp_fixtures.py --messages 10000 --splits dev=6000,hard_negative=2000,heldout=1000,red_team=1000 --no-api`
