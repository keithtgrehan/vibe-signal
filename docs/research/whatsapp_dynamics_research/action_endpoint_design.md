# Future analyzeChatData Action Endpoint Design

This document describes a possible future `analyzeChatData` action endpoint. It is not implemented in this prototype.

## Why It Is Not Production-Ready

- The current work is a local-only research pipeline for aggregate WhatsApp dynamics.
- The prototype has not completed consent UX review, legal review, security review, abuse-risk review, or human label review.
- The deterministic metrics are useful for research triage only and require human interpretation.
- Optional audio telemetry is treated as feature divergence, not as evidence of internal state.
- No production endpoint should be added until private-data handling, deletion, export, retention, and review workflows are approved.

## Required Consent Gate

A future endpoint would need an explicit consent gate before any analysis:

- Confirm the user has permission to analyze the uploaded chat material.
- Explain that outputs summarize observable wording patterns, timing ambiguity, response imbalance, communication pressure, and repair opportunity.
- State that the system does not infer intent, deception, attraction, diagnosis, neurotype, or relationship quality.
- Require an affirmative action before upload or processing.

## No Raw Persistence

The endpoint should avoid raw persistence by default:

- Process uploads in memory where feasible.
- Store only aggregate report fields after explicit consent.
- Do not persist raw messages, participant names, exact private examples, audio files, embeddings, matrices, or private labels.
- Do not store raw evidence spans in public or production logs.
- Keep audit metadata limited to consent, deletion, export, and aggregate processing status.

## Local-Only Prototype First

The local CLI remains the required first step:

- Analyze redacted JSONL under `data/restricted/private_whatsapp`.
- Write private-derived reports under `data/restricted/private_whatsapp/reports`.
- Export only synthetic fixtures under `data/synthetic/private_inspired`.
- Keep model experiments local-only and clearly marked weak-label/synthetic.

## Future Review Requirements

Before implementing an endpoint, complete:

- Consent copy review.
- Privacy and retention review.
- Abuse-risk review for pressure, coercive-use, and surveillance misuse.
- Security review for uploads, logs, storage, deletion, and export.
- Human review of at least 100 private windows before treating model output as useful.
- Product review to ensure no scoring, labels, or unsafe claims are exposed.

## Deletion And Export Flow

A future production flow must include:

- User-visible export of stored aggregate report data.
- User-visible deletion of uploaded files and derived aggregate reports.
- Clear retention windows for temporary processing artifacts.
- Confirmation that raw messages, audio telemetry, embeddings, and matrices are not retained.
- A deletion audit event that contains no raw private text.

## Risk Register

| Risk | Mitigation |
| --- | --- |
| Users treat outputs as fact about another person | Use low-confidence, evidence-backed cue language and require human interpretation. |
| Coercive or surveillance use | Consent gate, blocked claims, no hidden-state output, no production endpoint until review. |
| Raw private data leakage | Local-only prototype, restricted paths, no raw examples, no names, safety scanners. |
| Audio over-interpretation | Report feature divergence only; never emotion, intent, or deception claims. |
| Model-quality overclaim | Weak-label/synthetic report disclaimer; no production integration. |
| Endpoint scope creep | Keep endpoint unimplemented until review gates are complete. |
