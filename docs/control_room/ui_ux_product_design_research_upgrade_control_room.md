# UI/UX Product Design Research Upgrade Control Room

Date created: 2026-06-06  
Branch: `codex/ui-ux-product-design-research-upgrade`  
PR: https://github.com/keithtgrehan/vibe-signal/pull/28  
Primary commit: `7be952815fcf74344d00143cbec80fb64b196820`  
Base at implementation time: `origin/main` after PR #27 (`99ec1e3`)

## Executive Summary

This branch upgrades Vibe Signal’s trust-first web and mobile UX while preserving the existing visual identity. The work makes the product clearer in the first 10 seconds, makes synthetic demos the obvious first path, strengthens evidence-first result hierarchy, improves mobile result ergonomics, adds accessibility affordances, and documents the design system for future implementation.

No engine logic was changed. The branch intentionally avoids the engine precision/evaluation workstream and stays within web UI, mobile UI, UI tests, and docs.

## Product Positioning Preserved

Vibe Signal is presented as communication-support software that highlights observable wording patterns. The UI focuses on:

- Clarity
- Ambiguity
- Directness
- Reassurance
- Pressure and urgency cues
- Cognitive load
- Unanswered asks
- Boundary pressure
- Escalation risk
- Repair opportunities
- Limits and safe next steps

The branch does not add or imply:

- Cheating detection
- Hidden-intent detection
- Attraction prediction
- Lie detection
- Diagnosis, therapy, attachment-style, or neurotype inference
- Manipulation coaching
- Fake testimonials
- Fake scarcity
- Analytics SDKs
- Raw-message feedback payloads
- Legal/GDPR/App Store/model-quality claims
- New paywalls
- External datasets
- Real/private chat examples

## What Changed

### Web

Files:

- `web/src/App.jsx`
- `web/src/styles.css`
- `web/src/trustContent.js`
- `web/src/resultViewModel.js`
- `web/tests/uiTrustDemo.test.mjs`

Implemented:

- Expanded synthetic demo set from 3 cards to 6 cards.
- Added reviewer demo path in the hero preview.
- Added result hierarchy rail: Evidence, Pattern, Limits, Next step.
- Added privacy nav access.
- Added no-safe-evidence fallback so summary-only results do not render as full reads.
- Added input helper text and connected it with `aria-describedby`.
- Added always-visible submit guidance for disabled private-text analysis states.
- Removed misleading `role="tablist"` from the mode selector because it behaves as a button group, not a true tab interface.
- Added shared amber `:focus-visible` treatment for major controls.
- Added feedback selected state via `.feedback-option-selected`.
- Added live status/alert semantics for feedback success/error messages.
- Added scroll-to-top on view transitions so demos land at the top of result screens.
- Reduced desktop hero height pressure with clamped H1 sizing.

### Mobile

Files:

- `mobile/src/screens/VibeSignalApp.js`
- `mobile/src/screens/matchScreenModel.js`
- `mobile/src/screens/ProviderSettingsScreen.js`
- `mobile/tests/matchScreenModel.test.js`
- `mobile/tests/uiTrustDemo.test.js`

Implemented:

- Ported all 6 synthetic demos into mobile.
- Added demo pattern pills to home and analyze demo cards.
- Added synthetic-result label on result screens.
- Added compact result context cards for fit read and evidence confidence labels.
- Added alignment/friction cue blocks using existing view-model fields.
- Added no-safe-evidence fallback in the mobile result model.
- Added always-visible submit guidance for empty text, missing consent, missing backend, and loading states.
- Added `accessibilityLabel` for the main permissioned conversation input.
- Added checkbox roles/states and `hitSlop` for:
  - Main Vibe Signal consent checkbox
  - Feedback consent checkbox
  - Provider screen analysis consent checkbox
  - Provider screen match consent checkbox
  - Provider screen optional external-provider consent checkbox
- Raised key mobile controls to at least 44px where practical.
- Added polite/assertive live-region metadata to mobile status/error text.
- Added per-option pending feedback state and selected feedback styling.

### Documentation

Files:

