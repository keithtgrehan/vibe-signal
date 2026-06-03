# Vibe Signal UI Component Inventory

Date: 2026-06-03

## Files Audited

- `web/src/App.jsx`
- `web/src/styles.css`
- `web/src/trustContent.js`
- `web/src/resultViewModel.js`
- `mobile/src/screens/VibeSignalApp.js`
- `mobile/src/screens/matchScreenModel.js`
- `mobile/src/screens/ProviderSettingsScreen.js`
- `mobile/src/components/PaywallCard.js`
- `mobile/src/components/QuotaBadge.js`
- `mobile/src/components/SignalShareCard.js`

## Web Components

| Component | Source | Styling | States | Notes |
| --- | --- | --- | --- | --- |
| Top nav | `TopNav`, `.top-nav`, `.brand-lockup`, `.nav-links` | Navy sticky header, slate border, amber brand mark | Hover, focus-visible | Adds persistent privacy access. |
| Button | `Button`, `.button-*` | 8px radius, amber primary, dark secondary | Hover, disabled, focus-visible | Used across landing, analyze, result, beta. |
| Hero | `.hero-grid`, `.hero-copy`, `.hero-visual` | Dark card surfaces, subtle navy/amber gradient | Responsive single-column | H1 is clamped to reduce desktop height pressure. |
| Trust strip | `.trust-strip` | Compact slate-bordered pills | Responsive stack | Preserves existing trust wording. |
| Synthetic demo card | `.synthetic-demo-card`, `.demo-card-header`, `.synthetic-exchange` | Dark cards, amber pattern pill, monospace exchange | Button hover/focus | Six synthetic-only examples. |
| Result preview | `.result-preview-card` | Evidence-first card | Static | Shows signal, evidence, limits, safe next step. |
| Analyze form | `.analyze-surface`, `.segmented-control`, `textarea`, `.consent-card` | Dark form controls, green consent box | Focus-visible, disabled, live status | Mode selector is a button group, not tab semantics. |
| Match result | `.result-hero`, `.evidence-detail`, `.cannot-infer-block`, `.safe-next-card` | Main read card, flat evidence/limits blocks | Low-signal/no-evidence fallback | No numeric confidence displayed. |
| Feedback panel | `.feedback-panel`, `.feedback-option-selected` | Secondary buttons with selected green state | Consent-gated, disabled, live status/alert | Payload remains metadata-only. |
| Beta form | `.closed-beta-cta`, `.legal-surface` | Same dark card/button/input language | Disabled until local fields ready | Static local form only. |

## Mobile Components

| Component | Source | Styling | States | Notes |
| --- | --- | --- | --- | --- |
| Shell | `Shell`, `styles.safe`, `styles.content` | Deep navy, single-column scroll | Keyboard-safe | Dark-only beta surface. |
| Header | `Header`, `styles.brand`, `styles.headerButton` | Logo image, dark bordered legal button | Pressed, 44px target | Preserves system typography. |
| Buttons | `PressableText`, `primaryButton`, `secondaryButton` | Amber primary, dark secondary | Pressed, disabled, role button | Default hitSlop applied. |
| Hero | `HomeScreen`, `styles.hero` | Dark card, amber eyebrow | Scroll responsive | Synthetic CTA remains primary. |
| Demo cards | `SYNTHETIC_DEMOS`, `styles.demoCard`, `demoPatternPill` | Dark cards, amber pattern pill | Pressed | Six synthetic examples match web. |
| Analyze form | `AnalyzeScreen`, `textArea`, `disclosureBox`, `checkboxRow` | Dark text area, green consent box | Checkbox role/state, live status | Always-visible submit reason. |
| Match result | `MatchResult`, `resultHero`, `resultSignalGrid`, `evidenceDetail` | Main read, context stat cards, evidence cards | Synthetic result pill, low-signal fallback | Adds fit/confidence labels without numeric score. |
| Feedback | `FEEDBACK_OPTIONS`, `feedbackButton`, `feedbackButtonSelected` | Metadata buttons in wrapped rows | Consent-gated, pending, selected | No free-text feedback. |
| Provider checkboxes | `ProviderSettingsScreen.js` | Existing provider style | Checkbox role/state, hitSlop | Accessibility metadata only; visual migration deferred. |

## State Variants

- Hover: web nav/buttons.
- Focus: web buttons, textareas, inputs, selects via amber `:focus-visible`.
- Pressed: mobile opacity state.
- Disabled: web/mobile opacity reduction.
- Success: subdued green status and selected feedback state.
- Error: red text or red-tinted alert banner.
- Low signal: amber-tinted fallback card.
- No safe evidence: fallback state that blocks summary-only reads.

## Inconsistency Backlog

- Normalize older provider/paywall/quota/share-card visual systems to the documented dark navy/amber/slate 8px system.
- Add rendered accessibility tests for focus order, role/state coverage, and viewport overflow.
- Consider a shared trust-content module only if web/mobile drift becomes costly; avoid moving this into engine code.

## Boundary

This is a UI inventory. It should not drive edits in `src/vibesignal_ai/`, backend analysis routes, synthetic fixture generators, regression runners, engine reports, or engine precision tests.
