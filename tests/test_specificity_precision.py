from __future__ import annotations

from vibesignal_ai.features.cue_taxonomy import detect_cues


def _cue_ids(text: str) -> set[str]:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "created_at": "2026-06-03T10:00:00Z", "text": text}],
        conversation_id="synthetic_specificity_precision",
    )
    return {str(row["cue_family"]) for row in cues}


def test_specificity_does_not_fire_on_bare_numbers() -> None:
    cues = _cue_ids("I saw 7 messages in the thread.")

    assert "specificity" not in cues


def test_specificity_requires_actionable_time_or_schedule_context() -> None:
    assert "specificity" in _cue_ids("Can you confirm Friday at 3pm?")
    assert "specificity" in _cue_ids("I cannot share my location tonight.")
