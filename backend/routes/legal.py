from __future__ import annotations

from typing import Any

from fastapi import APIRouter


router = APIRouter()


LEGAL_STATUS = "draft_requires_legal_review"
LEGAL_STATUS_LINE = "Status: draft_requires_legal_review"
LEGAL_INTRO = (
    "Vibe Signal is currently in closed beta / early public beta. "
    "These legal drafts are provided for transparency and require legal review before public launch."
)

BASE_DRAFT_BOUNDARIES: dict[str, Any] = {
    "status": LEGAL_STATUS,
    "not_legal_advice": True,
    "closed_beta_only": True,
    "production_compliance_claimed": False,
    "raw_message_persistence_added": False,
    "account_storage_added": False,
    "analytics_tracking_added": False,
    "training_use_added": False,
    "review_note": "Draft copy for closed-beta readiness; requires legal review before public launch.",
}


def _groups_to_sections(groups: list[dict[str, Any]]) -> list[str]:
    sections = [LEGAL_STATUS_LINE, LEGAL_INTRO]
    for group in groups:
        sections.append(str(group["heading"]))
        sections.extend(str(item) for item in group.get("items", []))
    return sections


PRIVACY_GROUPS: list[dict[str, Any]] = [
    {
        "heading": "Operator and contact placeholders",
        "items": [
            "Operator/controller placeholder: [LEGAL_OPERATOR_NAME_REQUIRED].",
            "Privacy contact placeholder: [PRIVACY_CONTACT_EMAIL_REQUIRED].",
            "Business address or contact method placeholder: [BUSINESS_ADDRESS_OR_CONTACT_METHOD_REQUIRED].",
            "Production URL: https://www.vibe-signal.com.",
            "Controller role and lawful basis require legal review: [LAWFUL_BASIS_REQUIRES_LEGAL_REVIEW].",
        ],
    },
    {
        "heading": "Product purpose",
        "items": [
            "Vibe Signal is a communication-support tool for reviewing observable wording patterns such as clarity, ambiguity, pressure, reassurance, directness, cognitive load, and repair opportunities.",
            "Outputs are suggestions and limits based on the text shown, not truth claims or relationship-outcome predictions.",
        ],
    },
    {
        "heading": "Categories of data",
        "items": [
            "Submitted text is processed transiently to provide analysis.",
            "Metadata required to operate the service may include request status, timing, error state, and reliability signals.",
            "Feedback stores result metadata only, never message text.",
            "Infrastructure logs may be created by Vercel and Render.",
            "Domain and DNS provider metadata may exist with GoDaddy where relevant to domain operation.",
        ],
    },
    {
        "heading": "What is not intentionally stored",
        "items": [
            "No raw chat history is intentionally stored.",
            "No raw submitted message persistence is added.",
            "No raw messages are used for training.",
            "No analytics, cookies, or tracking are added by this implementation.",
        ],
    },
    {
        "heading": "Processing purposes",
        "items": [
            "Provide wording-based analysis and safer reply suggestions.",
            "Support security, debugging, reliability, abuse prevention, and closed-beta feedback.",
            "Handle legal, privacy, data request, or deletion request correspondence where applicable.",
        ],
    },
    {
        "heading": "Processors and subprocessors draft table",
        "items": [
            "Vercel - frontend hosting, CDN, deployment, and runtime logs. Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes.",
            "Render - backend/API hosting and logs. Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes.",
            "GitHub - source code, CI, and project workflow. No raw user chats are committed.",
            "GoDaddy - domain registration and DNS metadata.",
            "Email provider - [EMAIL_PROVIDER_REQUIRED].",
            "AI provider - [AI_PROVIDER_STATUS_REQUIRED]. Optional external provider connectors are disabled by default unless production configuration changes.",
            "Analytics - none configured.",
        ],
    },
    {
        "heading": "Retention draft",
        "items": [
            "Raw submitted text: transient processing only and not intentionally retained.",
            "Feedback metadata: [FEEDBACK_METADATA_RETENTION_REQUIRED].",
            "Vercel runtime logs: Hobby/basic, assume 1 hour unless account changes.",
            "Render logs: Hobby/basic, assume 7 days unless account changes.",
            "Legal/data request correspondence: [LEGAL_REQUEST_RETENTION_REQUIRED].",
        ],
    },
    {
        "heading": "Transfers, safeguards, and rights",
        "items": [
            "Processors may process or store data outside the user country or EEA depending on provider infrastructure; this requires legal review.",
            "Safeguards summary: HTTPS, minimal data design, no raw chat persistence by design, restricted artifacts checks, and public copy safety checks.",
            "Data subject rights may include access/export, deletion, correction, objection/restriction, and withdrawal of consent where applicable.",
            "Complaint or supervisory authority placeholder: [SUPERVISORY_AUTHORITY_REQUIRES_LEGAL_REVIEW].",
            "Vibe Signal is not intended for minors or teen romantic analysis.",
        ],
    },
    {
        "heading": "Automated decision-making and model limits",
        "items": [
            "Vibe Signal does not make automated legal, medical, financial, employment, education, housing, credit, or similarly significant decisions.",
            "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
            "No model-quality, health-label, or emotion-recognition claims are made.",
        ],
    },
]

