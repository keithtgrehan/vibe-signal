from __future__ import annotations

from vibesignal_ai.evidence.objects import validate_evidence_object
from vibesignal_ai.features.cue_taxonomy import detect_cues


def by_cue(cues: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for cue in cues:
        grouped.setdefault(cue["cue_id"], []).append(cue)
    return grouped


def test_detect_cues_returns_valid_evidence_objects() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "created_at": "2026-05-31T10:00:00Z", "text": "Please confirm by Friday."}],
        conversation_id="synthetic_unit",
    )

    assert {"directness", "specificity"} <= set(by_cue(cues))
    for cue in cues:
        assert validate_evidence_object(cue) == []
        assert cue["interpretation_limits"]["does_not_infer_true_emotion"] is True


def test_reducers_suppress_pressure_and_urgency() -> None:
    cues = by_cue(
        detect_cues(
            [{"id": "m1", "author": "self", "created_at": "2026-05-31T10:00:00Z", "text": "No pressure and no rush, please reply when you can."}],
            conversation_id="synthetic_unit",
        )
    )

    assert "reassurance" in cues
    assert "pressure" not in cues
    assert "urgency" not in cues


def test_response_timing_hidden_without_timestamps() -> None:
    cues = by_cue(
        detect_cues(
            [
                {"id": "m1", "author": "self", "text": "Can you confirm?"},
                {"id": "m2", "author": "self", "text": "Just checking."},
            ],
            conversation_id="synthetic_unit",
        )
    )

    assert "response_timing" not in cues


def test_quoted_lines_are_excluded_from_detection() -> None:
    cues = by_cue(
        detect_cues(
            [{"id": "m1", "author": "self", "created_at": "2026-05-31T10:00:00Z", "text": "> Please confirm by Friday.\nMaybe later."}],
            conversation_id="synthetic_unit",
        )
    )

    assert "hedging" in cues
    assert "directness" not in cues
    assert "specificity" not in cues
