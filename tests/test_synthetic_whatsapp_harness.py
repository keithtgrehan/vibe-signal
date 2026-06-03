from __future__ import annotations

import json
from pathlib import Path

from tools.generate_synthetic_whatsapp_fixtures import build_conversations, main


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_build_conversations_uses_synthetic_metadata_only() -> None:
    rows = build_conversations(22)

    assert sum(row["message_count"] for row in rows) == 22
    assert {row["category"] for row in rows} >= {"happy", "cheating_ambiguous", "low_signal"}
    cheating_rows = [row for row in rows if row["category"] == "cheating_ambiguous"]
    assert cheating_rows
    assert cheating_rows[0]["category_scope"] == "private synthetic evaluation metadata only"
    assert "cheating detection" in cheating_rows[0]["notes"]
    assert all(row["synthetic"] is True and row["not_copied_from_real_chat"] is True for row in rows)


def test_synthetic_whatsapp_generator_writes_reports(tmp_path: Path) -> None:
    out_dir = tmp_path / "data"
    report_dir = tmp_path / "reports"

    exit_code = main(["--messages", "22", "--no-api", "--out-dir", str(out_dir), "--report-dir", str(report_dir)])

    assert exit_code == 0
    conversations = _read_jsonl(out_dir / "conversations.jsonl")
    evaluations = _read_jsonl(out_dir / "evaluations.jsonl")
    assert sum(row["message_count"] for row in conversations) == 22
    assert len(evaluations) == len(conversations)
    assert all(row["source_type"] == "synthetic_fixture" for row in evaluations)
    assert "not real-world accuracy" in (report_dir / "fixture_regression_report.md").read_text(encoding="utf-8")
    assert "Unsafe-output block rate" in (report_dir / "unsafe_output_regression_report.md").read_text(encoding="utf-8")
