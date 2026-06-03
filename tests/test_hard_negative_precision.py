from __future__ import annotations

from vibesignal_ai.matching.features import extract_matching_features


def _cues(messages: list[dict[str, str]]) -> set[str]:
    result = extract_matching_features(messages, conversation_id="synthetic_hard_negative_precision")
    return {str(row["cue_family"]) for row in result.all_evidence}


def test_hedged_concrete_plan_does_not_create_cross_speaker_specificity_drop() -> None:
    messages = [
        {"id": "m1", "author": "self", "created_at": "2026-06-03T10:00:00Z", "text": "I think 7 works, but I will confirm by 3."},
        {"id": "m2", "author": "other", "created_at": "2026-06-03T10:05:00Z", "text": "That timing works."},
    ]

    cues = _cues(messages)

    assert "specificity_drop" not in cues


def test_softener_without_pressure_is_reassurance_not_directness() -> None:
    cues = _cues(
        [
            {"id": "m1", "author": "self", "text": "No rush, just send it when you can."},
            {"id": "m2", "author": "other", "text": "Will do."},
        ]
    )

    assert "reassurance" in cues
    assert "directness" not in cues
    assert "pressure" not in cues


def test_urgency_with_no_stress_does_not_create_pressure() -> None:
    cues = _cues(
        [
            {"id": "m1", "author": "self", "text": "Can you send it by 5? No stress if not."},
            {"id": "m2", "author": "other", "text": "I can send it by 4."},
        ]
    )

    assert "urgency" in cues
    assert "pressure" not in cues

