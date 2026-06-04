# Replit A/B Frontend Redesign Proof

Branch: `replit/ab-minimal-frontend-redesign`

## Source

- Zip source: `/Users/keith/Desktop/Vibe Signal Replit/replit_ab_minimal_frontend_redesign.zip`
- Extracted patch: `/tmp/replit_ab_patch/replit_ab_minimal_frontend_redesign.patch`

## Why Direct Apply Failed

The patch conflicted with the already-merged Codex minimal UI on current main:

- `web/src/App.jsx`
- `web/src/styles.css`
- `web/tests/uiTrustDemo.test.mjs`

The patch was therefore used as reference material only. No forced patch apply, reject file merge, or blind hunk acceptance was used.

## What Was Manually Ported

- Added a frontend-only variant model in `web/src/variants.js`.
- Variant selection is controlled by `?variant=a` or `?variant=b`.
- Invalid variants fall back to Variant A.
- Optional local storage only remembers the visual variant for this browser.
- Result sections stay in the evidence-first order.
- Public copy scanning now includes `web/src/variants.js`.

## Variant A

Variant A is the production Codex minimal UI:

- Headline: "See what a message is doing - without guessing what someone feels."
- Primary action: "Run a demo"
- Result order: What stands out, Evidence, What it could mean, Safer reply, Limits.

## Variant B

Variant B is the Replit-inspired "Before You Reply" experiment:

- Headline: "Before you reply, check what the message actually says."
- Primary action: "Check a demo"
- Result labels: The part to slow down on, The exact words, A grounded read, A calmer reply, Limits.
- The synthetic unclear-timing demo uses calmer wording while staying grounded in the visible words.

## Validation

Completed on branch `replit/ab-minimal-frontend-redesign`:

- `cd web && npm test` - PASS, 34 tests.
- `cd web && npm run build` - PASS.
- `python scripts/check_public_copy_safety.py` - PASS, 23 allowlisted findings and 0 unallowlisted findings.
- `python scripts/check_no_raw_content_leaks.py` - PASS, 0 findings.
- `git diff --check` - PASS.
- Required blocked-copy `git grep` - PASS, no output.

An additional regex scan found existing blocked-term examples only in README/tests used for safety boundaries. No match appeared in `web/src` consumer UI copy.

## Safety Boundaries

- No backend logic changes.
- No API contract changes.
- No analytics, tracking pixels, auth, or user identity logic.
- No raw message persistence or raw message logging.
- No n8n production wiring.
- No production Vercel setup changes.
- No consumer UI claims about concealed motives, attraction, truth certainty, diagnostic labels, or persuasion tactics.

## Known Risks

- Variant B is a friend-feedback experiment, not a production replacement.
- The Replit hosting path may need separate environment setup outside this repository.
- Friend testing should use synthetic examples or permissioned text only.

## Merge Boundary

Draft only. Do not merge this branch until friend A/B feedback is reviewed and the decision template is completed.
