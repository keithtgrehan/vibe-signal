# Vibe Signal UI A/B Variant Registry

## Production baseline - Codex minimal UI

Status: Production baseline  
Source: Codex  
Branch: main  
Merged PR: #39  
Commit: f814a8216f2d5e7435a2161a9f2fec8ba0cf274b  
Tag: ui-baseline-codex-minimal-2026-06-04  
URL: https://vibe-signal.vercel.app  
Backend: https://vibe-signal.onrender.com  
Purpose: Stable baseline for friends/user feedback.

Notes:
- Backend unchanged.
- Frontend deployed through Vercel.
- Evidence-first result order:
  1. What stands out
  2. Evidence
  3. What it could mean
  4. Safer reply
  5. Limits

## Experimental variant - Replit A/B frontend

Status: Experimental / do not merge yet  
Source: Replit  
Target branch: replit/ab-minimal-frontend-redesign  
Branch note: Branch pending export from Replit working tree.  
URL: https://vibe-signal-ab.replit.app  
Backend: https://vibe-signal.onrender.com  
Purpose: Friend A/B testing only.

Rules:
- Do not merge to main until A/B test feedback is complete.
- Do not use as production.
- Do not collect real private chats from friends.
- Use synthetic demo or permissioned text only.
- Keep backend unchanged.
- Keep API contracts unchanged.
- No analytics/tracking SDKs.

## Decision rule

Replit variant may only be merged or cherry-picked after:
- Friend feedback is reviewed.
- Safety copy scan passes.
- Web tests pass.
- Build passes.
- No consumer-facing unsafe claims exist.
- A final decision doc is written.
