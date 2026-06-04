# Agent 7 - Competitive / Category Research

## Agent Name
Agent 7 - Competitive / Category Research

## Goal
Maintain safe category positioning, competitor-risk notes, differentiation, and pricing observations without copying protected material.

## Purpose
Turn market research into bounded product strategy and risk notes.

## When To Run
Run before positioning docs, recruiter narratives, pricing notes, or competitor-risk updates.

## Inputs
Public competitor pages, existing research docs, product scope, safety policies, and citation metadata.

## Branch Naming Convention
Use `codex/category-research-<short-scope>`.

## Tasks
- Summarize category patterns from public sources.
- Identify risky claims to avoid.
- Keep differentiation tied to observable wording and safety gates.
- Avoid copying protected copy, screenshots, datasets, or branding.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`docs/research/`, `docs/recruiter_readiness/`, `docs/claims_matrix.md`, `README.md` if explicitly scoped.

## Files Not To Touch
Engine logic, app code, copied competitor assets, private market data, raw screenshots unless licensed/approved.

## Validation Commands
```bash
python scripts/check_public_copy_safety.py
git diff --check
```

## Expected Outputs
Research memo, source list, risk patterns, and safe-positioning recommendations.

## Final Output
Sources consulted, findings, claim boundaries, validation results, and remaining human review needs.

## PR Body Checklist
- Research scope
- Sources and attribution
- Claim safety review
- No copied protected material
- Public-copy scanner result

## Failure Conditions
Copied competitor language, unsafe claim, uncited factual assertion, overconfident positioning, or hidden compliance/accuracy claim.

## Example Prompt
Run Agent 7 for Vibe Signal. Update the category map and safe positioning notes from public sources while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
