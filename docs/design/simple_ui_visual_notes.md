# Simple UI Visual Notes

Date: 2026-06-04

## Current Audit

The prior web UI was polished but visually dense: a hero card, phone preview, reviewer strip, trust strip, six visible demo cards, result preview, how-it-works cards, limits grid, safety band, beta CTA, and FAQ all competed for attention.

The redesign keeps the existing visual language and removes hierarchy noise.

## Visual Direction

- Dark navy background and surfaces.
- Amber primary actions and selected states.
- Slate borders.
- Green safe-next/consent accents.
- Red error accents.
- Inter/system typography.
- 8px radius.
- Compact, low-shadow panels.

## Density Changes

- One main panel above the fold.
- Goal selector before mode choice.
- Segmented control for Demo / Analyze.
- Three visible demos first.
- More examples expansion for lower-priority demos.
- Context chips and style cards stay compact.
- Result panel is the main artifact.

## Desktop Layout

- Left: controls and active mode content.
- Right: result preview/result panel.
- The result panel is sticky on desktop only.

## Mobile Layout

- Single-column guided flow.
- Sticky result disabled.
- Buttons and selectors stay at least 44px high where practical.
- Long labels wrap inside their controls.

## Accessibility Notes

- Native buttons for selectors.
- `role="radiogroup"` and `role="radio"` for segmented/chip choices.
- Visible amber focus outline.
- Consent checkbox remains native.
- Loading/error/status copy uses live/status/alert affordances.

## Mobile Implementation Status

Mobile code is intentionally deferred in this sprint. The web redesign changes the first-use product structure substantially; directly mirroring it in the mature Expo screen would risk a broad test rewrite and cramped controls. Mobile tests still validate the current mobile-safe flow.
