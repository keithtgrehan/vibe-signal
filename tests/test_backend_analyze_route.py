from __future__ import annotations

from fastapi.testclient import TestClient

import backend.routes.analyze as analyze_route
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


def test_analyze_route_accepts_current_web_payload_shape() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "web_analysis_synthetic_contract",
            "messages": [
                {"id": "m1", "author": "self", "text": "Are we still on for Friday?"},
                {"id": "m2", "author": "other", "text": "maybe later, not sure yet"},
            ],
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["conversation_id"] == "web_analysis_synthetic_contract"
    assert body["analysis_mode"] == "deterministic_local_only"
    assert body["provider_used"] is False
    assert body["raw_chat_persisted"] is False
    assert isinstance(body["evidence"], list)
    assert body["evidence"]


def test_analyze_route_accepts_2000_character_excerpt() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_backend_analyze_2000_chars",
            "messages": [{"id": "m1", "author": "self", "text": "a" * 2000}],
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["analysis_mode"] == "deterministic_local_only"
    assert body["raw_chat_persisted"] is False


def test_analyze_route_rejects_too_long_excerpt_without_echoing_raw_text() -> None:
    client = TestClient(app)
    raw_text = "raw-analyze-secret-" + ("a" * 2001)
    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_backend_analyze_too_long",
            "messages": [{"id": "m1", "author": "self", "text": raw_text}],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "This beta works best with short excerpts. Try 2-8 messages or under 2,000 characters."
    }
    assert "raw-analyze-secret" not in response.text


def test_analyze_route_rejects_empty_message_text_with_json_error() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_backend_analyze_empty",
            "messages": [{"id": "m1", "author": "self", "text": "   "}],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "messages must include non-empty text"}


def test_analyze_route_runtime_error_returns_safe_json(monkeypatch) -> None:
    def fail_extract(_messages, *, conversation_id):
        raise RuntimeError("raw private analysis secret should not be exposed")

    monkeypatch.setattr(analyze_route, "extract_matching_features", fail_extract)
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_backend_analyze_runtime_error",
            "messages": [{"id": "m1", "author": "self", "text": "Can you confirm Friday?"}],
        },
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "analyze service unavailable"}
    assert "raw private analysis secret" not in response.text
