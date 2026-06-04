# Agent 4 - Trust / Explainability / Safe Output UX

## Agent Name
Agent 4 - Trust / Explainability / Safe Output UX

## Goal
Improve evidence-first result hierarchy, cannot-infer blocks, signal-strength language, low-signal fallback, and safe repair suggestions.

## Purpose
Make outputs understandable and bounded without false authority.

## When To Run
Run when result cards, summaries, evidence spans, blockers, or safe suggestion copy changes.

## Inputs
Result payloads, web/mobile result UI, safe-output policy, low-signal tests, and synthetic examples.

## Branch Naming Convention
Use `codex/safe-output-ux-<short-scope>`.

## Tasks
- Ensure evidence appears before interpretation.
- Keep cannot-infer limits visible and specific.
- Verify low-signal fallbacks do not overread context.
- Review repair suggestions for agency and non-manipulation.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`web/src/`, `mobile/src/`, `src/vibesignal_ai/safety/`, `docs/legal_safe_output_policy.md`, UI tests.

## Files Not To Touch
Dataset registries, legal approval records, engine taxonomy changes unless explicitly assigned.

## Validation Commands
```bash
cd web && npm test
cd mobile && npm test
python scripts/check_public_copy_safety.py
python -m pytest -q tests/test_vibe_safe_phrasing.py tests/test_vibe_matching_safe_phrasing.py
```

## Expected Outputs
Safer result UX, updated tests, and evidence/cannot-infer validation.

## Final Output
Changed output surfaces, safety blocker status, UI validation, and unresolved UX risks.

## PR Body Checklist
- Output surfaces changed
- Cannot-infer and low-signal behavior
- Safe repair suggestion review
- Public-copy scanner result
- Screenshots if UI

## Failure Conditions
Output implies private motives, truth, attraction, diagnosis, therapy, manipulation, or confidence beyond evidence.

## Example Prompt
Run Agent 4 for Vibe Signal. Review the result UX for evidence-first hierarchy, cannot-infer boundaries, low-signal fallback, and safe repair suggestions while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
