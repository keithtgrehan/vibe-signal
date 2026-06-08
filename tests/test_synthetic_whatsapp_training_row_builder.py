from __future__ import annotations

import json
from pathlib import Path

from tools.build_pattern_training_rows_from_synthetic_whatsapp import main as build_rows_main


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _sample_fixture(conversation_id: str = "fixture_001") -> dict[str, object]:
    return {
        "conversation_id": conversation_id,
        "fixture_id": conversation_id,
        "synthetic": True,
        "source_type": "synthetic_fixture",
        "not_copied_from_real_chat": True,
        "split": "dev",
        "scenario": "vague_timing",
        "category": "vague_timing",
        "expected_cues": ["ambiguity", "response_timing"],
        "expected_signal_strength": "low",
        "messages": [
            {
                "id": "m1",
                "message_id": "m1",
                "speaker": "self",
                "author": "self",
                "synthetic": True,
                "text": "When should we check in?",
            },
            {
                "id": "m2",
                "message_id": "m2",
                "speaker": "other",
                "author": "other",
                "synthetic": True,
                "text": "Maybe sometime later, not sure yet.",
            },
        ],
        "safe_repair_suggestion": "Ask for one concrete time.",
    }


def test_converter_writes_valid_jsonl_from_tiny_synthetic_fixture_sample(tmp_path: Path) -> None:
    input_dir = tmp_path / "synthetic" / "whatsapp"
    out = tmp_path / "training_rows.jsonl"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"
    _write_jsonl(input_dir / "conversations.jsonl", [_sample_fixture()])

    exit_code = build_rows_main(
        [
            "--input-dir",
            str(input_dir),
            "--out",
            str(out),
            "--manifest-out",
            str(manifest),
            "--report-out",
            str(report),
        ]
    )

    assert exit_code == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    row = rows[0]
    assert row["row_id"] == "synthetic_whatsapp_000001"
    assert row["source_tier"] == "bronze_synthetic_whatsapp_10k"
    assert row["source_type"] == "synthetic_fixture"
    assert row["rights_review_status"] == "synthetic_only"
    assert row["consent_status"] == "not_required_synthetic"
    assert row["commercial_training_allowed"] is False
    assert row["research_training_allowed"] is True
    assert row["production_use_allowed"] is False
    assert row["model_quality_claims_allowed"] is False
    assert row["contains_raw_private_text"] is False
    assert row["contains_personal_data"] is False
    assert row["redaction_status"] == "synthetic"
    assert row["review_status"] == "synthetic_expected"
    assert row["split"] == "dev"
    assert row["scenario_family"] == "vague_timing"
    assert row["expected_cues"] == ["ambiguity"]
    assert row["messages"] == [
        {"message_id": "m1", "speaker_role": "self", "text": "When should we check in?"},
        {"message_id": "m2", "speaker_role": "other", "text": "Maybe sometime later, not sure yet."},
    ]
    assert "other: Maybe sometime later, not sure yet." in row["text_for_training"]
    assert row["evidence_spans"]
    assert row["evidence_spans"][0]["cue_type"] == "ambiguity"
    assert row["evidence_spans"][0]["span"] in row["text_for_training"]
    assert "hidden_intent" in row["blocked_interpretations"]
    assert "they are lying" in row["forbidden_outputs"]
    assert "response_timing" not in row["expected_cues"]

    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_payload["row_count"] == 1
    assert manifest_payload["message_count"] == 2
    assert manifest_payload["excluded_unsupported_cue_counts"] == {"response_timing": 1}

    report_text = report.read_text(encoding="utf-8")
    assert "Synthetic-only fixture conversion" in report_text
    assert "deterministic cue engine remains primary" in report_text.lower()


def test_converter_rejects_non_synthetic_fixture_rows(tmp_path: Path) -> None:
    input_dir = tmp_path / "synthetic" / "whatsapp"
    out = tmp_path / "training_rows.jsonl"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"
    row = _sample_fixture()
    row["synthetic"] = False
    _write_jsonl(input_dir / "conversations.jsonl", [row])

    exit_code = build_rows_main(
        [
            "--input-dir",
            str(input_dir),
            "--out",
            str(out),
            "--manifest-out",
            str(manifest),
            "--report-out",
            str(report),
        ]
    )

    assert exit_code == 1
    assert not out.exists()
