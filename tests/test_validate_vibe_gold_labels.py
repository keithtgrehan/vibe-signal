from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_vibe_gold_labels.py"
EXAMPLE = ROOT / "data" / "vibe_gold" / "example_gold_labels.jsonl"


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--path", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_example_gold_labels_validate() -> None:
    result = run_validator(EXAMPLE)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed" in result.stdout


def test_invalid_enum_and_duplicate_label_id_fail(tmp_path: Path) -> None:
    rows = [
        {
            "conversation_id": "conv_1",
            "label_id": "label_1",
            "label_type": "not_allowed",
            "direction": "present",
            "speaker_role": "self",
            "evidence_text": "Please reply now.",
            "evidence_start": 0,
            "evidence_end": 17,
            "confidence": "medium",
            "reviewer": "unit",
            "notes": "bad enum",
        },
        {
            "conversation_id": "conv_1",
            "label_id": "label_1",
            "label_type": "neutral",
            "direction": "neutral",
            "speaker_role": "unknown",
            "evidence_text": "",
            "evidence_start": 0,
            "evidence_end": 0,
            "confidence": "low",
            "reviewer": "unit",
            "notes": "duplicate id",
        },
    ]
    path = tmp_path / "bad.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "invalid label_type" in result.stdout
    assert "duplicate label_id" in result.stdout


def test_non_neutral_requires_evidence_and_valid_offsets(tmp_path: Path) -> None:
    row = {
        "conversation_id": "conv_1",
        "label_id": "label_2",
        "label_type": "pressure_language",
        "direction": "present",
        "speaker_role": "other",
        "evidence_text": "",
        "evidence_start": 5,
        "evidence_end": 3,
        "confidence": "high",
        "reviewer": "unit",
        "notes": "missing evidence and bad offsets",
    }
    path = tmp_path / "bad_offsets.jsonl"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "evidence_text is required for non-neutral labels" in result.stdout
    assert "evidence_end must be >= evidence_start" in result.stdout


def test_blocks_unsafe_fields_and_requires_jsonl(tmp_path: Path) -> None:
    row = {
        "conversation_id": "conv_1",
        "label_id": "label_3",
        "label_type": "neutral",
        "direction": "neutral",
        "speaker_role": "unknown",
        "evidence_text": "",
        "evidence_start": 0,
        "evidence_end": 0,
        "confidence": "low",
        "reviewer": "unit",
        "notes": "unsafe",
        "deception_score": 0.7,
    }
    path = tmp_path / "unsafe.jsonl"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "unsafe field deception_score" in result.stdout

    wrong_suffix = tmp_path / "labels.json"
    wrong_suffix.write_text(json.dumps(row), encoding="utf-8")
    suffix_result = run_validator(wrong_suffix)
    assert suffix_result.returncode == 1
    assert "JSONL" in suffix_result.stdout


def test_provider_external_and_weak_rows_cannot_be_gold(tmp_path: Path) -> None:
    row = {
        "conversation_id": "conv_1",
        "label_id": "label_4",
        "label_type": "neutral",
        "direction": "neutral",
        "speaker_role": "unknown",
        "evidence_text": "",
        "evidence_start": 0,
        "evidence_end": 0,
        "confidence": "low",
        "reviewer": "unit",
        "notes": "external rows must stay out of gold",
        "source_type": "provider_response_metadata",
        "weak_label": True,
    }
    path = tmp_path / "provider_gold.jsonl"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "provider or external source rows cannot become gold labels" in result.stdout
    assert "weak or auto-promoted labels cannot become gold labels" in result.stdout
