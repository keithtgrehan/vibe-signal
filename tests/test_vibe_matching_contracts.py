from __future__ import annotations

import json
from pathlib import Path

from vibesignal_ai.matching import (
    match_conversation,
    normalize_match_request,
    validate_match_request,
    validate_match_result,
)


ROOT = Path(__file__).resolve().parents[1]


def valid_request() -> dict:
    return {
        "conversation_id": "synthetic_match_contract",
        "messages": [
            {
                "id": "m1",
                "author": "self",
                "text": "Can you confirm Friday at 3pm?",
                "created_at": "2026-05-31T10:00:00Z",
            },
            {
                "id": "m2",
                "author": "other",
                "text": "Yes, Friday at 3pm works.",
                "created_at": "2026-05-31T10:01:00Z",
            },
        ],
        "user_preferences": {
            "prefers_directness": True,
            "prefers_low_pressure": True,
            "prefers_explicit_plans": True,
            "max_message_load": "low",
        },
    }


def test_match_request_schema_file_covers_required_contract_fields() -> None:
    schema = json.loads((ROOT / "schemas" / "vibe_match_request.schema.json").read_text(encoding="utf-8"))

    assert schema["required"] == ["conversation_id", "messages"]
    assert schema["properties"]["messages"]["items"]["required"] == ["id", "author", "text"]
    assert set(schema["properties"]["messages"]["items"]["properties"]["author"]["enum"]) == {"self", "other", "unknown"}


def test_match_result_schema_file_blocks_hidden_state_fields() -> None:
    schema = json.loads((ROOT / "schemas" / "vibe_match_result.schema.json").read_text(encoding="utf-8"))

    assert "blocked_interpretations" in schema["required"]
    unsafe_field_names = json.dumps(schema.get("not", {}))
    assert "deception_score" in unsafe_field_names
    assert "attraction_score" in unsafe_field_names
    assert "diagnosis" in unsafe_field_names


def test_validate_and_normalize_match_request() -> None:
    payload = valid_request()

    assert validate_match_request(payload) == []
    normalized = normalize_match_request(payload)

    assert normalized["conversation_id"] == "synthetic_match_contract"
    assert normalized["messages"][0]["speaker_role"] == "self"
    assert normalized["user_preferences"]["max_message_load"] == "low"


def test_invalid_match_request_reports_specific_errors() -> None:
    payload = valid_request()
    payload["messages"][0]["author"] = "partner"
    payload["user_preferences"]["max_message_load"] = "tiny"

    errors = validate_match_request(payload)

    assert "messages[0].author must be one of ['other', 'self', 'unknown']" in errors
    assert "user_preferences.max_message_load must be one of ['high', 'low', 'medium']" in errors


def test_match_result_validates_after_running_engine() -> None:
    result = match_conversation(valid_request())

    assert validate_match_result(result) == []
    assert result["conversation_id"] == "synthetic_match_contract"
    assert result["compatibility_band"] in {"low", "mixed", "moderate", "strong"}
    assert 0.0 <= result["score"] <= 1.0
    assert result["blocked_interpretations"] == [
        "deception",
        "hidden_intent",
        "attraction",
        "cheating",
        "diagnosis",
        "neurotype",
        "attachment_style",
        "manipulation",
        "emotional_truth",
    ]
