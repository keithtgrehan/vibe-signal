from __future__ import annotations

from vibesignal_ai.features.cue_taxonomy import detect_cues


def _cue_ids(messages: list[dict[str, str]]) -> set[str]:
    return {str(row["cue_family"]) for row in detect_cues(messages, conversation_id="synthetic_response_timing")}


def test_response_timing_requires_timestamps() -> None:
    cues = _cue_ids(
        [
            {"id": "m1", "author": "self", "text": "Can you confirm?"},
            {"id": "m2", "author": "self", "text": "Following up with one more detail."},
        ]
    )

    assert "response_timing" not in cues


def test_response_timing_requires_short_same_author_gap() -> None:
    cues = _cue_ids(
        [
            {"id": "m1", "author": "self", "created_at": "2026-06-03T10:00:00Z", "text": "Can you confirm?"},
            {"id": "m2", "author": "self", "created_at": "2026-06-03T10:01:00Z", "text": "Following up with one more detail."},
        ]
    )

    assert "response_timing" in cues


def test_response_timing_does_not_fire_for_spaced_followup() -> None:
    cues = _cue_ids(
        [
            {"id": "m1", "author": "self", "created_at": "2026-06-03T10:00:00Z", "text": "Can you confirm?"},
            {"id": "m2", "author": "self", "created_at": "2026-06-03T10:05:00Z", "text": "Following up with one more detail."},
        ]
    )

    assert "response_timing" not in cues
