# Synthetic WhatsApp Fixture Regression Report

Status: synthetic regression coverage only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, diagnosis, or production readiness.

- Total synthetic messages: `1000`
- Synthetic conversations: `455`
- Evaluation mode: `local_deterministic`
- Fixture regression pass rate: `455/455`
- Evidence completeness rate: `455/455`
- Unsafe-output block rate: `455/455`

## Category Message Counts

- `boundary_pressure`: `90`
- `cheating_ambiguous`: `180`
- `conflict_repair`: `90`
- `happy`: `92`
- `in_love`: `92`
- `low_signal`: `90`
- `new_in_love`: `92`
- `overloaded_message`: `90`
- `scared`: `92`
- `unhappy`: `92`

## Notes

- `cheating_ambiguous` is private synthetic evaluation metadata only.
- Vibe Signal must never claim cheating detection, hidden-intent detection, diagnosis, attraction prediction, or model accuracy from these fixtures.
- Fixtures are hand-authored synthetic WhatsApp-style examples and are not copied from real chats or external datasets.
