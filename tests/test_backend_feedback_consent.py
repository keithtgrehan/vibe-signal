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


def test_feedback_route_keeps_bounded_cue_metadata_without_raw_text() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/feedback",
        json={
            "feedback_event_id": "evt_feedback_cue_001",
            "match_id": "vibe_match_456",
            "rating": 1,
            "feedback_tag": "cue_fits",
            "comment": "raw free text should not be returned",
            "consent_to_store_feedback": True,
            "cue_id": "evidence_1",
            "cue_family": "vague_timing",
            "evidence_quality": "strong",
            "goal_id": "over_reading",
            "context_id": "work",
            "analysis_style_id": "careful",
            "low_signal": False,
            "synthetic": True,
            "client_timestamp": "1712652000000",
            "raw_message_text": "private message",
            "evidence_text": "quoted private phrase",
            "draft_reply_text": "draft private reply",
        },
    )

    assert response.status_code == 200, response.text
    stored = response.json()["stored_feedback"]
    assert stored["feedback_event_id"] == "evt_feedback_cue_001"
    assert stored["feedback_tag"] == "cue_fits"
    assert stored["cue_id"] == "evidence_1"
    assert stored["cue_family"] == "vague_timing"
    assert stored["evidence_quality"] == "strong"
    assert stored["goal_id"] == "over_reading"
    assert stored["context_id"] == "work"
    assert stored["analysis_style_id"] == "careful"
    assert stored["low_signal"] is False
    assert stored["synthetic"] is True
    assert stored["client_timestamp"] == "1712652000000"
    assert "comment" not in stored
    assert "raw_message_text" not in stored
    assert "evidence_text" not in stored
    assert "draft_reply_text" not in stored


def test_feedback_route_bounds_match_id_metadata() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/feedback",
        json={
            "match_id": "vibe match private@example.com raw phrase " + ("x" * 80),
            "rating": 0,
            "feedback_tag": "missed_context",
            "comment": "metadata only",
            "consent_to_store_feedback": True,
        },
    )

    assert response.status_code == 200, response.text
    stored = response.json()["stored_feedback"]
    assert stored["match_id"].startswith("vibe_match_private_example.com_raw_phrase_")
    assert len(stored["match_id"]) == 64
    assert " " not in stored["match_id"]
    assert "@" not in stored["match_id"]
    assert "private@example.com raw phrase" not in stored["match_id"]
