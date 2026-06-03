from __future__ import annotations

from vibesignal_ai.features.cue_taxonomy import detect_cues


def _cue_ids(text: str) -> set[str]:
    return {
        str(row["cue_family"])
        for row in detect_cues(
            [{"id": "m1", "author": "self", "created_at": "2026-06-03T10:00:00Z", "text": text}],
            conversation_id="synthetic_hedging_precision",
        )
    }


def test_permission_preserving_copy_is_reassurance_not_hedging() -> None:
    cues = _cue_ids("Only if you want, you can say no.")

    assert "reassurance" in cues
    assert "hedging" not in cues


def test_maybe_later_can_be_hedging_without_emotion_inference() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "other", "created_at": "2026-06-03T10:00:00Z", "text": "Maybe later."}],
        conversation_id="synthetic_hedging_precision",
    )

    assert any(row["cue_family"] == "hedging" for row in cues)
    assert all(row["interpretation_limits"]["does_not_infer_true_emotion"] for row in cues)
