# Vibe Signal UI/UX Research Sprint

Date: 2026-06-03
Branch: `codex/ui-ux-product-design-research-upgrade`

## Scope

This sprint focused on trust-first AI UX, explainable result screens, synthetic demo onboarding, mobile-first form ergonomics, accessibility basics, and closed-beta demo readiness. The work stayed inside web/mobile UI, UI tests, and documentation. Engine-owned files were not in scope.

Local sources reviewed:

- `docs/design/ui_style_notes.md`
- `docs/proof/closed_beta/`
- `docs/research/`
- `README.md`
- `docs/ethical_engagement_principles.md`
- `docs/legal_safe_output_policy.md`

External references used:

- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- Google PAIR Guidebook, Explainability + Trust: https://pair.withgoogle.com/guidebook-v2/chapter/explainability-trust/
- W3C WCAG 2.2: https://w3c.github.io/wcag/guidelines/22/
- W3C Focus Appearance understanding: https://w3c.github.io/wcag/understanding/focus-appearance.html
- FTC dark-pattern guidance: https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf
- Apple Human Interface Guidelines, Buttons: https://developer.apple.com/design/human-interface-guidelines/buttons
- Material Design text fields and error patterns: https://m1.material.io/components/text-fields.html and https://m1.material.io/patterns/errors.html

## Top 20 UI Improvements

1. Keep synthetic examples as the first successful path.
2. Put the primary CTA on the synthetic demo, not private paste.
3. Show a short reviewer demo path in the hero preview.
4. Use a compact result hierarchy rail: evidence, pattern, limits, next step.
5. Expand synthetic demos beyond the first three scenarios.
6. Make the low-signal demo visible as a positive safety behavior.
7. Treat missing safe evidence as a fallback, not a summary-only result.
8. Add always-visible disabled-submit guidance.
9. Keep consent compact and near private input.
10. Add helper text for input format.
11. Show signal strength as a phrase, not a number.
12. Keep quoted evidence above pattern explanation.
13. Add selected/pending feedback states.
14. Keep feedback metadata-only and consent-gated.
15. Add shared web focus-visible styles.
16. Increase mobile tap targets to at least 44px where practical.
17. Add checkbox roles/states for custom mobile checkbox controls.
18. Make status/error updates announceable.
19. Add persistent privacy/legal access in navigation.
20. Update screenshot and QA docs around synthetic-only capture.

## Safe Product Psychology Principles

1. Calibrated trust: show what is known and what is not known.
2. User agency: present next steps as options.
3. Evidence before interpretation: quote safe phrases first.
4. Low cognitive load: one primary action per surface.
5. Progressive disclosure: simple read first, details below.
6. Privacy by default: synthetic-first and minimized private text.
7. Friction where risk rises: consent before private paste.
8. Predictable feedback: no variable rewards or suspense loops.
9. Repair orientation: prefer clearer, lower-pressure wording.
10. Honest uncertainty: no result when evidence is too thin.

## Dark-Pattern Risks To Avoid

1. Scarcity or urgency around beta access.
2. Shame-based or fear-based relationship copy.
3. Prechecked consent.
4. Buried privacy, deletion, export, or legal access.
5. Emotional certainty language.
6. Persuasion optimization.
7. Hidden scoring that implies personal truth.
8. Repeated prompts that encourage compulsive checking.
9. Ambiguous disabled states.
10. Unsupported quality, compliance, or review claims.

## Mobile UX Risks

1. Keyboard covering the textarea or CTA.
2. Tap targets under 44px.
3. Long result cards hiding the limits block.
4. Feedback buttons wrapping into cramped rows.
5. Legal controls overflowing on narrow screens.
6. Disabled submit without a visible reason.
7. Muted text losing contrast in dense cards.
8. Scroll position landing below result headers.
9. Offline/private-backend gaps feeling like product failure.
10. Dynamic text sizes breaking pills or quoted evidence cards.

## Trust And Explainability Improvements

1. Label result flow as evidence-first.
2. Use signal strength labels as evidence-quality descriptors.
3. Render no full result without at least one safe quoted phrase.
4. Show limits before feedback.
5. Separate low-signal and no-safe-evidence fallbacks.
6. Add clear next steps that do not pressure the user.
7. Make synthetic demo provenance visible.
8. Keep feedback copy explicit about metadata-only submission.
9. Keep privacy/legal routes visible.
10. Keep screenshot proof synthetic-only.

## Implementation Shortlist Completed

- Expanded web and mobile synthetic demos to six scenarios.
- Added web reviewer demo flow and explainability rail.
- Added no-safe-evidence fallback in web and mobile result view models.
- Added web focus-visible treatment and mobile checkbox/tap-target/accessibility updates.
- Added mobile always-visible submit guidance and result context cards.
- Added metadata-feedback selected/pending states.
- Added required design, research, screenshot, and QA docs.

## Deferred Gaps

- Full rendered accessibility test automation remains future work.
- Mobile provider, paywall, quota, and share-card surfaces still need a separate visual-system cleanup pass.
- Real-device mobile QA and legal review are still required before tester invites.