- `docs/research/ui_ux/ui_ux_research_sprint.md`
- `docs/design/ui_style_notes.md`
- `docs/design/ui_component_inventory.md`
- `docs/assets/screenshots/README.md`
- `docs/proof/closed_beta/ui_accessibility_qa.md`
- `docs/proof/closed_beta/web_beta_signup_readiness.md`

Implemented:

- Research sprint doc with UI improvements, safe product psychology principles, dark-pattern risks, mobile risks, trust/explainability improvements, and implementation shortlist.
- Expanded design-system notes with token map, typography, surfaces, cards, buttons, result surfaces, mobile layout rules, and known cleanup candidates.
- Component inventory for web and mobile UI surfaces.
- Synthetic-only screenshot checklist updated for expanded demos, fallback states, and feedback states.
- Accessibility QA proof doc with command matrix, viewport matrix, safety/privacy QA, and remaining manual QA.
- Web beta readiness note explaining the static/local beta form and review path.

## Synthetic Demo Inventory

Defined in:

- Web: `web/src/trustContent.js`
- Mobile: `mobile/src/screens/VibeSignalApp.js`

Current demo cards:

1. `unclear_ask`
   - Title: `Unclear ask`
   - Pattern: vague timing after a direct question.
   - Result strength: medium.

2. `pressure_urgency`
   - Title: `Pressure / urgency`
   - Pattern: urgency and consequence pressure.
   - Result strength: medium.

3. `repair_opportunity`
   - Title: `Repair opportunity`
   - Pattern: reassurance, repair wording, and a clear next step.
   - Result strength: high.

4. `low_signal_fallback`
   - Title: `Low-signal fallback`
   - Pattern: intentionally avoids over-reading short/context-light text.
   - Result state: `low_signal`.

5. `boundary_respecting_request`
   - Title: `Boundary-respecting request`
   - Pattern: clear low-pressure ask that leaves room to decline or delay.
   - Result strength: high.

6. `overloaded_message`
   - Title: `Overloaded message`
   - Pattern: cognitive load and narrowing the next ask.
   - Result strength: medium.

Important implementation note:

- Web and mobile currently duplicate synthetic demo data.
- If adding a new demo, update both files and both UI tests.
- Do not move this data into engine-owned files unless a separate shared-UI module is created deliberately.

## Result Model Changes

### Web result model

File: `web/src/resultViewModel.js`

Important functions:

- `buildTrustFirstResultView(result)`
- `buildLowSignalFallback(text)`
- `buildNoEvidenceFallback()`
- `buildSyntheticResult(demoId)`
- `isContextLightInput(text)`

Key behavior:

- Short/context-light text such as `hey`, `ok`, `lol sure`, and `fine` gets the low-signal fallback.
- Non-fallback results must have at least one safe evidence phrase.
- If a result lacks safe evidence phrases, `buildNoEvidenceFallback()` returns:
  - `resultState: "no_safe_evidence"`
  - `title: "No safe evidence phrase returned."`
  - no evidence details
  - safe next step to add context or use a synthetic example.

### Mobile result model

File: `mobile/src/screens/matchScreenModel.js`

Important functions:

- `buildMatchResultViewModel(result)`
- `buildLowSignalFallback(text)`
- `buildNoEvidenceFallback()`
- `buildMatchComposerState(...)`
- `isContextLightInput(text)`

Key behavior mirrors web:

- Low-signal fallback for short/context-light text.
- Separate no-safe-evidence fallback for summary-only result payloads.
- No numeric confidence is rendered in UI.
- `bandLabel`, `confidenceLabel`, `positiveFactors`, and `riskFactors` feed compact mobile context cards.

## UI Flow Guide

### Web landing demo path

1. Start at web home.
2. Primary CTA: `Try a synthetic example`.
3. CTA runs the first synthetic demo without private-text consent.
4. Result screen shows:
   - Main read
   - Signal strength pill
   - Evidence phrases
   - Pattern explanation
   - Cannot-infer block
   - Safe next-step block
   - Can/cannot lists
   - Metadata-only feedback panel
5. Feedback buttons stay disabled until bounded feedback consent is checked.

### Web private-text path

1. Go to analyze view.
2. User sees synthetic demo row first.
3. User sees `Before you paste` consent card.
4. Private text submit stays disabled until:
   - there is text
   - the permission checkbox is checked
   - request is not loading
