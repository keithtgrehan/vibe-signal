from __future__ import annotations

import csv
import json
from pathlib import Path

from tools.build_goemotions_local_research_rows import main as build_goemotions_main
from tools.build_meld_local_research_rows import main as build_meld_main
from tools.transcript_nlp_local_research_common import (
    GOEMOTIONS_SOURCE_TIER,
    MELD_SOURCE_TIER,
    build_local_research_row,
    validate_local_research_row,
    write_json,
)
from tools.validate_transcript_nlp_local_research_rows import main as validate_combined_main


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _write_meld_csv(path: Path, text: str, emotion: str = "neutral", sentiment: str = "neutral") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Sr No.", "Utterance", "Speaker", "Emotion", "Sentiment", "Dialogue_ID", "Utterance_ID"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "Sr No.": "1",
                "Utterance": text,
                "Speaker": "speaker",
                "Emotion": emotion,
                "Sentiment": sentiment,
                "Dialogue_ID": "0",
                "Utterance_ID": "0",
            }
        )


def test_goemotions_builder_writes_valid_local_rows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    cache = tmp_path / "cache"
    _write_jsonl(
        cache / "train.jsonl",
        [
            {"id": "a", "text": "Can you explain what happened?", "labels": [6]},
            {"id": "b", "text": "Thank you, that makes sense.", "labels": [15]},
        ],
    )
    _write_jsonl(cache / "validation.jsonl", [{"id": "c", "text": "Maybe later.", "labels": [6]}])
    _write_jsonl(cache / "test.jsonl", [{"id": "d", "text": "Good morning.", "labels": [27]}])
    manifest = tmp_path / "manifest.json"
    write_json(
        manifest,
        {
            "source_tier": GOEMOTIONS_SOURCE_TIER,
            "license_id": "apache-2.0",
            "license_metadata_confirmed": True,
            "row_commit_allowed": False,
            "aggregate_report_only": True,
            "cache_files": {
                "train": str(cache / "train.jsonl"),
                "validation": str(cache / "validation.jsonl"),
                "test": str(cache / "test.jsonl"),
            },
        },
    )
    out = tmp_path / ".local_artifacts" / "goemotions_local_research_rows.jsonl"
    report = tmp_path / "goemotions_report.md"

    exit_code = build_goemotions_main(["--manifest", str(manifest), "--out", str(out), "--report-out", str(report)])

    assert exit_code == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 4
    assert all(row["source_tier"] == GOEMOTIONS_SOURCE_TIER for row in rows)
    assert rows[0]["messages"][0]["speaker_role"] == "unknown"
    assert "confusion" in rows[0]["source_labels"]
    assert rows[0]["evidence_spans"]
    assert "Can you" in rows[0]["evidence_spans"][0]["span"]
    assert "Can you explain" not in report.read_text(encoding="utf-8")


def test_goemotions_builder_rejects_tracked_row_output(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    _write_jsonl(cache / "train.jsonl", [{"id": "a", "text": "Can you explain?", "labels": [6]}])
    manifest = tmp_path / "manifest.json"
    write_json(
        manifest,
        {
            "source_tier": GOEMOTIONS_SOURCE_TIER,
            "license_id": "apache-2.0",
            "license_metadata_confirmed": True,
            "row_commit_allowed": False,
            "aggregate_report_only": True,
            "cache_files": {"train": str(cache / "train.jsonl")},
        },
    )

    assert build_goemotions_main(["--manifest", str(manifest), "--out", str(tmp_path / "rows.jsonl"), "--report-out", str(tmp_path / "report.md")]) == 1


def test_meld_builder_writes_valid_local_rows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    for split, filename in {"train": "train.csv", "validation": "dev.csv", "test": "test.csv"}.items():
        _write_meld_csv(tmp_path / filename, "I am frustrated and this is not okay." if split == "train" else "Good morning.", "anger" if split == "train" else "neutral", "negative" if split == "train" else "neutral")
    manifest = tmp_path / "meld_manifest.json"
    write_json(
        manifest,
        {
            "source_tier": MELD_SOURCE_TIER,
            "license_id": "gpl-3.0",
            "license_metadata_confirmed": True,
            "audio_video_used": False,
            "commercial_training_allowed": False,
            "production_use_allowed": False,
            "model_quality_claims_allowed": False,
            "row_commit_allowed": False,
            "raw_rows_committed": False,
            "local_only": True,
            "text_only": True,
            "files": {
                "train": str(tmp_path / "train.csv"),
                "validation": str(tmp_path / "dev.csv"),
                "test": str(tmp_path / "test.csv"),
            },
        },
    )
    out = tmp_path / ".local_artifacts" / "meld_local_research_rows.jsonl"
    report = tmp_path / "meld_report.md"

    exit_code = build_meld_main(["--manifest", str(manifest), "--out", str(out), "--report-out", str(report)])

    assert exit_code == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 3
    assert rows[0]["source_tier"] == MELD_SOURCE_TIER
    assert any("conflict" in row["expected_cues"] for row in rows)
    assert any(row["evidence_spans"] for row in rows)
    assert "frustrated" not in report.read_text(encoding="utf-8")


def test_local_research_row_validator_rejects_missing_evidence() -> None:
    row = build_local_research_row(
        source_tier=GOEMOTIONS_SOURCE_TIER,
        row_number=1,
        source_row_id="x",
        split="train",
        text="Can you explain?",
        labels=["confusion"],
        expected_cues=["directness"],
        evidence_spans=[],
    )

    errors = validate_local_research_row(row, 1)

    assert any("require evidence" in error or "missing evidence" in error for error in errors)


def test_local_research_row_validator_rejects_unsafe_flags_and_blocked_labels() -> None:
    row = build_local_research_row(
        source_tier=GOEMOTIONS_SOURCE_TIER,
        row_number=1,
        source_row_id="x",
        split="train",
        text="Can you explain?",
        labels=["confusion"],
        expected_cues=["directness"],
        evidence_spans=[{"cue_type": "directness", "span": "Can you explain", "explanation": "Observable directness."}],
    )

    for field in (
        "commercial_training_allowed",
        "production_use_allowed",
        "model_quality_claims_allowed",
        "contains_raw_private_text",
        "contains_private_or_tester_text",
        "row_commit_allowed",
    ):
        probe = dict(row)
        probe[field] = True
        assert validate_local_research_row(probe, 1)

    probe = dict(row)
    probe["expected_cues"] = ["directness", "gaslighting"]
    assert any("blocked label" in error for error in validate_local_research_row(probe, 1))

    probe = dict(row)
    probe["safe_summary"] = "They are lying and this proves hidden intent."
    assert any("safe_summary" in error for error in validate_local_research_row(probe, 1))

    probe = dict(row)
    probe["forbidden_outputs"] = []
    assert any("forbidden_outputs" in error for error in validate_local_research_row(probe, 1))


def test_local_research_row_validator_rejects_evidence_not_in_text() -> None:
    row = build_local_research_row(
        source_tier=GOEMOTIONS_SOURCE_TIER,
        row_number=1,
        source_row_id="x",
        split="train",
        text="Can you explain?",
        labels=["confusion"],
        expected_cues=["directness"],
        evidence_spans=[{"cue_type": "directness", "span": "missing phrase", "explanation": "Missing."}],
    )

    errors = validate_local_research_row(row, 1)

    assert any("does not appear" in error for error in errors)
