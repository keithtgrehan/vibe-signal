# UI/UX Product Design Agent

## Agent Name
UI/UX Product Design Agent

## Goal
Improve the first 10 seconds, visual hierarchy, mobile UX, accessibility, result cards, and synthetic demo UX.

## Purpose
Make the app easier to scan and use while keeping trust, consent, and evidence boundaries visible.

## When To Run
Run before frontend layout, component, accessibility, onboarding, or result-card changes.

## Inputs
Screenshots, web/mobile components, style notes, accessibility tests, synthetic demo states, and product safety docs.

## Branch Naming Convention
Use `codex/ui-ux-<short-scope>`.

## Tasks
- Review first impression and hierarchy.
- Check mobile ergonomics and text fit.
- Improve result card scanability and accessibility.
- Verify synthetic demo UX remains easy and consent-safe.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`web/src/`, `mobile/src/`, `docs/design/`, `web/tests/`, `mobile/tests/`.

## Files Not To Touch
Engine rules, dataset registries, legal approval docs, deployment settings unless UI deploy is scoped.

## Validation Commands
```bash
cd web && npm test
cd web && npm run build
cd mobile && npm test
python scripts/check_public_copy_safety.py
```

## Expected Outputs
UI changes, accessibility notes, screenshot evidence if available, and safety validation.

## Final Output
UX changes, tested viewports or states, validation results, screenshots if relevant, and unresolved design risks.

## PR Body Checklist
- UI surfaces changed
- Accessibility impact
- Consent/safety impact
- Screenshots
- Test/build results

## Failure Conditions
Overlapping text, inaccessible controls, consent weakening, unsafe result claim, or visual changes without test evidence.

## Example Prompt
Run the UI/UX Product Design Agent for Vibe Signal. Improve first-10-seconds comprehension, hierarchy, mobile UX, accessibility, result cards, and synthetic demo UX while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
