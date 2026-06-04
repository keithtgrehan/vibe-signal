# Replit Friend A/B Test Plan

## Purpose

Use Replit hosting only as a parallel feedback environment for friends. Production remains Vercel + Render.

## Setup

- Import the repo into Replit from: `https://github.com/keithtgrehan/vibe-signal`
- Use a separate branch for experiments: `replit/ab-minimal-frontend-redesign`
- Frontend only.
- Backend API should point to: `https://vibe-signal.onrender.com`
- Do not rebuild backend.
- Do not collect real private chats from friends.
- Ask friends to use the synthetic demo or permissioned text only.
- Do not add analytics or tracking SDKs.
- Collect feedback manually or via bounded metadata-only notes.

## Suggested Friend Feedback Questions

1. What do you think this product does after 5 seconds?
2. Which button would you click first?
3. Does the result feel useful?
4. Does anything feel creepy, too strong, or unclear?
5. Would you trust this with a message if you had permission to analyze it?
6. Which wording is better:
   - "See what a message is doing"
   - "Before you reply, check what the message actually says"
7. What would stop you from using it?

## A/B Approach

- Production/Codex variant: `https://vibe-signal.vercel.app`
- Replit experimental variant: Replit-hosted URL
- Keep backend same for both.
- Compare user comprehension, CTA click intent, perceived trust, and result usefulness.
- Do not compare using private user messages.

## Feedback Table Template

| tester_name_or_alias | variant_seen | 5_second_understanding | first_click | useful_result_yes_no | trust_score_1_to_5 | confusing_copy | creepy_or_too_strong_copy | suggested_change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Production/Codex or Replit |  |  |  |  |  |  |  |

## Guardrails

- Replit is not production.
- Do not change production backend behavior.
- Do not add auth, tracking, analytics, raw message persistence, or raw message logging.
- Do not wire n8n into production.
- Do not make legal compliance claims.
- Do not introduce claims about hidden intent, attraction, deception, cheating, diagnosis, neurotype, attachment style, manipulation, secret feelings, or relationship truth.