5. Short/context-light text returns local fallback before network submission.

### Mobile landing demo path

1. Home screen shows hero, CTA, trust strip, six demos, how-it-works copy, and can/cannot lists.
2. Synthetic demo cards run without private-text consent.
3. Result screen shows synthetic-result label, main read, signal label, fit/evidence context, alignment/friction cues, evidence, explanation, limits, safe next step, and feedback.

### Mobile private-text path

1. Analyze screen shows inline synthetic demos first.
2. Private text area has accessibility label.
3. Consent card appears before private analysis.
4. Submit status is always visible:
   - empty text
   - missing consent
   - missing backend
   - loading
   - ready
5. Short/context-light text returns local fallback before backend use.

## Design System Rules

Preserved tokens and conventions:

- Background: deep navy `#0A0F1C` / `#0a0f1c`
- Surfaces: `#101827`, `#111827`, `#141e2f`, `#162033`
- Foreground: near-white `#eef2f7` / `#E8EAF0`
- Muted text: slate `#94a3b8`, `#8EA0BE`, `#64748B`, `#4A6080`
- Border: `#22314d`
- Primary accent: amber `#ffb84d`
- Positive accent: green `#7dd3a8`
- Risk accent: red `#ff7a7a`
- Radius: 8px
- Web font: Inter, then system UI fallback
- Mobile font: React Native system typography

Do not introduce:

- New font family
- New unrelated palette
- Large-radius card system
- Decorative blob/orb background language
- Marketing-like hero unrelated to the current app
- Score-first result layout
- Summary-only result rendering

## Accessibility Details

Web:

- Shared `:focus-visible` outline added for controls.
- Mode selector is a button group, not tablist.
- Text area uses `aria-describedby="conversation-helper consent-helper"`.
- Feedback success uses `role="status"` and `aria-live="polite"`.
- Feedback error uses `role="alert"`.

Mobile:

- Main app custom checkboxes use:
  - `accessibilityRole="checkbox"`
  - `accessibilityState={{ checked: ... }}`
  - `hitSlop={6}`
- Provider screen custom checkboxes now use the same role/state pattern.
- Status text uses `accessibilityLiveRegion="polite"`.
- Error text uses `accessibilityLiveRegion="assertive"`.
- Main text input uses `accessibilityLabel="Permissioned conversation text"`.
- Core touch targets were raised to 44px+ where practical.

Known remaining accessibility gaps:

- Full screen-reader pass still required.
- Keyboard-only web focus-order test still should be run manually.
- Rendered accessibility automation is not yet built.
- Real-device mobile dynamic text QA remains required.

## Safety And Privacy Implementation

Feedback:

- Web: `web/src/api.js` still sends feedback metadata only:
  - `feedback_event_id`
  - `match_id`
  - `rating`
  - `feedback_tag`
  - `comment: ""`
  - `consent_to_store_feedback`
- Mobile: `mobile/src/services/vibeBackendClient.js` still sends bounded feedback metadata only.
- No free-text feedback field was added.
- No raw message text is attached to feedback payloads.

Consent:

- Synthetic demos do not require private-text consent.
- Private paste requires explicit permission checkbox.
- Short/context-light input can return local fallback before backend submission.

Scanner posture:

- Public-copy scanner was not weakened.
- No-raw-content scanner was not weakened.
- Restricted-artifact scanner was not weakened.

## Files Not Touched

These were intentionally not edited:

- `src/vibesignal_ai/`
- `backend/routes/analyze.py`
- `tools/generate_synthetic_whatsapp_fixtures.py`
- `tools/run_synthetic_fixture_regression.py`
- `reports/engine_eval/*.jsonl`
- `data/synthetic/whatsapp/*.jsonl`
- Engine precision tests

The only provider-screen edit was accessibility metadata on existing custom checkbox controls.

## How To Run Locally

### Web

```bash
cd web
npm ci
npm run dev -- --port 5174
```

If 5174 is busy, Vite will choose another port. Open the reported local URL.

Useful paths:

