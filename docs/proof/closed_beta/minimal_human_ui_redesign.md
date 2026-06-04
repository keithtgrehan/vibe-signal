# Minimal Human UI Redesign Proof

## What changed

- Replaced the dense web landing layout with a minimal consumer product flow.
- Added the research-agent phase under `docs/research/ui_minimal_redesign/` before implementation.
- Made the hero promise direct: "See what a message is doing - without guessing what someone feels."
- Centered the page on one synthetic demo and one evidence-first result card.
- Simplified pasted-text analysis to a textarea, consent checkbox, helper copy, and one Analyze button.
- Reduced "How it works" to three short steps and replaced repeated safety panels with one trust footer.

## Why the UI was simplified

The old page exposed goals, context, style, comparison, multiple demo cards, trust chips, and boundary panels before the user saw a result. The new page shows value first: run a demo, see what stands out, read the evidence, and decide whether to try allowed text.

## Before / after positioning

Before: "A trust-first analysis dashboard for observable message patterns."

After: "A calm message-reading aid that helps users stop guessing and look at observable wording before replying."

## Safety boundaries preserved

- No backend engine behavior changed.
- No backend API contract changed.
- No mobile code changed.
- No analytics SDKs, tracking, user accounts, raw-message persistence, raw-message logging, or n8n production calls were added.
- Results stay evidence-first: what stands out, evidence, what it could mean, safer reply, limits.
- Pasted-text analysis still requires explicit permission.
- Feedback sends result metadata only and no message text.
- Consumer UI avoids hidden-intent, attraction, deception, cheating, manipulation, diagnosis, therapy, legal, medical, or outcome claims.

## Validation commands

Run from the repo root unless noted:

```bash
python -m pytest -q
cd web && npm test && npm run build
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
git diff --check
git grep -ni "they like you\|hidden intent\|they are lying\|cheating detector\|diagnose\|attachment style\|neurotype\|make them respond\|win them back" -- web docs README.md || true
```

## Blocked phrase grep note

Blocked phrase matches are expected only in tests and in existing safety, legal, labeling, readiness, research, or proof documentation where those phrases are listed as forbidden examples or explicit product boundaries. They must not appear in consumer-facing `web/src` copy.

## Screenshots checklist

- Desktop hero: headline, two CTAs, and trust line fit in the first viewport.
- Desktop demo/result: one demo card appears left and the result card is readable on the right.
- Desktop after demo: result order is what stands out, evidence, what it could mean, safer reply, limits.
- Mobile hero: single-column layout, CTA visible, no horizontal overflow.
- Mobile result: result card is bounded, readable, and no text overlaps.
- Analyze section: consent checkbox and Analyze button are visible and at least 44px tall.

## PR description checklist

- Summarize the research-agent phase and final thesis.
- Include desktop and mobile screenshots for hero, demo/result before running, and demo/result after running.
- List validation commands and outcomes.
- State that backend, mobile, analytics, tracking, raw storage, and n8n production calls were not changed.