TERMS_GROUPS: list[dict[str, Any]] = [
    {
        "heading": "Beta status",
        "items": [
            "Vibe Signal is offered as a closed beta / early public beta draft service.",
            "The service may change, pause, or be removed while legal, privacy, and product review continue.",
        ],
    },
    {
        "heading": "Permission and permitted use",
        "items": [
            "Only submit text you have permission to analyze.",
            "Permitted use includes communication clarity, reflection, and drafting safer replies.",
            "Use outputs as one input to your own judgment and context.",
        ],
    },
    {
        "heading": "Prohibited use",
        "items": [
            "Prohibited use includes stalking, harassment, coercion, manipulation, or trying to make someone respond.",
            "Do not use Vibe Signal to make hidden-intent, attraction, truthfulness, deception, cheating, or relationship-outcome certainty claims.",
            "Do not use Vibe Signal for workplace/education emotional assessment, minors/teen romantic analysis, or content you lack rights or permission to use.",
        ],
    },
    {
        "heading": "No professional advice",
        "items": [
            "Vibe Signal is not professional advice.",
            "Vibe Signal is not therapy, medical advice, legal advice, financial advice, or emergency support.",
            "For urgent risk or safety situations, contact appropriate emergency or local support services.",
        ],
    },
    {
        "heading": "Accounts, payment, availability, and access",
        "items": [
            "Account features: [ACCOUNT_FEATURES_NOT_CURRENTLY_IMPLEMENTED].",
            "Payment features: [PAYMENT_FEATURES_NOT_CURRENTLY_IMPLEMENTED].",
            "Service availability and warranty language require legal review before launch.",
            "Limitation of liability placeholder: [LIMITATION_OF_LIABILITY_REQUIRES_LEGAL_REVIEW].",
            "Governing law placeholder: [GOVERNING_LAW_REQUIRES_LEGAL_REVIEW].",
            "Access removal or termination process requires legal review before launch.",
        ],
    },
]

DATA_REQUEST_GROUPS: list[dict[str, Any]] = [
    {
        "heading": "Contact and request types",
        "items": [
            "Send data requests to: [PRIVACY_CONTACT_EMAIL_REQUIRED].",
            "Request types may include access/export, deletion, correction, objection/restriction, and withdrawal of consent where applicable.",
            "Response timeline placeholder: [RESPONSE_TIMELINE_REQUIRES_LEGAL_REVIEW].",
        ],
    },
    {
        "heading": "What to include",
        "items": [
            "Include the email or contact method used with Vibe Signal.",
            "Include the request type and enough information to verify the request.",
            "Do not include unnecessary private message content in the request.",
            "Identity verification may be required before action is taken.",
        ],
    },
    {
        "heading": "Raw message and metadata limits",
        "items": [
            "Raw submitted text may not be available for export or deletion because the app is designed not to intentionally retain it.",
            "Feedback is metadata-only and does not include message text.",
            "Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes.",
            "Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes.",
            "Provider infrastructure logs may expire before a request is processed.",
        ],
    },
    {
        "heading": "Closed-beta manual runbook",
        "items": [
            "1. Receive request.",
            "2. Verify requester.",
            "3. Search app metadata stores if any.",
            "4. Check feedback metadata if applicable.",
            "5. Delete, export, or correct data where technically available.",
            "6. Respond with what was found or deleted, or explain when no retained raw text exists.",
        ],
    },
]