- Landing: default app view.
- Synthetic first run: click `Try a synthetic example`.
- Analyze form: click `Back to input` from results, or navigate through the app controls.
- Consent gate: analyze form section `Before you paste`.
- Low-signal fallback: run the `Low-signal fallback` synthetic demo, or enter a short context-light private input after consent.

### Mobile

```bash
cd mobile
npm ci
npx expo start
```

Useful paths:

- Home screen: default `VibeSignalApp`.
- Synthetic demo: tap any demo card.
- Analyze screen: tap `See how it works` from mobile home.
- Result screen: synthetic demo result or private analysis response.
- Provider settings checkboxes: `ProviderSettingsScreen.js` contains provider consent controls with accessibility metadata.

## How To Add Another Synthetic Demo

1. Add the demo to `web/src/trustContent.js` in `SYNTHETIC_DEMOS`.
2. Add the same demo to `mobile/src/screens/VibeSignalApp.js` in `SYNTHETIC_DEMOS`.
3. Include:
   - `id`
   - `title`
   - `exchange`
   - `highlight`
   - `previewPattern`
   - `actionLabel` on web
   - `requiresPrivateConsent: false` on web
   - `result`
4. Ensure result includes:
   - `match_id`
   - `synthetic: true`
   - `requiresPrivateConsent: false`
   - `signal_strength`
   - `safe_explanation`
   - `evidence` with `safe_phrase` unless intentionally low-signal
   - `safe_next_steps`
5. Update tests:
   - `web/tests/uiTrustDemo.test.mjs`
   - `mobile/tests/uiTrustDemo.test.js`
6. Run:

```bash
cd web && npm test
cd mobile && npm test
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
```

## How To Modify Result Hierarchy Safely

Use this required order:

1. Main read
2. Signal strength
3. Evidence phrase(s)
4. Pattern explanation
5. What this cannot tell you
6. Safe next step
7. Feedback buttons

Rules:

- Do not show numeric confidence.
- Do not show full result if safe evidence phrases are missing.
- Keep evidence above interpretation.
- Keep cannot-infer visible before or near feedback.
- Keep safe next steps low-pressure and optional.
- Do not add persuasion or certainty language.

## Validation Run For PR #28

Post-rebase validation on latest `origin/main`:

```bash
cd web && npm test
```

Result: passed 17/17.

```bash
cd web && npm run build
```

Result: passed.

```bash
cd mobile && npm test
```

Result: passed 137/137.

```bash
cd mobile && npx expo config --type public
```

Result: passed.

```bash
python scripts/check_public_copy_safety.py
```

Result: passed, 16 allowlisted findings, 0 unallowlisted.

```bash
python scripts/check_no_raw_content_leaks.py
```

Result: passed, 0 findings.

```bash
python scripts/check_vibe_restricted_artifacts.py --staged
```

Result: passed, 16 staged paths checked.

```bash
git diff --check
```

Result: passed.

Requested static grep:

```bash
git grep -ni "find out what they really think|detect cheating|cheating detector|they like you|hidden intent|diagnose|narcissist|attachment style|ADHD|autism|manipulate|make them|win them back|guaranteed|this proves|emotional truth|validated accuracy|production-grade" .
```

Result: passed with no output in the final run.

Skipped:

- Web lint: no `lint` script in `web/package.json`.
- Web typecheck: no `typecheck` script in `web/package.json`.
- Mobile lint: no `lint` script in `mobile/package.json`.
- Mobile typecheck: no `typecheck` script in `mobile/package.json`.
- Python py_compile/pytest: skipped because no Python files were changed.
- Real-device mobile QA: not available in this sprint.

## Browser QA

Local web server:

```bash
cd web
npm run dev -- --port 5173
```

5173 was occupied during QA, so Vite served on:

```text
http://localhost:5174/
```

Desktop checks passed:

- Hero copy visible.
- Synthetic CTA visible.
- Six demo cards visible.
- Trust strip visible.
- Reviewer demo flow visible.
- Synthetic result rendered.
- Evidence phrases visible.
- Cannot-infer block visible.
- Safe next step visible.
- Feedback disabled before consent.
- Console errors: 0.

Mobile viewport checks passed at 390x844:

