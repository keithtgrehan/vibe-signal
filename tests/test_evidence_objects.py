from __future__ import annotations

from pathlib import Path

from vibesignal_ai.evidence.objects import (
    build_evidence_object,
    stable_text_hash,
    validate_evidence_object,
)
from vibesignal_ai.evidence.export import load_evidence_jsonl, write_evidence_jsonl


def valid_object() -> dict:
    return build_evidence_object(
        evidence_id="ev_1",
        conversation_id="conversation_1",
        source_type="whatsapp_export",
        message_id="msg_1",
        turn_id="turn_1",
        speaker_role="self",
        cue_name="directness_shift",
        evidence_text="Can you confirm by Friday?",
        start_offset=0,
        end_offset=26,
        provenance={"source": "unit_test", "note": "synthetic fixture"},
        interpretation_limits={
            "does_not_infer_true_emotion": True,
            "does_not_detect_deception": True,
            "does_not_score_personality": True,
        },
    )


def test_valid_evidence_object_passes() -> None:
    row = valid_object()

    assert validate_evidence_object(row) == []
    assert row["text_sha256"] == stable_text_hash("Can you confirm by Friday?")


def test_missing_required_fields_fail() -> None:
    row = valid_object()
    row.pop("conversation_id")

    errors = validate_evidence_object(row)

    assert any("missing required field conversation_id" in error for error in errors)


def test_unsafe_fields_fail() -> None:
    row = valid_object()
    row["deception_score"] = 0.9
    row["emotion_label"] = "happy"

    errors = validate_evidence_object(row)

    assert "unsafe field deception_score is not allowed" in errors
    assert "unsafe field emotion_label is not allowed" in errors


def test_missing_interpretation_limits_fail() -> None:
    row = valid_object()
    row["interpretation_limits"].pop("does_not_detect_deception")

    errors = validate_evidence_object(row)

    assert any("missing interpretation limit does_not_detect_deception" in error for error in errors)


def test_hash_is_deterministic() -> None:
    assert stable_text_hash("same text") == stable_text_hash("same text")
    assert stable_text_hash("same text") != stable_text_hash("different text")
    assert stable_text_hash("same text").startswith("sha256:")


def test_jsonl_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "evidence.jsonl"
    row = valid_object()

    write_evidence_jsonl(path, [row])
    loaded = load_evidence_jsonl(path)

    assert loaded == [row]
