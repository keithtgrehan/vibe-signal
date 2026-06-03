from __future__ import annotations

from vibesignal_ai.features.cue_taxonomy import detect_cues


def _cue_ids(messages: list[dict[str, str]]) -> set[str]:
    return {
        str(row["cue_family"])
        for row in detect_cues(messages, conversation_id="synthetic_topic_shift_precision")
    }


def test_topic_shift_requires_relevant_previous_ask() -> None:
    cues = _cue_ids(
        [
            {"id": "m1", "author": "self", "created_at": "2026-06-03T10:00:00Z", "text": "Anyway, here is the plan."},
        ]
    )

    assert "topic_shift" not in cues


def test_topic_shift_fires_when_reply_moves_away_from_previous_ask() -> None:
    cues = _cue_ids(
        [
            {"id": "m1", "author": "self", "created_at": "2026-06-03T10:00:00Z", "text": "Can we talk tonight about the plan?"},
            {"id": "m2", "author": "other", "created_at": "2026-06-03T10:05:00Z", "text": "Maybe later. Anyway, I am frustrated."},
        ]
    )

    assert "topic_shift" in cues
    assert "unclear_ask" not in cues