- No horizontal overflow.
- Hero visible.
- Expanded demo cards visible.
- Trust strip visible.
- Synthetic result rendered.
- Evidence phrases visible.
- Limits visible.
- Feedback visible.
- Consent gate visible.
- Disabled-submit reason visible.
- Console errors: 0.

Low-signal browser QA:

- Browser text entry was blocked by the in-app browser virtual clipboard.
- Synthetic low-signal demo was used instead.
- Low-signal fallback rendered.
- Try-synthetic CTA rendered.
- Console errors: 0.

Local screenshots captured during QA:

- `/tmp/vibe-signal-ui-ux-desktop-result.png`
- `/tmp/vibe-signal-ui-ux-mobile-result.png`
- `/tmp/vibe-signal-ui-ux-low-signal.png`

No screenshots were committed.

## Research Sources Used

External references cited in `docs/research/ui_ux/ui_ux_research_sprint.md`:

- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- Google PAIR Explainability + Trust: https://pair.withgoogle.com/guidebook-v2/chapter/explainability-trust/
- W3C WCAG 2.2: https://w3c.github.io/wcag/guidelines/22/
- W3C Focus Appearance understanding: https://w3c.github.io/wcag/understanding/focus-appearance.html
- FTC dark-pattern guidance: https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf
- Apple Human Interface Guidelines, Buttons: https://developer.apple.com/design/human-interface-guidelines/buttons
- Material Design text fields: https://m1.material.io/components/text-fields.html
- Material Design errors: https://m1.material.io/patterns/errors.html

## Current PR State

PR:

- https://github.com/keithtgrehan/vibe-signal/pull/28

State at handoff:

- Draft PR open.
- Branch pushed.
- Worktree was clean after commit/push.
- The PR contains one implementation commit:
  - `7be952815fcf74344d00143cbec80fb64b196820` — `Strengthen trust-first UI and demo experience`

## Remaining Gaps

Required before closed-beta invites:

- Real-device mobile QA.
- Screen reader smoke pass.
- Legal review.
- Synthetic-only screenshot set committed or attached where appropriate.

Recommended next UI branch:

- Normalize older mobile provider/paywall/quota/share-card visual systems toward the documented navy/amber/slate 8px system.
- Add rendered web/mobile accessibility tests beyond string/model tests.
- Consider shared UI content extraction if web/mobile synthetic demo duplication becomes a maintenance burden.

Existing dependency note:

- `npm ci` in mobile reported existing transitive npm audit advisories. This sprint did not change dependency versions and did not attempt dependency upgrades.

## Conflict Risk

Conflict risk with engine work is low.

Reason:

- This branch only changes UI, UI tests, and documentation.
- It was rebased onto `origin/main` after PR #27.
- It does not edit engine-owned routes, packages, fixtures, reports, or precision tests.

Potential conflict areas:

- Future UI branches that also edit `web/src/App.jsx`, `web/src/styles.css`, `web/src/trustContent.js`, `mobile/src/screens/VibeSignalApp.js`, or `mobile/src/screens/matchScreenModel.js`.
- Future docs branches editing `docs/design/ui_style_notes.md` or `docs/assets/screenshots/README.md`.

## Implementation Checklist For Future Agents

Before editing:

1. Check current branch and status.
2. Pull/rebase onto latest `origin/main`.
3. Read:
   - `docs/design/ui_style_notes.md`
   - `docs/design/ui_component_inventory.md`
   - `docs/research/ui_ux/ui_ux_research_sprint.md`
   - `docs/proof/closed_beta/ui_accessibility_qa.md`
4. Confirm no engine files need to be touched.

When editing:

1. Keep synthetic-first path obvious.
2. Keep private paste consent-gated.
3. Keep result hierarchy evidence-first.
4. Keep no-safe-evidence fallback.
5. Keep feedback metadata-only.
6. Keep UI in the existing dark navy/amber/slate system.
7. Update both web and mobile demo content if demo cards change.
8. Update tests when UI contracts change.

Before PR:

```bash
cd web && npm test
cd web && npm run build
cd mobile && npm test
cd mobile && npx expo config --type public
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
git status --short
```

Run lint/typecheck only if scripts are added later.

