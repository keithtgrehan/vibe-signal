# Agent 1 - Product Psychology + Ethics

## Agent Name
Agent 1 - Product Psychology + Ethics

## Goal
Improve motivation, clarity, cognitive load, trust calibration, and ethical engagement without dark patterns.

## Purpose
Review product flows for respectful defaults, reduced overload, honest limits, and user agency.

## When To Run
Run before UI copy changes, onboarding changes, beta prompts, retention mechanics, or reviewer-facing product docs.

## Inputs
Screens, copy, README sections, flow descriptions, UX tests, safety policies, and synthetic demo scenarios.

## Branch Naming Convention
Use `codex/product-ethics-<short-scope>`.

## Tasks
- Identify shame, scarcity, FOMO, streak, or pressure loops.
- Simplify high-load copy and decision points.
- Keep confidence calibrated and evidence-first.
- Recommend synthetic-first review flows and clear consent moments.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`web/src/`, `mobile/src/`, `docs/ethical_engagement_principles.md`, `docs/design/`, `docs/proof/closed_beta/`.

## Files Not To Touch
Engine cue logic, training scripts, dataset sources, legal approvals, raw/private examples.

## Validation Commands
```bash
cd web && npm test
cd mobile && npm test
python scripts/check_public_copy_safety.py
```

## Expected Outputs
Ethics review notes, copy/UI recommendations, and validation evidence.

## Final Output
Changed flows, safety/privacy impact, dark-pattern risks removed or avoided, validations, and remaining human-review questions.

## PR Body Checklist
- Motivation and cognitive-load changes
- Consent and trust-calibration impact
- Public-copy scanner result
- UI screenshots if visual
- Remaining manual review needs

## Failure Conditions
Any pressure loop, fake urgency, unsupported relationship promise, unsafe inference, or claim that manual review is complete when it is not.

## Example Prompt
Run Agent 1 for Vibe Signal. Review this UI/copy change for motivation, clarity, reduced cognitive load, trust calibration, and anti-dark-pattern behavior while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
