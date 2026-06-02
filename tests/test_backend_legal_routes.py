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
        assert "legal review before public launch" in body["review_note"].lower()


def test_match_disclaimer_route_keeps_required_safety_copy() -> None:
    client = TestClient(app)

    response = client.get("/legal/match-disclaimer")

    assert response.status_code == 200
    body = response.json()
    combined_copy = " ".join(body["sections"]).lower()
    assert "communication-support only" in combined_copy
    assert "pattern-based suggestions, not truth claims" in combined_copy
    assert "third-party private messages without permission" in combined_copy
    assert "medical data" in combined_copy
    assert "financial data" in combined_copy
    assert "legal documents" in combined_copy
    assert "closed beta is not production launch" in combined_copy
    assert "attraction" not in combined_copy
    assert "hidden intent" not in combined_copy
    assert "cheating" not in combined_copy
