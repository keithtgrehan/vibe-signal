# Synthetic-Only Screenshot Checklist

Use synthetic examples only. Do not capture private or third-party chat content.

- Landing page first viewport with required hero copy and primary synthetic CTA.
- Trust strip plus visible can/cannot section.
- Six synthetic demo cards: unclear ask, pressure / urgency, repair opportunity, low-signal fallback, boundary-respecting request, overloaded message.
- Reviewer demo path and result hierarchy rail.
- Consent gate showing "Before you paste" and permission checkbox.
- Evidence-first result showing main read, signal strength, quoted evidence, pattern explanation, cannot-infer block, safe next step, and metadata-only feedback buttons.
- Low-signal fallback for short/context-light text such as "hey" or "ok".
- No-safe-evidence fallback if a backend response lacks safe quoted evidence.
- Mobile result screen if available, using the same synthetic examples and no private text.
- Feedback buttons before and after consent, showing metadata-only selected state.
- Privacy/legal fallback screen, without private content.

Suggested flow names:

- `web-landing-synthetic-first`
- `web-synthetic-demo-cards`
- `web-reviewer-demo-flow`
- `web-consent-gate`
- `web-evidence-first-result`
- `web-low-signal-fallback`
- `web-no-safe-evidence-fallback`
- `web-metadata-feedback`
- `mobile-evidence-first-result`
- `mobile-consent-and-low-signal`
