from __future__ import annotations

from vibesignal_ai.features.cue_taxonomy import detect_cues
from vibesignal_ai.matching.features import extract_matching_features


def _families(rows: list[dict]) -> set[str]:
    return {str(row["cue_family"]) for row in rows}


def test_unclear_timing_and_unclear_ask_are_observable_only() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "text": "Can we figure out that thing at some point maybe?"}],
        conversation_id="synthetic_private_inspired_unclear_timing",
    )

    assert {"ambiguity", "unclear_ask"} <= _families(cues)


def test_unanswered_ask_candidate_handles_vague_deferral() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "self", "text": "Can we confirm the plan by 5pm?"},
            {"id": "m2", "author": "other", "text": "Let me see later, not sure yet."},
        ],
        conversation_id="synthetic_private_inspired_unanswered",
    )

    assert result.answer_evasion_pattern


def test_boundary_pressure_requires_boundary_sensitive_context_for_have_to() -> None:
    neutral = detect_cues(
        [{"id": "m1", "author": "self", "text": "You have to submit the form by noon."}],
        conversation_id="synthetic_private_inspired_neutral_deadline",
    )
    boundary = detect_cues(
        [{"id": "m1", "author": "self", "text": "You have to prove it right now."}],
        conversation_id="synthetic_private_inspired_boundary_pressure",
    )

    assert "boundary_pressure" not in _families(neutral)
    assert "boundary_pressure" in _families(boundary)


def test_repair_attempt_patterns_include_reset_language() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "text": "My bad, I should have said this more clearly. Can we reset?"}],
        conversation_id="synthetic_private_inspired_repair",
    )

    assert "repair_opportunity" in _families(cues)


def test_pressure_with_intense_punctuation_flags_escalation_without_person_claim() -> None:
    cues = detect_cues(
        [{"id": "m1", "author": "self", "text": "You have to answer right now!!"}],
        conversation_id="synthetic_private_inspired_escalation",
    )
    rendered = " ".join(str(row.get("safe_phrase", "")) for row in cues).lower()

    assert "escalation_risk" in _families(cues)
    assert "abusive" not in rendered
    assert "diagnos" not in rendered


def test_clear_timing_and_clear_answer_are_hard_negatives() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "self", "text": "Can you reply by 4pm?"},
            {"id": "m2", "author": "other", "text": "Yes, I can reply by 4pm."},
        ],
        conversation_id="synthetic_private_inspired_hard_negative",
    )

    assert result.answer_evasion_pattern == []
    assert "pressure" not in result.cue_counts
    assert "ambiguity" not in result.cue_counts
