# Guided Reply, Redaction, And Evidence UX Research

Date: 2026-06-04
Branch: `codex/guided-reply-redaction-evidence-ui`

## Sources Reviewed

Local:

- `docs/research/ui_ux/simple_ui_redesign_research.md`
- `docs/design/simple_ui_information_architecture.md`
- `docs/design/simple_ui_copy_system.md`
- `docs/design/simple_ui_visual_notes.md`
- `docs/agents/ui_ux_product_design_agent.md`
- `README.md`

Public references:

- Google PAIR Explainability + Trust: https://pair.withgoogle.com/guidebook-v2/chapters/explainability-trust/
- Microsoft HAX Toolkit: https://www.microsoft.com/en-us/haxtoolkit/
- Microsoft overreliance guidance: https://learn.microsoft.com/en-us/ai/playbook/technology-guidance/overreliance-on-ai/overreliance-on-ai
- Apple HIG Privacy: https://developer.apple.com/design/human-interface-guidelines/privacy/
- Apple HIG Machine Learning: https://developer.apple.com/design/human-interface-guidelines/machine-learning/
- Material Design chips and selection controls: https://m2.material.io/components/chips and https://m1.material.io/components/selection-controls.html
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- FTC dark-pattern report summary: https://www.ftc.gov/node/79647

## Guided Goal Selection

- Keep one selected goal visible in the result header as "Your goal."
- Treat goals as local presentation choices, not analysis inputs.
- Use goal choice to adjust next-step wording and reply-helper defaults.
- Keep goal options stable in order so mobile users do not relearn the control.

## Evidence Tables

- Put quote, pattern, explanation, and evidence quality in one scan path.
- Avoid numeric scores. Evidence quality should describe support strength, not product accuracy.
- Use stacked evidence cards on narrow screens instead of horizontal scrolling.
- Do not render a full evidence table when no safe quote exists.

## Redaction Helpers

- Run redaction before submit and show the edited text to the user.
- Use modest language: "helps remove obvious identifiers."
- Keep undo local and temporary.
- Replace only obvious emails, phone numbers, links, handles, and simple address-like patterns.

## Safe Draft Suggestions

- Label outputs as "Draft option."
- Offer multiple editable choices so the user remains in control.
- Keep draft options tied to communication tasks: ask, lower pressure, boundary, repair, timing.
- Never imply outcome control or private-state knowledge.

## Comparison Views

- Use neutral labels like "earlier" and "later."
- Describe visible wording changes only: specificity, timing, pressure, repair, warmth.
- Route weak comparisons to low-signal fallback.
- Do not use comparison copy as a truth or intent verdict.

## Cue-Level Feedback

- Keep feedback bounded to metadata: result id, cue id, cue family, evidence quality, goal, context, style, synthetic flag, low-signal flag.
- Do not include quote text, pasted text, draft text, or free-form comments.
- Treat feedback as review prioritization, not a human-reviewed label.

## Top Risks To Avoid

1. Goal selector appears to change analysis truth.
2. Evidence quality is mistaken for real-world accuracy.
3. Drafts sound like instructions to control the other person.
4. Redaction copy overstates privacy guarantees.
5. Comparison mode implies private motives.
6. Feedback accidentally includes evidence quote text.
7. Low-signal fallback feels like a dead end.
8. Mobile cards become too tall to scan.
9. Too many controls compete above the fold.
10. Consent and privacy actions become visually secondary.

## Implementation Recommendations

1. Add evidence quality labels directly to evidence rows.
2. Use local draft templates with no network request.
3. Keep comparison mode local unless a reviewed backend contract exists.
4. Send feedback metadata only, with cue ids instead of quote text.
5. Keep redaction reversible in local state only.
6. Preserve the Demo Mode first path.
7. Use browser QA at desktop and 390px mobile.
8. Re-run public-copy and no-raw-content scanners before PR.
