# DPA / Processor / Subprocessor Research

Status: draft_requires_legal_review

This is research grounding for Vibe Signal vendor and DPA readiness. It is not legal approval and does not claim the GDPR requirements are satisfied.

## Sources

- GDPR Article 28 processor obligations: https://eur-lex.europa.eu/eli/reg/2016/679/art_28/oj/eng
- Vercel Data Processing Addendum: https://vercel.com/legal/dpa
- Vercel subprocessors and security portal reference: https://security.vercel.com
- Vercel runtime logs: https://vercel.com/docs/concepts/observability/runtime-logs
- Render Data Processing Addendum: https://render.com/dpa
- Render trust/subprocessor reference: https://render.com/trust
- Render logs: https://render.com/docs/logging
- GitHub privacy statement: https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement
- GitHub subprocessors: https://docs.github.com/en/site-policy/privacy-policies/github-subprocessors
- GoDaddy Data Processing Addendum: https://www.godaddy.com/legal/agreements/data-processing-addendum
- OpenAI DPA and subprocessors, only relevant if production provider path is enabled: https://openai.com/policies/feb-2024-data-processing-addendum/ and https://openai.com/policies/sub-processor-list/

## Controller / Processor Summary

- Controller: the party deciding why and how Vibe Signal processes user data. Placeholder: [LEGAL_OPERATOR_NAME_REQUIRED].
- Processor: a vendor processing personal data for the controller under instructions, such as hosting or infrastructure services.
- GDPR Article 28 generally requires controller-processor terms covering subject matter, duration, nature and purpose, data categories, controller obligations, processor obligations, security, subprocessing, assistance, return/deletion, and audits.
- This draft should not claim that DPAs are signed or complete until Keith/legal confirms vendor account terms and plan-specific availability.

## Proposed Subprocessor Table

| Vendor | Draft role | Purpose | Current assumption |
| --- | --- | --- | --- |
| Vercel | Processor / independent controller for its own service metadata depending on context | Frontend hosting, CDN, deployment, runtime logs | Hobby/basic runtime logs assumed 1 hour unless account changes |
| Render | Processor / independent controller for its own service metadata depending on context | Backend/API hosting and logs | Hobby/basic logs assumed 7 days unless workspace changes |
| GitHub | Developer platform vendor | Source code, CI, PR workflow | No raw user chats should be committed |
| GoDaddy | Registrar/DNS vendor | Domain registration and DNS metadata | Domain registrar/DNS metadata only |
| Email provider | Placeholder | Privacy contact and request correspondence | [EMAIL_PROVIDER_REQUIRED] |
| OpenAI / Anthropic / Groq | Disabled unless production provider path is enabled | Optional external AI provider path | [AI_PROVIDER_STATUS_REQUIRED]; repo provider flags default off |
| Analytics/crash providers | None | Not configured | Do not add analytics, cookies, or tracking |

## Log Retention Notes

- Vercel documentation states Hobby runtime logs are retained for 1 hour.
- Render documentation states Hobby logs are retained for 7 days.
- No external log streaming is configured per Keith's setup notes.
- If account plans, log drains, observability vendors, or backend plan change, the public privacy page must be updated.

## Repo Implementation Findings

- Existing provider flags default to disabled: `VIBESIGNAL_ENABLE_EXTERNAL_PROVIDERS`, `VIBESIGNAL_ENABLE_OPENAI_PROVIDER`, `VIBESIGNAL_ENABLE_ANTHROPIC_PROVIDER`, and `VIBESIGNAL_ENABLE_GROQ_PROVIDER` default false.
- Existing backend legal routes expose draft boundary flags for no raw persistence, no account storage, no analytics tracking, and no training use.
- Existing copy and restricted-artifact scanners should remain part of release readiness.

## Unresolved Legal-Review Questions

- Which vendor DPAs have been accepted for Keith's actual accounts?
- Does Vercel DPA availability differ for Hobby/basic versus Pro/Enterprise on the active account?
- Is Render's DPA accepted automatically through account terms, or does Keith need a signed addendum?
- Which email provider will receive privacy requests?
- Is any external AI provider enabled in production, and if so under what terms, region, retention, and training settings?
- What subprocessor update notification process should be documented?
