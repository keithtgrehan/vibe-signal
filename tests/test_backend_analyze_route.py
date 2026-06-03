from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app


def test_analyze_route_returns_custom_deterministic_evidence() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_backend_analyze_custom_evidence",
            "messages": [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday at 7pm and the place?"},
                {"id": "m2", "author": "other", "text": "Maybe later. Anyway."},
            ],
            "source_type": "synthetic_fixture",
            "synthetic": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    cues = {row["cue_family"] for row in body["evidence"]}
    assert "answer_evasion_pattern" in cues
    assert "specificity_drop" in cues
    assert body["signal_strength"] in {"low", "insufficient"}
    assert body["raw_chat_persisted"] is False


def test_analyze_route_uses_low_signal_for_short_sparse_text() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_backend_analyze_low_signal",
            "messages": [
                {"id": "m1", "author": "self", "text": "ok"},
                {"id": "m2", "author": "other", "text": "maybe"},
            ],
            "source_type": "synthetic_fixture",
            "synthetic": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["signal_state"] == "low_signal"
    assert body["signal_strength"] == "insufficient"
    assert body["low_signal_fallback"] is True
    assert body["cannot_infer"]
