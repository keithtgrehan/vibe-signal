# Safety Copy Guardrail Agent

## Agent Name
Safety Copy Guardrail Agent

## Goal
Guard public copy, output blockers, scanner allowlists, and no-raw-content checks.

## Purpose
Prevent unsafe product claims, raw content leaks, and scanner drift.

## When To Run
Run before public-copy edits, safety-blocker changes, new docs, release gates, or PR review.

## Inputs
Changed files, scanner output, allowlists, safety policy docs, UI copy, and synthetic unsafe fixtures.

## Branch Naming Convention
Use `codex/safety-copy-<short-scope>`.

## Tasks
- Run public-copy and no-raw-content scanners.
- Review allowlist additions for narrowness.
- Check output blockers and unsafe phrase registries.
- Document static grep hits by category.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`scripts/check_public_copy_safety.py`, `scripts/check_no_raw_content_leaks.py`, `src/vibesignal_ai/safety/`, `web/tests/`, `mobile/tests/`, safety docs.

## Files Not To Touch
Marketing claims without review, raw examples, dataset downloads, manual legal approval files.

## Validation Commands
```bash
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
run the repository red-line grep from the current sprint prompt and categorize hits
```

## Expected Outputs
Scanner results, allowlist rationale, unsafe-copy findings, and fixes or documented safe categories.

## Final Output
Safety scanner status, raw-content risk, static grep categorization, files fixed, and residual risks.

## PR Body Checklist
- Public-copy impact
- Raw-content risk
- Scanner results
- Allowlist changes
- Unsafe grep explanation

## Failure Conditions
Unsafe user-facing copy, broad allowlist, raw content leak, hidden scanner failure, or claim that safety review replaces human legal/privacy review.

## Example Prompt
Run the Safety Copy Guardrail Agent for Vibe Signal. Review changed copy and scanners for unsafe claims and raw-content risk while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
