# Vibe Matching Engine Gap Audit

## Existing Deterministic Assets

- Deterministic cue taxonomy covers directness, specificity, hedging, urgency, reassurance, pressure, conflict, alignment, topic shift, ambiguity, cognitive load, unclear asks, overload, repair opportunity, boundary pressure, consent clarity, escalation risk, and response timing.
- Evidence objects include safe cue phrasing, span offsets, confidence, provenance, and interpretation limits.
- Safety controls include red-line phrase blocking, broader output validation, claims matrix checks, training-source rights gates, resource registry validation, and restricted artifact scanning.
- Current product docs position Vibe as deterministic-first conversation-pattern analysis, not hidden-state inference.

## Missing Pieces Before This Build

- No first-class `vibesignal_ai.matching` package existed.
- No match request/result contract or JSON schemas existed.
- No deterministic compatibility scoring layer existed.
- No matching-specific synthetic corpus, validator, training harness, embedding experiment, API route, model card, or matching eval gates existed.
- External dataset review existed as benchmark radar and training-source metadata, but matching-specific rights and prior-art maps were missing.

## Launch Blockers

- Real reviewed labels are not available, so model-quality and benchmark claims remain blocked.
- Commercial training rights are not proven for external sources.
- Backend and frontend/mobile integration for `/api/match` are not yet live-deployed.
- Privacy, terms, deletion/export URLs remain draft until final deployment.
- Production monitoring and reviewed-label feedback loops remain future work.

## PR-by-PR Implementation Plan

1. Add deterministic matching contracts, schemas, scoring, confidence, safe explanation, and tests.
2. Add synthetic match-pair corpus generator, committed synthetic fixture corpus, and validator.
3. Add research-only sklearn baseline gated to synthetic matching data with commercial mode fail-closed.
4. Add optional local embedding experiment that skips without cached dependencies and never downloads data or models.
5. Add local FastAPI backend routes with `/api/match` calling deterministic matching and no raw chat persistence by default.
6. Add launch-readiness docs, matching eval gates, dataset rights map, prior-art map, and claims hardening.
