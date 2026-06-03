from __future__ import annotations

from vibesignal_ai.matching import match_conversation


def _request(messages: list[dict], *, conversation_id: str = "synthetic_low_signal_case") -> dict:
    return {
        "conversation_id": conversation_id,
        "messages": messages,
        "user_preferences": {
            "prefers_directness": True,
            "prefers_low_pressure": True,
            "prefers_explicit_plans": True,
            "max_message_load": "low",
        },
    }


def test_short_context_light_exchange_uses_low_signal_fallback() -> None:
    result = match_conversation(
        _request(
            [
                {"id": "m1", "author": "self", "text": "ok", "created_at": "2026-05-31T10:00:00Z"},
                {"id": "m2", "author": "other", "text": "maybe", "created_at": "2026-05-31T10:01:00Z"},
            ]
        )
    )

    assert result["result_state"] == "low_signal"
    assert result["signal_strength"] == "insufficient"
    assert result["low_signal_fallback"] is True
    assert result["score"] == 0.5
    assert result["compatibility_band"] == "mixed"
    assert "not enough evidence-backed wording" in result["safe_summary"].lower()
    assert "%" not in result["safe_summary"]
    assert result["cannot_infer"]
    assert result["safe_next_steps"]


def test_no_normal_result_renders_without_evidence_spans() -> None:
    result = match_conversation(
        _request(
            [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T10:00:00Z"},
                {
                    "id": "m2",
                    "author": "other",
                    "text": "Yes, Friday at 3pm works. No pressure if we need to adjust.",
                    "created_at": "2026-05-31T10:02:00Z",
                },
            ],
            conversation_id="synthetic_normal_result_evidence_required",
        )
    )

    assert result["result_state"] == "ready"
    assert result["evidence"]
    for row in result["evidence"]:
        assert row["evidence_text"]
        assert row["span_end"] > row["span_start"]
        assert row["safe_phrase"]
        assert row["repair_suggestion"]
