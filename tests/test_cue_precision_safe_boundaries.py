from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app
from vibesignal_ai.features.cue_taxonomy import detect_cues
from vibesignal_ai.matching.features import extract_matching_features


def _render(rows: list[dict]) -> str:
    return " ".join(f"{row.get('safe_phrase', '')} {row.get('explanation', '')}" for row in rows).lower()


def test_urgency_is_not_automatically_pressure() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "text": "The deadline is tonight, but no rush if tomorrow is better."}],
        conversation_id="synthetic_urgency_not_pressure",
    )
    families = {row["cue_family"] for row in cues}

    assert "pressure" not in families


def test_reassurance_is_not_anxiety_or_attachment_label() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "text": "No pressure if not, all good."}],
        conversation_id="synthetic_reassurance_not_attachment",
    )
    rendered = _render(cues)

    assert "reassurance" in {row["cue_family"] for row in cues}
    assert "anxiety" not in rendered
    assert "attachment" not in rendered


def test_conflict_language_does_not_label_person_or_diagnose() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "self", "text": "I am frustrated because the plan changed."},
            {"id": "m2", "author": "other", "text": "Sorry, let me rephrase the ask."},
        ],
        conversation_id="synthetic_conflict_not_person_label",
    )
    rendered = _render(result.all_evidence)

    assert "diagnos" not in rendered
    assert "abusive" not in rendered
    assert "narcissist" not in rendered


def test_conflict_with_intense_punctuation_can_flag_escalation_without_person_label() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "other", "text": "I am frustrated!! Sorry, let me rephrase."}],
        conversation_id="synthetic_conflict_escalation_precision",
    )
    families = {row["cue_family"] for row in cues}
    rendered = _render(cues)

    assert "escalation_risk" in families
    assert "abusive" not in rendered
    assert "diagnos" not in rendered


def test_short_context_light_messages_fallback_when_analyzed() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={
            "conversation_id": "synthetic_short_context_light",
            "messages": [
                {"id": "m1", "author": "self", "text": "ok"},
                {"id": "m2", "author": "other", "text": "maybe"},
            ],
        },
    )
    body = response.json()

    assert response.status_code == 200, response.text
    assert body["signal_state"] == "low_signal"
    assert body["signal_strength"] == "insufficient"
    assert body["low_signal_fallback"] is True
