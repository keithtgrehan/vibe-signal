# Data Request / Delete Research

Status: draft_requires_legal_review

This is research grounding for Vibe Signal data request/delete handling. It is not legal approval and does not claim any final legal response timeline.

## Sources

- EUR-Lex GDPR Article 12 request handling and identity verification context: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- EUR-Lex GDPR Articles 15-22 data subject rights: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- ICO individual rights guidance: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/
- Vercel runtime logs: https://vercel.com/docs/concepts/observability/runtime-logs
- Render logs: https://render.com/docs/logging

## Request Types

- Access/export.
- Deletion.
- Correction.
- Objection/restriction.
- Withdrawal of consent where applicable.

## Contact Placeholder

- Privacy contact email: keith.t.grehan@gmail.com.

## What Requesters Should Include

- Email used or contact method used with Vibe Signal.
- Request type.
- Enough information to verify the request.
- Avoid unnecessary private message content.

## Identity Verification

- A closed-beta manual process should verify the requester before exporting, deleting, or correcting data.
- If identity cannot be verified, legal review should define what response can be sent and what additional information can be requested.

## Raw Message And Metadata Limits

- Raw submitted text may not be available for export/delete because the app is designed not to intentionally retain it.
- Feedback is metadata-only and should not include message text.
- Provider infrastructure logs may expire before a request is processed.
- Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes.
- Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes.

## Response Process Placeholder

- Vibe Signal aims to respond to verified privacy requests without undue delay and, where GDPR applies, within one month of receipt. This timeline may depend on identity verification, request scope, and applicable legal requirements. This section requires legal review before public launch.
- Feedback metadata retention: 90 days during beta.
- Legal request correspondence retention: 24 months unless legal review changes this.

## Closed-Beta Manual Runbook

1. Receive request.
2. Verify requester.
3. Search app metadata stores if any.
4. Check feedback metadata if applicable.
5. Delete, export, or correct where technically available.
6. Respond with what was found/deleted or explain that no retained raw text exists.

## Unresolved Legal-Review Questions

- Confirm request-response timeline by jurisdiction.
- Confirm identity verification method and evidence retention.
- Confirm whether any metadata store exists beyond feedback and infrastructure logs.
- Confirm when requests should be refused, extended, or escalated.
- Confirm exact export format and deletion confirmation wording.
