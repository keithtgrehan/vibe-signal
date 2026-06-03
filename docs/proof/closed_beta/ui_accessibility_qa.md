# UI Accessibility QA

Date: 2026-06-03
Branch: `codex/ui-ux-product-design-research-upgrade`

## Status

UI accessibility and safety QA is improved but not complete. Web and mobile now have stronger focus, live status, checkbox, fallback, and feedback states. Tester invites should still wait for real-device QA and legal review.

## Scope

Covered in this sprint:

- Web landing, synthetic demos, analyze form, result hierarchy, feedback, legal fallback.
- Mobile landing, synthetic demos, analyze form, result hierarchy, feedback, provider consent checkboxes.
- Synthetic-only demo and screenshot rules.
- Metadata-only feedback behavior.

Out of scope:

- Engine precision/evaluation work.
- Real-device App Store/TestFlight review.
- Full automated accessibility audit.
- Legal review.

## Commands To Run

```bash
cd web && npm test
cd web && npm run build
cd mobile && npm test
cd mobile && npx expo config --type public
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

If backend or Python surfaces are touched, also run:

```bash
python -m py_compile $(git ls-files '*.py')
python -m pytest -q
```

## Viewport / Device Matrix

- Web desktop: landing, synthetic result, consent gate, low-signal fallback, metadata feedback.
- Web mobile viewport: landing, synthetic result, consent gate, low-signal fallback.
- Mobile app: home, analyze, synthetic result, low-signal result, feedback, legal fallback.
- Real iOS device or simulator remains required before invites.

## Accessibility Improvements

- Web controls now share an amber `:focus-visible` outline.
- Web mode selector is a button group, not a misleading tablist.
- Web input helper text is connected through `aria-describedby`.
- Web feedback success and error messages use live status/alert roles.
- Mobile custom checkboxes expose checkbox role and checked state.
- Mobile status/error text uses polite/assertive live regions where supported.
- Mobile key controls were raised to 44px+ tap targets where practical.
- Mobile result cards now show compact fit/evidence context before evidence details.

## Safety / Privacy QA

- Synthetic demos do not require private-text consent.
- Private text still requires explicit permission checkbox.
- Short/context-light input renders an intentional fallback.
- Missing safe evidence renders a fallback instead of a summary-only result.
- Feedback buttons send bounded metadata labels only.
- No free-text feedback field is present.
- Screenshot capture must use synthetic examples only.

## Scanner Notes

The public-copy scanner remains unchanged. Blocked public-copy categories include romantic certainty, private-state certainty, accusation/detection claims, diagnosis/neurotype claims, persuasion coaching, quality guarantees, and dark-pattern retention phrases. Internal mentions of these categories should stay in safety docs, tests, scanner code, or allowlists with a reason.

## Remaining Manual QA

- Keyboard-only web flow through nav, hero CTAs, demo cards, analyze form, consent, submit, result feedback, and legal tabs.
- Screen reader smoke pass for result hierarchy and feedback status.
- Mobile dynamic text pass for demo cards, evidence cards, and feedback buttons.
- Real-device keyboard coverage for the multiline input.
- Provider/paywall/quota/share-card visual-system cleanup in a separate branch.
