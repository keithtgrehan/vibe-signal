from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.config import BackendSettings
from backend.storage import EVENT_ROWS, FEEDBACK_ROWS


def test_feedback_route_dedupes_safe_client_feedback_event_id() -> None:
    client = TestClient(create_app(BackendSettings()))
    before = len(FEEDBACK_ROWS)
    payload = {
        "feedback_event_id": "evt_feedback_dedupe_001",
        "match_id": "vibe_match_dedupe_001",
        "rating": 1,
        "comment": "",
        "consent_to_store_feedback": True,
    }

    first = client.post("/api/feedback", json=payload)
    second = client.post("/api/feedback", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "accepted"
    assert second.json()["status"] == "accepted"
    assert first.json()["stored_feedback"]["feedback_id"] == second.json()["stored_feedback"]["feedback_id"]
    assert second.json()["stored_feedback"]["duplicate"] is True
    assert len(FEEDBACK_ROWS) == before + 1


def test_event_route_dedupes_safe_event_id_without_raw_payload_storage() -> None:
    client = TestClient(create_app(BackendSettings()))
    before = len(EVENT_ROWS)
    payload = {
        "event_id": "evt_backend_dedupe_001",
        "client_timestamp": 1712652000000,
        "text": "synthetic private text should not be stored",
    }

    first = client.post("/api/events/analysis", json=payload)
    second = client.post("/api/events/analysis", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "accepted"
    assert second.json()["status"] == "accepted"
    assert first.json()["stored_event"]["event_id"] == "evt_backend_dedupe_001"
    assert second.json()["stored_event"]["event_id"] == "evt_backend_dedupe_001"
    assert second.json()["stored_event"]["duplicate"] is True
    assert len(EVENT_ROWS) == before + 1
    assert "synthetic private text should not be stored" not in str(EVENT_ROWS[-1])
