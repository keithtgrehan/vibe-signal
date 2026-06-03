# Vibe Signal UI Style Notes

## Observed Palette / Tokens

- Background: deep navy `#0A0F1C` / `#0a0f1c`, with subtle navy gradients in web.
- Surfaces: dark blue-gray cards around `#101827`, `#111827`, `#141E2F`, and `#162033`.
- Text: near-white foreground around `#EEF2F7` / `#E8EAF0`.
- Muted text: slate blue-gray around `#94A3B8`, `#8EA0BE`, and quieter `#64748B` / `#4A6080`.
- Borders: muted navy-slate `#22314D` or low-opacity slate borders.
- Primary accent: amber `#FFB84D` with darker amber `#E59A20`.
- Semantic accents: green `#7DD3A8` for safe/positive states and red `#FF7A7A` for errors/risk.

## Typography

- Web uses Inter first, then system UI fallbacks.
- Mobile uses React Native system typography with the same weight rhythm.
- Headings are heavy, compact, and high contrast.
- Body text uses muted slate, medium line height, and no negative letter spacing.
- Utility labels use uppercase amber text, small size, and heavy weight.

## Cards and Buttons

- Cards use 8px radius, subtle slate borders, dark translucent surfaces, and restrained shadows.
- Buttons use 8px radius, 46-50px minimum height, heavy labels, and amber primary fills.
- Secondary buttons keep transparent/dark surfaces with muted borders.
- Evidence phrases use bordered dark quote cards, not bright callouts.
- Cannot-infer blocks use calmer muted-slate treatment; safe next-step blocks use subdued green.

## Spacing / Radius / Shadow

- Radius convention is 8px across cards, controls, inputs, icons, and pills.
- Layout uses compact but breathable gaps: 8-12px inside controls, 16-18px between cards, 28-34px between major sections.
- Web page width stays constrained around 1120px, with narrow pages around 850px.
- Shadows are used on primary surface cards only; secondary evidence/limit blocks can be flatter.

## Preservation Rule

Do not introduce a new font family, color palette, large-radius card style, decorative gradient-orb treatment, or unrelated component language. New UI should reuse the dark navy surface system, amber primary action, muted slate borders, 8px radius, compact cards, and evidence-first hierarchy.
