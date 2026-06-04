# Minimal Human UI Agent Findings

## Agent UI Simplification

- Current clutter: goal cards, context chips, style cards, comparison tools, three primary demos, extra demos, trust chips, can/cannot panels, evidence table, reply helper, and feedback controls all compete on the same page.
- Minimal IA: nav, hero, demo/result, analyze text, how it works, trust footer.
- Remove: goal selector, context selector, analysis style selector, comparison mode from the landing flow, repeated safety panels, and the trust-chip wall.
- Collapse: additional synthetic examples and feedback actions.
- Merge: pattern and interpretation into "What it could mean"; can/cannot content into one short footer line.

## Agent Human Copy / Conversion

- Public copy should sound like a calm assistant, not a compliance report.
- Use "What stands out," "Evidence," "What it could mean," "Safer reply," and "Limits."
- Lead with curiosity and relief: a user can stop guessing and inspect the words before replying.
- CTA language should be short: "Run a demo" and "Analyze text."
- Avoid fear, urgency pressure, jealousy, secret-meaning claims, or dark-pattern loops.

## Agent Safe Inference / Explainability

- Strongest safe language: Vibe Signal shows observable wording patterns, ambiguity, pressure, unclear asks, repair openings, and safer reply options.
- Result explanations must quote evidence before interpretation.
- Limits should be short and human: "This does not tell you what they feel or intend."
- Feedback remains metadata-only and should stay downstream of the result.
- Consumer UI must not claim hidden intent, emotional truth, deception certainty, attraction prediction, diagnosis, therapy, legal advice, or manipulation ability.

## Agent Implementation Planner

- Web files to change: `web/src/App.jsx`, `web/src/styles.css`, `web/src/trustContent.js`, `web/src/resultViewModel.js`, and focused tests under `web/tests`.
- Docs to add: `docs/research/ui_minimal_redesign/final_thesis.md` and `docs/proof/closed_beta/minimal_human_ui_redesign.md`.
- Tests to update: hero copy, primary CTA, blocked public copy, result section order, consent gate, metadata-only feedback, and responsive single-column CSS.
- Acceptance criteria: the page is understandable in one glance, the result card is evidence-first, the analyzer requires consent, safety copy is visible but compact, and no backend/mobile/runtime contracts change.
