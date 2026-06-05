from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app


def test_legal_routes_return_draft_review_boundaries() -> None:
    client = TestClient(app)

    for path in (
        "/legal/privacy",
        "/legal/terms",
        "/legal/data-deletion",
        "/legal/data-export",
        "/legal/match-disclaimer",
    ):
        response = client.get(path)

        assert response.status_code == 200, path
        body = response.json()
        assert body["status"] == "draft_requires_legal_review"
        assert body["not_legal_advice"] is True
        assert body["closed_beta_only"] is True
        assert body["production_compliance_claimed"] is False
        assert body["raw_message_persistence_added"] is False
        assert body["account_storage_added"] is False
        assert body["analytics_tracking_added"] is False
        assert body["training_use_added"] is False
        assert body["title"]
        assert body["document_ref"].startswith("docs/")
        assert body["sections"]
        assert body["intro"].startswith("Vibe Signal is currently in closed beta / early public beta.")
        assert body["groups"]
        assert "legal review before public launch" in body["review_note"].lower()


def test_match_disclaimer_route_keeps_required_safety_copy() -> None:
    client = TestClient(app)

    response = client.get("/legal/match-disclaimer")

    assert response.status_code == 200
    body = response.json()
    combined_copy = " ".join(body["sections"]).lower()
    assert "communication-support only" in combined_copy
    assert "wording-based suggestions only" in combined_copy
    assert "closed beta / early public beta" in combined_copy
    assert "vibe signal does not know intent, attraction, truthfulness, diagnosis, or outcomes." in combined_copy
    assert "not therapy" in combined_copy
    assert "not emergency/crisis support" in combined_copy


def test_legal_routes_include_required_public_draft_content() -> None:
    client = TestClient(app)

    privacy = client.get("/legal/privacy").json()
    privacy_copy = " ".join(privacy["sections"])
    assert "Status: draft_requires_legal_review" in privacy_copy
    assert "[LEGAL_OPERATOR_NAME_REQUIRED]" in privacy_copy
    assert "https://www.vibe-signal.com" in privacy_copy
    assert "Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes." in privacy_copy
    assert "Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes." in privacy_copy
    assert "No raw messages are used for training." in privacy_copy
    assert "No analytics, cookies, or tracking are added by this implementation." in privacy_copy

    terms = client.get("/legal/terms").json()
    terms_copy = " ".join(terms["sections"])
    assert "Only submit text you have permission to analyze." in terms_copy
    assert "Prohibited use includes stalking, harassment, coercion, manipulation, or trying to make someone respond." in terms_copy
    assert "[LIMITATION_OF_LIABILITY_REQUIRES_LEGAL_REVIEW]" in terms_copy
    assert "[GOVERNING_LAW_REQUIRES_LEGAL_REVIEW]" in terms_copy

    data_request = client.get("/legal/data-deletion").json()
    data_request_copy = " ".join(data_request["sections"])
    for required in ("access/export", "deletion", "correction", "objection/restriction"):
        assert required in data_request_copy
    assert "[RESPONSE_TIMELINE_REQUIRES_LEGAL_REVIEW]" in data_request_copy

    disclaimer = client.get("/legal/match-disclaimer").json()
    disclaimer_copy = " ".join(disclaimer["sections"])
    assert "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes." in disclaimer_copy