DISCLAIMER_GROUPS: list[dict[str, Any]] = [
    {
        "heading": "Communication support only",
        "items": [
            "Vibe Signal is communication-support only.",
            "Vibe Signal provides wording-based suggestions only.",
            "Outputs should be read as observable text evidence and possible patterns.",
            "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
        ],
    },
    {
        "heading": "Not professional or crisis support",
        "items": [
            "Vibe Signal is not therapy.",
            "Vibe Signal is not medical advice, legal advice, or financial advice.",
            "Vibe Signal is not emergency/crisis support.",
            "If there is urgent risk or a safety situation, contact appropriate emergency or local support services.",
        ],
    },
    {
        "heading": "Use human judgment",
        "items": [
            "Vibe Signal is not a substitute for human judgment, context, consent, or respectful communication.",
            "Low-signal outputs may be incomplete.",
            "Use safe, respectful, non-coercive communication and ask one clear follow-up when appropriate.",
        ],
    },
]

DATA_EXPORT_GROUPS: list[dict[str, Any]] = [
    {
        "heading": "Export request compatibility route",
        "items": [
            "This route remains available for compatibility with earlier clients.",
            "Use the Data request/delete page for access/export, deletion, correction, objection/restriction, and withdrawal of consent where applicable.",
            "Raw submitted text may not be available for export or deletion because the app is designed not to intentionally retain it.",
        ],
    },
    *DATA_REQUEST_GROUPS,
]

LEGAL_PAGES: dict[str, dict[str, Any]] = {
    "privacy": {
        "title": "Privacy",
        "document_ref": "docs/legal/research/gdpr_privacy_notice_research.md",
        "intro": LEGAL_INTRO,
        "groups": PRIVACY_GROUPS,
        "sections": _groups_to_sections(PRIVACY_GROUPS),
    },
    "terms": {
        "title": "Terms",
        "document_ref": "docs/legal/research/terms_research.md",
        "intro": LEGAL_INTRO,
        "groups": TERMS_GROUPS,
        "sections": _groups_to_sections(TERMS_GROUPS),
    },
    "data-deletion": {
        "title": "Data request/delete",
        "document_ref": "docs/legal/research/data_request_delete_research.md",
        "intro": LEGAL_INTRO,
        "groups": DATA_REQUEST_GROUPS,
        "sections": _groups_to_sections(DATA_REQUEST_GROUPS),
    },
    "data-export": {
        "title": "Data export request",
        "document_ref": "docs/legal/research/data_request_delete_research.md",
        "intro": LEGAL_INTRO,
        "groups": DATA_EXPORT_GROUPS,
        "sections": _groups_to_sections(DATA_EXPORT_GROUPS),
    },
    "match-disclaimer": {
        "title": "Disclaimer",
        "document_ref": "docs/legal/research/disclaimer_ai_safety_research.md",
        "intro": LEGAL_INTRO,
        "groups": DISCLAIMER_GROUPS,
        "sections": _groups_to_sections(DISCLAIMER_GROUPS),
    },
}


def _legal_page(slug: str) -> dict[str, Any]:
    return {
        **BASE_DRAFT_BOUNDARIES,
        "slug": slug,
        **LEGAL_PAGES[slug],
    }


@router.get("/legal/privacy")
def privacy_policy_draft() -> dict[str, Any]:
    return _legal_page("privacy")


@router.get("/legal/terms")
def terms_draft() -> dict[str, Any]:
    return _legal_page("terms")


@router.get("/legal/data-deletion")
def data_deletion_request_draft() -> dict[str, Any]:
    return _legal_page("data-deletion")


@router.get("/legal/data-export")
def data_export_request_draft() -> dict[str, Any]:
    return _legal_page("data-export")


@router.get("/legal/match-disclaimer")
def match_usage_consent_disclaimer() -> dict[str, Any]:
    return _legal_page("match-disclaimer")
