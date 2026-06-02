from __future__ import annotations

from typing import Any

from fastapi import APIRouter


router = APIRouter()


BASE_DRAFT_BOUNDARIES: dict[str, Any] = {
    "status": "draft_requires_legal_review",
    "not_legal_advice": True,
    "closed_beta_only": True,
    "production_compliance_claimed": False,
    "raw_message_persistence_added": False,
    "account_storage_added": False,
    "analytics_tracking_added": False,
    "training_use_added": False,
    "review_note": "Draft copy for closed-beta readiness; requires legal review before public launch.",
}

LEGAL_PAGES: dict[str, dict[str, Any]] = {
    "privacy": {
        "title": "Privacy Policy Draft",
        "document_ref": "docs/privacy_policy_draft.md",
        "sections": [
            "Vibe Signal is communication-support only and processes submitted text to return pattern-based suggestions, not truth claims.",
            "The local backend does not persist raw messages by default for analysis or matching routes.",
            "Feedback storage requires explicit consent and stores bounded metadata only by default.",
            "Do not submit sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.",
            "Closed beta is not production launch. Final privacy URLs, retention windows, deletion handling, and export handling require legal review before public launch.",
        ],
    },
    "terms": {
        "title": "Terms And Acceptable Use Draft",
        "document_ref": "docs/terms_draft.md",
        "sections": [
            "Use Vibe Signal only for communication-support and observable wording-pattern review.",
            "Outputs are pattern-based suggestions, not truth claims, professional advice, relationship predictions, or identity/health judgments.",
            "Do not use the app to pressure, harass, surveil, diagnose, profile, or make hidden-state claims about another person.",
            "Do not submit material you do not have permission to process.",
            "Closed beta is not production launch. Draft terms require legal review before public launch.",
        ],
    },
    "data-deletion": {
        "title": "Data Deletion Request Draft",
        "document_ref": "docs/data_deletion_request_draft.md",
        "sections": [
            "Local matching and analysis routes do not persist raw messages by default.",
            "Deletion handling applies to stored metadata such as consented feedback, event metadata, device-scoped identifiers, or support records when those systems are enabled.",
            "Requests should include a contact address, approximate submission date, and any non-sensitive identifiers needed to locate stored metadata.",
            "Do not include raw chat text, secrets, medical data, legal documents, financial data, or unrelated third-party private messages in a deletion request.",
            "Production deletion workflow, identity checks, retention windows, and response timelines require legal review before public launch.",
        ],
    },
    "data-export": {
        "title": "Data Export Request Draft",
        "document_ref": "docs/data_export_request_draft.md",
        "sections": [
            "Local matching and analysis routes do not persist raw messages by default, so there may be no raw message content to export.",
            "Export handling applies to stored metadata such as consented feedback, event metadata, device-scoped identifiers, or support records when those systems are enabled.",
            "Requests should include a contact address, approximate submission date, and any non-sensitive identifiers needed to locate stored metadata.",
            "Do not include raw chat text, secrets, medical data, legal documents, financial data, or unrelated third-party private messages in an export request.",
            "Production export workflow, identity checks, retention windows, and response timelines require legal review before public launch.",
        ],
    },
    "match-disclaimer": {
        "title": "Match Usage Consent Disclaimer",
        "document_ref": "docs/match_usage_consent_disclaimer.md",
        "sections": [
            "Vibe Signal matching is communication-support only.",
            "Outputs are pattern-based suggestions, not truth claims.",
            "Only submit messages you have permission to analyze.",
            "Do not include sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.",
            "Closed beta is not production launch. Privacy and terms drafts require legal review before public launch.",
        ],
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
