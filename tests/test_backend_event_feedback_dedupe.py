from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.config import BackendSettings
from backend.storage import ALLOWED_MONITORING_EVENT_TYPES, EVENT_ROWS, FEEDBACK_ROWS


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


def test_event_route_keeps_only_allowlisted_monitoring_metadata() -> None:
    client = TestClient(create_app(BackendSettings()))
    before = len(EVENT_ROWS)
    payload = {
        "event_id": "evt_monitoring_contract_001",
        "monitoring_event_type": "analysis_succeeded",
        "client_timestamp": 1712652000000,
        "synthetic": True,
        "evidence_quote": "synthetic message text must not be persisted",
        "raw_input_text": "synthetic raw input must not be persisted",
    }

    response = client.post("/api/events/analysis", json=payload)

    assert response.status_code == 200
    stored = response.json()["stored_event"]
    assert stored["monitoring_event_type"] == "analysis_succeeded"
    assert stored["synthetic"] is True
    assert "synthetic message text must not be persisted" not in str(EVENT_ROWS[before:])
    assert "synthetic raw input must not be persisted" not in str(EVENT_ROWS[before:])


def test_event_route_downgrades_unknown_monitoring_event_type() -> None:
    client = TestClient(create_app(BackendSettings()))
    payload = {
        "event_id": "evt_monitoring_contract_002",
        "monitoring_event_type": "unsafe_custom_event_with_private_text",
        "client_timestamp": 1712652000000,
    }

    response = client.post("/api/events/state", json=payload)

    assert response.status_code == 200
    assert response.json()["stored_event"]["monitoring_event_type"] == "unspecified"
    assert "unsafe_custom_event_with_private_text" not in str(EVENT_ROWS[-1])


def test_monitoring_event_contract_covers_closed_beta_p0_events() -> None:
    assert {
        "analysis_started",
        "analysis_succeeded",
        "analysis_failed",
        "safety_blocked",
        "low_signal_fallback",
        "synthetic_demo_started",
        "synthetic_demo_completed",
        "user_feedback_useful",
        "user_feedback_too_strong",
        "user_feedback_missed_context",
        "user_feedback_unsafe_wording",
        "user_feedback_confusing",
    } <= ALLOWED_MONITORING_EVENT_TYPES
