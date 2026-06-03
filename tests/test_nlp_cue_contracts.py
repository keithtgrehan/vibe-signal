from __future__ import annotations

import json
import re

from vibesignal_ai.matching import match_conversation


def _request(messages: list[dict], *, conversation_id: str) -> dict:
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


def _cue_families(result: dict) -> set[str]:
    return {str(row.get("cue_family", "")) for row in result["evidence"]}


def _generated_text(result: dict) -> str:
    return " ".join(
        [
            result["safe_summary"],
            result["safe_explanation"],
            " ".join(result["top_alignment_factors"]),
            " ".join(result["top_friction_factors"]),
            " ".join(row.get("safe_phrase", "") for row in result["evidence"]),
            " ".join(row.get("explanation", "") for row in result["evidence"]),
            " ".join(row.get("repair_suggestion", "") for row in result["evidence"]),
        ]
    )


def test_urgency_without_coercive_wording_does_not_become_pressure() -> None:
    result = match_conversation(
        _request(
            [
                {
                    "id": "m1",
                    "author": "self",
                    "text": "Can you send the notes by tonight before the deadline?",
                    "created_at": "2026-05-31T10:00:00Z",
                },
                {
                    "id": "m2",
                    "author": "other",
                    "text": "Yes, I can send the notes by tonight.",
                    "created_at": "2026-05-31T10:01:00Z",
                },
            ],
            conversation_id="synthetic_urgency_not_pressure",
        )
    )

    cues = _cue_families(result)
    assert "urgency" in cues
    assert "pressure" not in cues
    assert "boundary_pressure" not in cues


def test_pressure_and_boundary_pressure_label_wording_not_person() -> None:
    result = match_conversation(
        _request(
            [
                {"id": "m1", "author": "self", "text": "Can you answer by tonight?", "created_at": "2026-05-31T10:00:00Z"},
                {"id": "m2", "author": "other", "text": "You have to answer right now or else.", "created_at": "2026-05-31T10:01:00Z"},
            ],
            conversation_id="synthetic_pressure_wording_not_person",
        )
    )

    cues = _cue_families(result)
    assert "pressure" in cues
    assert "boundary_pressure" in cues
    assert "escalation_risk" in cues
    generated = _generated_text(result).lower()
    assert "unsafe person" not in generated
    assert "abusive" not in generated
    assert "personality" not in generated


def test_contradiction_is_not_rendered_as_deception() -> None:
    result = match_conversation(
        _request(
            [
                {"id": "m1", "author": "other", "text": "I can meet Friday at 3pm.", "created_at": "2026-05-31T10:00:00Z"},
                {"id": "m2", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T10:01:00Z"},
                {"id": "m3", "author": "other", "text": "I can't meet Friday.", "created_at": "2026-05-31T10:02:00Z"},
            ],
            conversation_id="synthetic_contradiction_not_deception",
        )
    )

    assert "contradiction_against_prior_message" in _cue_families(result)
    generated = _generated_text(result).lower()
    assert not re.search(r"\bl(ying|ie|ied)\b", generated)
    assert "deception" not in generated


def test_reassurance_is_not_rendered_as_attachment_or_anxiety_label() -> None:
    result = match_conversation(
        _request(
            [
                {"id": "m1", "author": "self", "text": "Can you send the notes by Friday?", "created_at": "2026-05-31T10:00:00Z"},
                {
                    "id": "m2",
                    "author": "other",
                    "text": "Yes, Friday works. No pressure if you need more time.",
                    "created_at": "2026-05-31T10:01:00Z",
                },
            ],
            conversation_id="synthetic_reassurance_not_identity_label",
        )
    )

    assert "reassurance" in _cue_families(result)
    generated = _generated_text(result).lower()
    assert "attachment" not in generated
    assert "anxiety" not in generated
    assert "romantic" not in generated
    assert "interest" not in generated


def test_evidence_contract_contains_required_explainability_fields() -> None:
    result = match_conversation(
        _request(
            [
                {"id": "m1", "author": "self", "text": "Can you confirm Friday at 3pm?", "created_at": "2026-05-31T10:00:00Z"},
                {"id": "m2", "author": "other", "text": "Maybe later. Anyway.", "created_at": "2026-05-31T10:01:00Z"},
            ],
            conversation_id="synthetic_evidence_contract_required_fields",
        )
    )

    assert result["evidence"]
    for row in result["evidence"]:
        assert row["cue_id"]
        assert row["cue_family"]
        assert row["evidence_text"]
        assert row["span_end"] > row["span_start"]
        assert row["safe_phrase"]
        assert row["explanation"]
        assert row["repair_suggestion"]
        assert row["signal_strength"] in {"low", "medium"}
        assert row["interpretation_limits"]["does_not_infer_true_emotion"] is True
        assert row["interpretation_limits"]["does_not_detect_deception"] is True
        assert row["interpretation_limits"]["does_not_score_personality"] is True

    generated = json.dumps(result)
    assert not re.search(r"\b\d{1,3}\s?%\b", generated)
