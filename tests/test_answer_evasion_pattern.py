from __future__ import annotations

from vibesignal_ai.matching.features import extract_matching_features


def test_clarifying_reply_to_overloaded_ask_is_not_evasion() -> None:
    result = extract_matching_features(
        [
            {
                "id": "m1",
                "author": "self",
                "text": "Can you confirm the time, place, backup plan, printed copy, and what to prepare before tomorrow?",
            },
            {
                "id": "m2",
                "author": "other",
                "text": "Can you send one request first so I can answer clearly?",
            },
        ],
        conversation_id="synthetic_answer_evasion_precision",
    )

    assert result.answer_evasion_pattern == []
    assert result.specificity_drop == []


def test_relevant_works_reply_is_not_evasion() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "self", "text": "Could you confirm Saturday lunch for a longer check-in?"},
            {"id": "m2", "author": "other", "text": "Saturday lunch works, and we can keep it simple."},
        ],
        conversation_id="synthetic_answer_evasion_precision",
    )

    assert result.answer_evasion_pattern == []


def test_direct_question_followed_by_vague_topic_change_is_evasion() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "self", "text": "Can you confirm Friday at 7pm and the place?"},
            {"id": "m2", "author": "other", "text": "Maybe later. Anyway."},
        ],
        conversation_id="synthetic_answer_evasion_precision",
    )

    assert result.answer_evasion_pattern
    assert result.specificity_drop


def test_topic_bridge_before_answer_is_not_evasion() -> None:
    result = extract_matching_features(
        [
            {"id": "m1", "author": "self", "text": "Can you answer the budget question?"},
            {"id": "m2", "author": "other", "text": "I will answer that, but first I need one detail."},
        ],
        conversation_id="synthetic_answer_evasion_topic_bridge",
    )

    assert result.answer_evasion_pattern == []
