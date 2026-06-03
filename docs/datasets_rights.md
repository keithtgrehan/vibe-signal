# Dataset Rights Gate

Vibe Signal keeps dataset use fail-closed. The current closed-beta engine is deterministic-first and synthetic-regression-tested; it is not trained on external datasets and the repository does not authorize raw third-party dataset downloads.

## Current Registry

- Registry: `configs/vibe_training_sources.example.yml`
- Schema reference: `schemas/vibe_training_sources.schema.json`
- Validator: `scripts/validate_vibe_training_sources.py`
- Compatibility wrapper: `tools/validate_training_sources.py`

## Allowed Today

- `synthetic_vibe_matching`: hand-authored synthetic fixtures only. These may support research-only training smoke tests, deterministic eval scaffolds, UI tests, and regression checks. Synthetic fixture performance is not real-world model accuracy.

## Metadata-Only Research Candidates

- `goemotions`: research/benchmark metadata only. Google Research describes GoEmotions as 58k English Reddit comments labeled with 27 emotion categories or neutral. No raw Reddit comments are downloaded or committed.
- `tweeteval_sentiment`: sentiment benchmark metadata only. This entry covers positive/neutral/negative sentiment shape; other TweetEval subsets require separate license review.
- `dailydialog`: non-commercial/research metadata only; commercial training remains blocked.

## Blocked Pending Review

- `dair_ai_emotion`
- `empathetic_dialogues`
- sensitive survivor, consent, accessibility, neurodivergent, transcript, audio, video, and multimodal sources

## Commercial Fail-Closed Rule

Commercial mode must reject any source that is external, research-only, non-commercial, eval-only, restricted, manual-review, unknown, or synthetic-only. It must also reject model-quality claims derived from synthetic fixtures.

## Prohibited Repository Artifacts

Do not commit raw chats, private messages, tester content, screenshots of private content, provider outputs, external dataset rows, embeddings, vectors, checkpoints, trained models, or derived corpora.
