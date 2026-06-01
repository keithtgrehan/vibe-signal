from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app


def test_match_route_calls_deterministic_matcher() -> None:
    client = TestClient(app)
    payload = {
        "conversation_id": "synthetic_backend_match",
        "messages": [
            {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T10:00:00Z"},
            {"id": "m2", "author": "other", "text": "Yes, Friday at 3pm works. No pressure if we need to adjust.", "created_at": "2026-05-31T10:01:00Z"},
        ],
        "user_preferences": {"prefers_directness": True, "prefers_low_pressure": True},
    }

    response = client.post("/api/match", json=payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["conversation_id"] == "synthetic_backend_match"
    assert body["redline_status"] == "allow"
    assert body["score"] >= 0.55
    assert body["safe_summary"]


def test_match_route_rejects_invalid_payload_clearly() -> None:
    client = TestClient(app)

    response = client.post("/api/match", json={"conversation_id": "bad", "messages": []})

    assert response.status_code == 400
    assert "messages must be a non-empty list" in response.json()["detail"]
