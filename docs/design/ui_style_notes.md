# Vibe Signal UI Style Notes

Date updated: 2026-06-03

## Purpose

These notes document the existing Vibe Signal UI language so future UI work improves polish without drifting into a new brand. UI changes should preserve the current dark navy, amber, slate, compact-card system unless a separate design-system migration is explicitly approved.

## Observed Palette / Tokens

Web tokens live in `web/src/styles.css`:

- `--background`: deep navy `#0a0f1c`
- `--surface`: dark blue-gray `#101827`
- `--surface-strong`: `#141e2f`
- `--surface-soft`: `#172238`
- `--foreground`: near-white `#eef2f7`
- `--muted`: slate `#94a3b8`
- `--muted-strong`: quieter slate `#64748b`
- `--border`: navy-slate `#22314d`
- `--primary`: amber `#ffb84d`
- `--primary-strong`: darker amber `#e59a20`
- `--positive`: green `#7dd3a8`
- `--risk`: red `#ff7a7a`
- `--radius`: `8px`

Mobile `COLORS` live in `mobile/src/screens/VibeSignalApp.js` and intentionally mirror the same navy/amber/slate/green/red language.

## Typography

- Web uses Inter first, then system UI fallbacks.
- Mobile uses React Native system typography.
- Headings are heavy, compact, high-contrast, and use letter spacing `0`.
- Body text uses muted slate with medium line height.
- Eyebrows and utility labels use small uppercase amber text with heavy weight.
- Do not introduce a new font family in UI polish branches.

## Backgrounds And Surfaces

- Web uses a subtle navy gradient with a restrained amber wash near the top.
- Mobile shell is flat deep navy.
- Primary surfaces use dark cards with slate borders.
- Evidence and limit blocks are flatter than hero/shell cards.
- Avoid decorative blobs, new gradient palettes, or large-radius editorial cards.

## Cards, Radius, Spacing, Shadow

- Radius convention is 8px across cards, buttons, inputs, pills, icon containers, and quote cards.
- Major web pages constrain width around 1120px; narrow flows around 850px.
- Internal card padding generally sits between 13px and 22px on mobile and 18px to 32px on web.
- Common gaps: 8-12px inside compact controls, 16-18px between cards, 28-34px between major sections.
- Use shadow only for elevated shell/hero/result cards. Evidence, cannot-infer, and safe-next blocks should remain calmer.

## Buttons And Interactive States

- Primary actions use amber fills and dark navy text.
- Secondary actions use dark translucent surfaces, slate borders, and near-white text.
- Web buttons are 46px+ tall; mobile primary/secondary controls target 48-50px.
- Custom mobile controls should use at least 44px tap targets where practical.
- Web focus uses a shared amber `:focus-visible` outline.
- Feedback buttons use the same secondary style until selected, then a subdued green state.

## Result Surfaces

- Results must keep this order: main read, signal strength, evidence, pattern explanation, limits, safe next step, feedback.
- Evidence phrases use dark quote cards with slate borders.
- Signal and pattern chips use amber outlines and fills.
- Cannot-infer blocks use muted slate treatment.
- Safe-next blocks use subdued green treatment.
- No normal result should render without a safe evidence phrase.

## Mobile Layout Rules

- Mobile is single-column, scroll-first, and dark-only in this beta.
- Tap targets should be usable with thumbs and should not rely only on small text.
- Long lists should keep headers and limits visible through compact cards.
- Keyboard-safe layout is handled by `KeyboardAvoidingView` and `ScrollView`.
- Dark/light mode is not currently supported; do not half-add light mode without contrast QA.

## Known Exceptions / Cleanup Candidates

The provider, paywall, quota, and share-card surfaces use older cream/white or larger-radius styling in some places:

- `mobile/src/screens/ProviderSettingsScreen.js`
- `mobile/src/components/PaywallCard.js`
- `mobile/src/components/QuotaBadge.js`
- `mobile/src/components/SignalShareCard.js`

This sprint documents those as cleanup candidates rather than mixing a broader visual migration into the trust/demo polish branch.

## Preservation Rule

Do not introduce inconsistent styles: no new color palette, no new font, no large-radius card system, no decorative background treatment, no unrelated component language. Reuse the dark navy surfaces, amber primary action, muted slate borders, 8px radius, compact cards, and evidence-first hierarchy.
