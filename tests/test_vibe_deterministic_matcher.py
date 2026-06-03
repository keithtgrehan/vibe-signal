from __future__ import annotations

import pytest

from vibesignal_ai.matching import match_conversation
from vibesignal_ai.matching.deterministic_matcher import band_for_score, clamp_score


def request_with(messages: list[dict], *, conversation_id: str = "synthetic_matcher") -> dict:
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


def test_score_clamp_and_band_mapping() -> None:
    assert clamp_score(-2.0) == 0.0
    assert clamp_score(2.0) == 1.0
    assert band_for_score(0.34) == "low"
    assert band_for_score(0.35) == "mixed"
    assert band_for_score(0.55) == "moderate"
    assert band_for_score(0.75) == "moderate"
    assert band_for_score(0.76) == "strong"


def test_high_alignment_conversation_gets_moderate_or_strong_band() -> None:
    result = match_conversation(
        request_with(
            [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T10:00:00Z"},
                {"id": "m2", "author": "other", "text": "Yes, Friday at 3pm works. No pressure if we need to adjust.", "created_at": "2026-05-31T10:02:00Z"},
                {"id": "m3", "author": "self", "text": "That works, thanks for confirming.", "created_at": "2026-05-31T10:03:00Z"},
            ]
        )
    )

    assert result["score"] >= 0.55
    assert result["compatibility_band"] in {"moderate", "strong"}
    assert any("specificity" in factor.lower() for factor in result["top_alignment_factors"])
    assert result["redline_status"] == "allow"


def test_pressure_and_evasion_lower_score_and_return_evidence() -> None:
    result = match_conversation(
        request_with(
            [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T10:00:00Z"},
                {"id": "m2", "author": "other", "text": "Maybe later. Anyway, why are you asking?", "created_at": "2026-05-31T10:01:00Z"},
                {"id": "m3", "author": "other", "text": "You always make this difficult and you have to stop.", "created_at": "2026-05-31T10:02:00Z"},
            ],
            conversation_id="synthetic_pressure_evasion",
        )
    )

    assert result["score"] < 0.55
    assert result["compatibility_band"] in {"low", "mixed"}
    assert result["answer_evasion_pattern"]
    assert result["unsupported_claim_shift"]
    assert result["inconsistency_cues"]
    assert all("evidence_id" in item and item["evidence_text"] for item in result["inconsistency_cues"])


def test_specificity_drop_and_contradiction_return_safe_cues() -> None:
    result = match_conversation(
        request_with(
            [
                {"id": "m1", "author": "other", "text": "I can meet Friday at 3pm.", "created_at": "2026-05-31T09:00:00Z"},
                {"id": "m2", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T09:01:00Z"},
                {"id": "m3", "author": "other", "text": "I can't meet Friday. Maybe later.", "created_at": "2026-05-31T09:02:00Z"},
            ],
            conversation_id="synthetic_specificity_contradiction",
        )
    )

    assert result["specificity_drop"] == []
    assert result["contradiction_against_prior_message"]
    assert result["contradiction_against_prior_message"][0]["safe_phrase"] == "This reply conflicts with an earlier stated availability/commitment."
    assert "lied" not in result["safe_summary"].lower()


def test_specificity_drop_requires_prior_direct_ask_and_non_answer() -> None:
    result = match_conversation(
        request_with(
            [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T09:01:00Z"},
                {"id": "m2", "author": "other", "text": "Maybe later.", "created_at": "2026-05-31T09:02:00Z"},
            ],
            conversation_id="synthetic_specificity_drop_non_answer",
        )
    )

    assert result["specificity_drop"]
    assert result["answer_evasion_pattern"]


def test_match_request_rejects_debug_summary_override() -> None:
    with pytest.raises(ValueError, match="unsupported field"):
        match_conversation(
            {
                "conversation_id": "synthetic_debug_override_rejected",
                "messages": [
                    {"id": "m1", "author": "self", "text": "Can you confirm Friday?"},
                    {"id": "m2", "author": "other", "text": "Maybe later."},
                ],
                "debug_summary_override": "They lied.",
            }
        )


def test_repeated_negative_availability_is_not_a_contradiction() -> None:
    result = match_conversation(
        request_with(
            [
                {"id": "m1", "author": "other", "text": "I can't meet Friday.", "created_at": "2026-05-31T09:00:00Z"},
                {"id": "m2", "author": "self", "text": "Thanks for confirming.", "created_at": "2026-05-31T09:01:00Z"},
                {"id": "m3", "author": "other", "text": "I can't meet Friday.", "created_at": "2026-05-31T09:02:00Z"},
            ],
            conversation_id="synthetic_repeated_negative_availability",
        )
    )

    assert result["contradiction_against_prior_message"] == []


def test_confidence_downgrades_for_short_one_sided_missing_timestamp_input() -> None:
    result = match_conversation(
        request_with(
            [
                {"id": "m1", "author": "self", "text": "Maybe later."},
            ],
            conversation_id="synthetic_low_confidence",
        )
    )

    assert result["confidence"]["level"] == "low"
    assert result["confidence"]["score"] < 0.55
    assert any("short" in reason.lower() for reason in result["confidence"]["reasons"])
    assert any("one-sided" in reason.lower() for reason in result["confidence"]["reasons"])
    assert any("timestamps" in reason.lower() for reason in result["confidence"]["reasons"])
