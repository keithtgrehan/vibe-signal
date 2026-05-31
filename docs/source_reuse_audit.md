# Source Reuse Audit

## Reused Patterns

Vibe Signal reused only neutral engineering patterns from earlier local analysis projects:

- strict conversation contracts;
- safe IO and schema helper structure;
- observability helper shape;
- audio pause and segment aggregation helpers;
- deterministic shift and clarity feature scaffolding;
- optional summary adapter structure;
- safety validation around user-facing text.

## Vibe Adaptations

- Case metadata became strict conversation metadata.
- Source-domain scoring became conversation-native deterministic feature review.
- Audio helpers now support bounded pacing and hesitation proxies without biometric claims.
- Optional summary layers remain late-bound and non-canonical.
- Pipeline outputs target safe comparison cards rather than source-domain reports.

## Dropped On Purpose

Legacy source-domain scoring, entity fields, event windows, and reporting artifacts were intentionally dropped.

## Original To VibeSignal AI

- WhatsApp and pasted-chat parsers.
- Speaker normalization, language hints, turn grouping, response linking, and topical block detection.
- Conversation-native consistency, directness, specificity, and hedging features.
- Output safety validator and banned-term policy.
- Soft-verdict safety validation and safe UI summary export.
- Safe UI payload builders for MVP cards plus the canonical UI summary artifact.
- Conversation-first README, docs, tests, and handoff notes.
