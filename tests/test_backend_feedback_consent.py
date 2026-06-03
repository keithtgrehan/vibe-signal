from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app


def test_feedback_route_requires_explicit_consent() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/feedback",
        json={"match_id": "vibe_match_123", "rating": 1, "comment": "useful", "consent_to_store_feedback": False},
    )

    assert response.status_code == 400
    assert "explicit consent" in response.json()["detail"].lower()


def test_feedback_route_stores_metadata_only_when_consented() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/feedback",
        json={"match_id": "vibe_match_123", "rating": 1, "comment": "useful", "consent_to_store_feedback": True},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "accepted"
    assert body["stored_feedback"]["match_id"] == "vibe_match_123"
    assert body["stored_feedback"]["comment_length"] == 6
    assert "comment" not in body["stored_feedback"]
    assert "comment_sha256" not in body["stored_feedback"]
