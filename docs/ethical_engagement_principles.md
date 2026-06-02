# Ethical Engagement Principles

This document translates habit-loop mechanics into ethical, user-controlled value loops for Vibe Signal. It is a product policy, not legal advice. Legal/privacy/consumer-protection review remains required before public launch.

References:

- Nir Eyal, *Hooked* model: trigger, action, variable reward, investment.
- FTC, [Bringing Dark Patterns to Light](https://www.ftc.gov/reports/bringing-dark-patterns-light).
- EU Digital Services Act, [Regulation (EU) 2022/2065](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R2065), including online interface design obligations.
- EDPB, [Guidelines 03/2022 on deceptive design patterns](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en).

## Allowed Value Loop

| Hook mechanic | Vibe Signal implementation |
| --- | --- |
| Trigger | User-initiated onboarding, visible example prompts, and opt-in reminders only. |
| Action | One clear synthetic first success path: paste or use a synthetic example, confirm permission, submit. |
| Reward | Predictable explanation: score/band, factors, evidence safe phrases, limits, and next-step suggestions. No suspense, shame, or hidden emotional scoring. |
| Investment | User-controlled saved/recent examples, feedback metadata only after consent, export/delete links, and clear stop/pause controls. |

## Required UX Boundaries

- Clear first-run onboarding.
- Example-driven first success using synthetic examples.
- User agency and clear exits.
- Transparent limits before submit.
- Opt-in reminders only.
- Delete/export affordances visible through legal/support surfaces.
- Safe progress indicators that describe processing, not mind-reading.
- Helpful next-step suggestions that reduce pressure.
- Explainable value loops.
- Pause/stop controls for reminders or beta participation.

## Blocked UX

- Streak pressure.
- Shame copy.
- FOMO copy.
- Infinite-scroll engagement traps.
- Dark-pattern consent.
- Hidden emotional scoring.
- Coercive notifications.
- “They secretly feel...” claims.
- “Keep checking until they reply” loops.
- Interface choices that obscure, subvert, or impair user choice.
- Hard-to-cancel paid flows or buried subscription terms.

## Product Copy Red Lines

Do not claim or imply:

- hidden intent.
- attraction prediction.
- cheating detection.
- diagnosis, neurotype, or attachment style.
- emotional truth.
- manipulation scoring.
- relationship-success prediction.
- production model quality from synthetic-only metrics.
- legal/GDPR compliance without review.

## Current Implementation Notes

- Web and mobile show communication-support disclaimers before analysis.
- Web and mobile use synthetic sample text by default.
- Feedback is consent-gated, metadata-only, and deduped by bounded client event IDs.
- Loading copy uses observable-pattern wording, not suspense or mind-reading.
- Local-analysis copy avoids “intent” and “meaning” as output claims.
- Share cards include a pattern-based support boundary.
- No analytics/tracking SDK is added.
- No raw-message persistence is added.

## Test Coverage

- Mobile local-analysis tests block hidden-state and dark-pattern phrases.
- Mobile backend-client tests assert raw backend error bodies are not returned.
- Backend tests assert feedback/event dedupe and metadata-only storage.
- Dataset rights tests keep synthetic fixtures as the only training-ready source.
