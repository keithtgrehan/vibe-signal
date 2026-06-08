from __future__ import annotations

import json
from pathlib import Path

from tools.validate_synthetic_whatsapp_training_rows import main as validate_rows_main


def _valid_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "row_id": "synthetic_whatsapp_000001",
        "conversation_id": "fixture_001",
        "source_tier": "bronze_synthetic_whatsapp_10k",
        "source_type": "synthetic_fixture",
        "rights_review_status": "synthetic_only",
        "consent_status": "not_required_synthetic",
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_raw_private_text": False,
        "contains_personal_data": False,
        "redaction_status": "synthetic",
        "review_status": "synthetic_expected",
        "split": "dev",
        "scenario_family": "vague_timing",
        "synthetic": True,
        "not_copied_from_real_chat": True,
        "messages": [
            {"message_id": "m1", "speaker_role": "self", "text": "When should we check in?"},
            {"message_id": "m2", "speaker_role": "other", "text": "Maybe sometime later, not sure yet."},
        ],
        "text_for_training": "self: When should we check in?\nother: Maybe sometime later, not sure yet.",
        "expected_cues": ["ambiguity"],
        "evidence_spans": [
            {
                "cue_type": "ambiguity",
                "span": "Maybe sometime later",
                "explanation": "The phrase gives no clear timing.",
            }
        ],
        "blocked_interpretations": [
            "hidden_intent",
            "attraction",
            "deception_certainty",
            "diagnosis",
            "therapy",
            "manipulation_claim",
            "relationship_outcome",
        ],
        "forbidden_outputs": [
            "they like you",
            "they are lying",
            "this proves",
            "hidden intent",
            "gaslighting",
            "manipulating you",
            "diagnosis",
            "attachment style",
            "narcissist",
            "abusive person",
            "make them respond",
            "win them back",
        ],
        "safe_summary": "The synthetic exchange contains vague timing wording.",
        "safe_next_step": "Ask for one concrete time or pause before replying.",
    }
    row.update(overrides)
    return row


def _write_inputs(tmp_path: Path, rows: list[dict[str, object]], manifest_overrides: dict[str, object] | None = None) -> tuple[Path, Path]:
    input_path = tmp_path / "rows.jsonl"
    input_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    manifest: dict[str, object] = {
        "source_tier": "bronze_synthetic_whatsapp_10k",
        "row_count": len(rows),
        "message_count": sum(len(row["messages"]) for row in rows),
        "synthetic": True,
    }
    if manifest_overrides:
        manifest.update(manifest_overrides)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return input_path, manifest_path


def _validate(tmp_path: Path, rows: list[dict[str, object]], *extra_args: str, manifest_overrides: dict[str, object] | None = None) -> int:
    input_path, manifest_path = _write_inputs(tmp_path, rows, manifest_overrides)
    return validate_rows_main(["--input", str(input_path), "--manifest", str(manifest_path), *extra_args])


def test_validator_accepts_synthetic_only_rows(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row()]) == 0


def test_validator_rejects_commercial_training_allowed_true(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(commercial_training_allowed=True)]) == 1


def test_validator_rejects_production_use_allowed_true(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(production_use_allowed=True)]) == 1


def test_validator_rejects_model_quality_claims_allowed_true(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(model_quality_claims_allowed=True)]) == 1


def test_validator_rejects_raw_or_personal_data_flags(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(contains_raw_private_text=True)]) == 1
    assert _validate(tmp_path, [_valid_row(contains_personal_data=True)]) == 1


def test_validator_rejects_blocked_labels(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(expected_cues=["ambiguity", "gaslighting"])]) == 1


def test_validator_rejects_unsafe_safe_summary(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(safe_summary="They are lying and this proves hidden intent.")]) == 1


def test_validator_rejects_missing_evidence_spans_for_cue_positive_rows(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(evidence_spans=[])]) == 1


def test_validator_allows_missing_evidence_for_low_signal_or_neutral(tmp_path: Path) -> None:
    row = _valid_row(expected_cues=["low_signal"], evidence_spans=[])
    assert _validate(tmp_path, [row]) == 0
    row = _valid_row(expected_cues=["neutral"], evidence_spans=[])
    assert _validate(tmp_path, [row]) == 0


def test_validator_rejects_evidence_spans_that_do_not_appear_in_text(tmp_path: Path) -> None:
    row = _valid_row(
        evidence_spans=[
            {
                "cue_type": "ambiguity",
                "span": "not in the conversation",
                "explanation": "Missing span.",
            }
        ]
    )
    assert _validate(tmp_path, [row]) == 1


def test_validator_rejects_missing_forbidden_outputs_or_blocked_interpretations(tmp_path: Path) -> None:
    assert _validate(tmp_path, [_valid_row(forbidden_outputs=[])]) == 1
    assert _validate(tmp_path, [_valid_row(blocked_interpretations=[])]) == 1


def test_validator_rejects_row_count_mismatch_unless_partial_sample_allowed(tmp_path: Path) -> None:
    row = _valid_row()
    assert _validate(tmp_path, [row], manifest_overrides={"row_count": 2}) == 1
    assert _validate(tmp_path, [row], "--allow-partial-sample", manifest_overrides={"row_count": 2}) == 0
