# GDPR Privacy Notice Research

Status: draft_requires_legal_review

This is research grounding for Vibe Signal public legal drafts. It is not legal approval and does not claim the GDPR requirements are satisfied.

## Sources

- EUR-Lex, GDPR Article 13: https://eur-lex.europa.eu/eli/reg/2016/679/art_13/oj/eng
- EUR-Lex, GDPR Article 14: https://eur-lex.europa.eu/eli/reg/2016/679/art_14/oj/eng
- EUR-Lex, GDPR Article 15-22 data subject rights: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- ICO, information to supply under GDPR: https://ico.org.uk/for-organisations/advice-for-small-organisations/getting-started-with-gdpr/data-protection-self-assessment/what-information-you-must-supply-under-the-gdpr/
- EDPB transparency guidelines: https://www.edpb.europa.eu/our-work-tools/our-documents/article-29-working-party-guidelines-transparency-under-regulation_en
- Vercel runtime logs: https://vercel.com/docs/concepts/observability/runtime-logs
- Render logs: https://render.com/docs/logging

## Privacy Notice Elements To Cover

- Controller identity: [LEGAL_OPERATOR_NAME_REQUIRED].
- Contact details: [PRIVACY_CONTACT_EMAIL_REQUIRED] and [BUSINESS_ADDRESS_OR_CONTACT_METHOD_REQUIRED].
- Production URL: https://www.vibe-signal.com.
- Product purpose: communication-support for observable wording patterns including clarity, ambiguity, pressure, reassurance, directness, cognitive load, and repair opportunities.
- Categories of personal data: submitted text processed transiently, service metadata, metadata-only feedback, infrastructure logs, and domain/DNS metadata where relevant.
- Purposes: provide analysis, security/debugging/reliability, closed-beta feedback, abuse prevention, and legal/data request handling.
- Lawful basis: [LAWFUL_BASIS_REQUIRES_LEGAL_REVIEW].
- Recipients/processors: Vercel, Render, GitHub, GoDaddy, email provider, AI provider status placeholder, and no analytics provider.
- International transfers: processors may process/store data outside the user country or EEA depending on provider infrastructure; legal review must decide notice and safeguards language.
- Retention: raw submitted text transient only; feedback metadata, legal request correspondence, and provider logs need explicit periods or placeholders.
- Data subject rights: access/export, deletion, correction, objection/restriction, and withdrawal of consent where applicable.
- Complaint right: [SUPERVISORY_AUTHORITY_REQUIRES_LEGAL_REVIEW].
- Security summary: HTTPS, minimal data design, no raw chat persistence by design, restricted artifact checks, and public copy safety checks.
- Children/minors limitation: not intended for minors or teen romantic analysis.
- Automated decision-making statement: no automated legal, medical, financial, employment, education, housing, credit, or similarly significant decisions.

## Training, AI, And Safety Wording

- No raw messages are used for training.
- No analytics, cookies, or tracking are added by this implementation.
- No model-quality, health-label, or emotion-recognition claims should be made.
- Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.

## Draft Retention Assumptions

- Vercel Hobby/basic runtime logs: assume 1 hour unless dashboard/account changes.
- Render Hobby/basic backend logs: assume 7 days unless dashboard/workspace changes.
- External log streaming: none configured.
- Feedback metadata: [FEEDBACK_METADATA_RETENTION_REQUIRED].
- Legal/data request correspondence: [LEGAL_REQUEST_RETENTION_REQUIRED].

## Open Legal-Review Questions

- Confirm operator/controller identity, address/contact method, and privacy contact email.
- Confirm whether Vibe Signal is subject to GDPR/UK GDPR/other privacy laws based on users and operator location.
- Confirm lawful basis by processing purpose.
- Confirm processor DPAs and international transfer mechanism language.
- Confirm retention periods for feedback metadata and legal request correspondence.
- Confirm age/minors policy language.
