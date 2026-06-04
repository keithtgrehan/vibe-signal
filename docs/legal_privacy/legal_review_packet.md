# Legal / Privacy Review Packet

Status: draft for human legal/privacy review. Legal review is pending.

This packet summarizes implementation facts for review. It does not claim GDPR compliance, legal compliance, EU AI Act compliance, App Store approval, or production readiness.

## Product Boundary

Vibe Signal highlights observable message patterns such as clarity, ambiguity, pressure, reassurance, cognitive load, unanswered asks, boundary pressure, escalation risk, and repair opportunities.

It must not be positioned as hidden-intent detection, cheating detection, attraction prediction, lie detection, diagnosis, therapy, attachment-style inference, neurotype inference, manipulation guidance, or relationship outcome prediction.

## Data Flow Summary

- User submits synthetic demo text or permissioned pasted text to analysis/match routes.
- Backend produces structured cue/evidence output.
- Feedback route requires explicit consent and stores bounded metadata only.
- Event routes store bounded metadata only.
- No raw private chats are intentionally committed to fixtures, docs, reports, tests, or training.
- Dataset/training sources are rights-gated and commercial fail-closed.

## Review Materials

- [data_flow_summary.md](data_flow_summary.md)
- [privacy_review_checklist.md](privacy_review_checklist.md)
- [processor_inventory_draft.md](processor_inventory_draft.md)
- [user_rights_request_draft.md](user_rights_request_draft.md)
- [delete_export_request_process.md](delete_export_request_process.md)
- [../privacy_data_flow.md](../privacy_data_flow.md)
- [../legal_safe_output_policy.md](../legal_safe_output_policy.md)

## Open Legal Questions

- final privacy policy wording
- terms and disclaimers for closed beta
- support/delete/export request handling commitments
- App Store privacy label entries
- whether any optional provider/BYOK behavior is in beta scope
- retention period for feedback/event metadata
- incident process if raw-content leakage is suspected

