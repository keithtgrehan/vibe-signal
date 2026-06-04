# Agent 6 - Web Growth / Landing Page

## Agent Name
Agent 6 - Web Growth / Landing Page

## Goal
Improve hosted web clarity, synthetic demo access, trust strip, SEO basics, and beta signup copy without dark patterns.

## Purpose
Make the web demo easier to understand and review while preserving consent and safety limits.

## When To Run
Run before landing page, CTA, SEO, beta signup, or hosted demo copy changes.

## Inputs
Web UI, README demo path, screenshots, public copy, SEO metadata, and synthetic examples.

## Branch Naming Convention
Use `codex/web-growth-<short-scope>`.

## Tasks
- Clarify the first screen and synthetic demo CTA.
- Improve conversion without fake scarcity or pressure.
- Keep consent gate and private-text warnings visible.
- Check public copy against safety scanners.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, fake scarcity, or user/tester training data

## Files Usually Touched
`web/src/`, `web/tests/`, `README.md`, `docs/recruiter_readiness/`, `docs/assets/screenshots/`.

## Files Not To Touch
Engine cue logic, dataset sources, legal approval docs, production backend code unless explicitly assigned.

## Validation Commands
```bash
cd web && npm test
cd web && npm run build
python scripts/check_public_copy_safety.py
```

## Expected Outputs
Clearer web flow, test coverage, screenshot notes if needed, and safety-copy result.

## Final Output
Changed UI/copy, screenshot status, validation results, and closed-beta impact.

## PR Body Checklist
- Landing/demo changes
- Consent and safety impact
- Public-copy scanner result
- Build/test results
- Screenshots if UI changed

## Failure Conditions
Dark-pattern CTA, unsafe product promise, private-text default, consent weakening, or hosted demo hiding backend failures.

## Example Prompt
Run Agent 6 for Vibe Signal. Improve hosted web demo clarity and beta conversion without dark patterns while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
