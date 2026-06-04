# Simple UI Redesign Research

Date: 2026-06-04
Branch: `codex/simple-ui-demo-analyze-redesign`

## Sources Reviewed

Local: `README.md`, `docs/design/ui_style_notes.md`, `docs/design/ui_component_inventory.md`, `docs/research/ui_ux/ui_ux_research_sprint.md`, `docs/agents/ui_ux_product_design_agent.md`, `docs/control_room/`.

Public references:

- Google PAIR Explainability + Trust: https://pair.withgoogle.com/guidebook-v2/chapters/explainability-trust/
- Microsoft HAX Toolkit: https://www.microsoft.com/en-us/haxtoolkit/
- Apple HIG segmented controls: https://developer.apple.com/design/human-interface-guidelines/segmented-controls
- Material selection controls/chips: https://m1.material.io/components/selection-controls.html and https://m2.material.io/components/chips
- WCAG 2.2 focus and target guidance: https://www.w3.org/WAI/WCAG22/quickref/
- FTC dark-pattern report: https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf

## Top 15 UI Changes

1. Replace multi-section first viewport with one guided product workspace.
2. Add goal selector before Demo/Analyze.
3. Use a two-option segmented control for Demo Mode and Analyze Text.
4. Default to Demo Mode.
5. Keep only three primary demo examples visible.
6. Put extra demos behind More examples.
7. Place context and analysis style in compact choice controls.
8. Keep context/style/goal client-side only.
9. Show result preview beside the input, not below many landing sections.
10. Use result labels: What stands out, Evidence, Pattern, What this cannot tell you, Safer next step.
11. Make low-signal fallback feel like a safe product behavior.
12. Keep one dominant primary action in the active mode.
13. Collapse repeated safety copy into one consent card plus one boundary section.
14. Keep footer/legal links short and calm.
15. Preserve navy/amber/slate/green/red styling and 8px radii.

## Top 10 Wording Improvements

1. Hero: “Understand message patterns without guessing motives.”
2. Subcopy: “Try a synthetic demo or paste permissioned text.”
3. Mode: “Demo Mode” and “Analyze Text.”
4. Goal helper: goal shapes wording only.
5. Context helper: context does not infer intent.
6. Style label: “Analysis style,” not model.
7. Consent: remove names, phone numbers, addresses, sensitive details.
8. Result: “What this cannot tell you.”
9. Low signal: “Not enough context to read safely.”
10. Error: “The backend may be waking up. Please try again in a moment.”

## Top 10 Safe Product Psychology Principles

1. Reduce first-screen choices to goal, mode, context/style, action.
2. Put the safest first success path first.
3. Show evidence before interpretation.
4. Preserve user agency with optional next steps.
5. Keep uncertainty visible.
6. Avoid urgency, shame, FOMO, streaks, and fake scarcity.
7. Add friction only where risk rises: private input and feedback storage.
8. Avoid authority signals that imply validation or diagnosis.
9. Make fallback states useful, not punitive.
10. Keep manual gates human.

## Top 10 Things To Remove Or Collapse

1. Hero eyebrow.
2. Separate hero visual card stack.
3. Dense reviewer-flow strip above the fold.
4. Full synthetic-card grid above the fold.
5. Repeated safety sections.
6. FAQ cards on first pass.
7. Separate analyze/results route split for the main demo.
8. Dashboard-like metric language.
9. Multiple competing secondary CTAs.
10. Repeated card wrappers around every section.

## Top 10 Mobile UX Risks

1. Goal selector becomes too tall.
2. Context chips wrap unpredictably.
3. Result panel can fall too far below controls.
4. Sticky result panel must disable on mobile.
5. Textarea plus keyboard can hide CTA.
6. More examples expansion can crowd the screen.
7. Long labels need wrapping without clipped buttons.
8. Tap targets must remain at least 44px where practical.
9. Muted helper text can lose contrast.
10. Feedback buttons can wrap into cramped rows.

## Implementation Shortlist

- Implement web first with one main workspace and client-side goal/context/style controls.
- Keep `/api/analyze` payload unchanged.
- Keep synthetic demos consent-free and private text consent-gated.
- Defer mobile code changes if mirroring the new flow risks breaking the mature mobile test surface.
- Validate with web tests/build, mobile tests/config, safety scanners, static grep, and rendered browser QA.
