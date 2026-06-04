# Replit Patch Assessment

Branch: `replit/ab-minimal-frontend-redesign`

## Patch Source

- Zip source: `/Users/keith/Desktop/Vibe Signal Replit/replit_ab_minimal_frontend_redesign.zip`
- Extracted patch: `/tmp/replit_ab_patch/replit_ab_minimal_frontend_redesign.patch`

The raw zip was not copied into the repository. The patch was used as reference material only.

## Direct Apply Result

Direct apply failed because the patch was generated against an older frontend shape than the current main branch, which already contains the approved Codex minimal UI from PR #39.

Conflicting files:

- `web/src/App.jsx`
- `web/src/styles.css`
- `web/tests/uiTrustDemo.test.mjs`

## Files Touched By Patch

- `docs/proof/closed_beta/replit_ab_frontend_redesign.md`
- `docs/research/replit_ab_frontend_redesign/final_thesis.md`
- `docs/research/replit_ab_frontend_redesign/research_agents.md`
- `scripts/check_public_copy_safety.py`
- `web/src/App.jsx`
- `web/src/styles.css`
- `web/src/variants.js`
- `web/tests/uiTrustDemo.test.mjs`
- `web/tests/uxCopySafety.test.mjs`
- `web/tests/variant.test.mjs`
- `web/vite.config.js`

Backend files were not part of the patch. The patch did include `web/vite.config.js`, but this manual port does not change Vite config because query-selected variants work in the existing build.

## Consumer UI Safety Read

The web-facing additions in the patch were reviewed as reference material. The manual port keeps the useful "Before You Reply" direction while preserving the product boundary: Vibe Signal describes observable wording, not private motives, relationship verdicts, diagnosis, or persuasion tactics.

## Decision

Do not force-apply the patch. Manually port the useful frontend ideas onto current main:

- Variant A remains the current Codex production UI.
- Variant B adds the Replit-inspired "Before You Reply" copy direction.
- Variant selection uses `?variant=a` or `?variant=b`, defaulting to Variant A.
- No backend behavior, API contract, production Vercel setup, tracking, auth, raw-content storage, or n8n production wiring changes are made.

Production remains `main` on Vercel at `https://vibe-signal.vercel.app`.
