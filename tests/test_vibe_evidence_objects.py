from __future__ import annotations

from vibesignal_ai.evidence.objects import build_evidence_object, validate_evidence_object


def valid_vibe_evidence() -> dict:
    return build_evidence_object(
        evidence_id="ev_vibe_1",
        conversation_id="synthetic_vibe_evidence",
        source_type="synthetic_fixture",
        message_id="m1",
        turn_id="m1",
        speaker_role="self",
        cue_name="directness",
        evidence_text="Please confirm Friday at 3pm.",
        start_offset=0,
        end_offset=29,
        provenance={"source": "unit_test", "note": "Synthetic fixture only."},
        cue_id="directness",
        cue_family="directness",
        span_start=0,
        span_end=29,
        confidence=0.82,
        explanation="Rule matched direct request wording.",
        safe_phrase="message contains direct request wording.",
    )


def test_vibe_evidence_object_schema_passes() -> None:
    row = valid_vibe_evidence()

    assert validate_evidence_object(row) == []
    assert row["cue_id"] == "directness"
    assert row["cue_family"] == "directness"
    assert row["span_start"] == row["start_offset"]
    assert row["span_end"] == row["end_offset"]
    assert row["safe_phrase"] == "message contains direct request wording."


def test_vibe_evidence_missing_required_new_field_fails() -> None:
    row = valid_vibe_evidence()
    row.pop("safe_phrase")

    errors = validate_evidence_object(row)

    assert "missing required field safe_phrase" in errors


def test_vibe_evidence_rejects_unsafe_generated_phrasing() -> None:
    row = valid_vibe_evidence()
    row["safe_phrase"] = "they feel angry and have an attachment style issue"

    errors = validate_evidence_object(row)

    assert "safe_phrase must start with safe cue wording" in errors
    assert any("safe_phrase contains forbidden interpretive language" in error for error in errors)


def test_vibe_evidence_rejects_invalid_confidence_and_span_alias_mismatch() -> None:
    row = valid_vibe_evidence()
    row["confidence"] = 1.4
    row["span_start"] = 4

    errors = validate_evidence_object(row)

    assert "confidence must be a number between 0 and 1" in errors
    assert "span_start must match start_offset" in errors
