# Recruiter Demo Agent

## Agent Name
Recruiter Demo Agent

## Goal
Keep README, repo tour, project summary, demo path, screenshots, and limitations recruiter-ready and honest.

## Purpose
Make the project easy to evaluate without overstating launch status, compliance, or model quality.

## When To Run
Run after major PRs, demo UI changes, README updates, screenshot updates, or portfolio packaging work.

## Inputs
README, repo-tour docs, screenshot assets, hosted demo status, validation results, and known limitations.

## Branch Naming Convention
Use `codex/recruiter-demo-<short-scope>`.

## Tasks
- Check README structure and demo path.
- Keep limitations visible and concrete.
- Verify screenshots or screenshot notes are current.
- Keep claims tied to implemented repo evidence.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`README.md`, `docs/recruiter_readiness/`, `docs/assets/screenshots/`, `docs/proof/closed_beta/known_limitations.md`.

## Files Not To Touch
Engine behavior, deployment secrets, legal approval records, raw chats, large generated reports unless scoped.

## Validation Commands
```bash
bash scripts/recruiter_readiness_check.sh
python scripts/check_public_copy_safety.py
git diff --check
```

## Expected Outputs
Recruiter-readable summary, repo tour updates, demo instructions, and honest limitation notes.

## Final Output
Presentation changes, demo status, validation results, and limitations still visible.

## PR Body Checklist
- README/repo tour changes
- Demo path
- Screenshots if updated
- Public-copy scanner result
- Closed-beta caveats

## Failure Conditions
Launch/compliance/accuracy overclaim, unsafe relationship claim, private example, or hiding manual blockers.

## Example Prompt
Run the Recruiter Demo Agent for Vibe Signal. Make the README and repo tour easier to review while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
