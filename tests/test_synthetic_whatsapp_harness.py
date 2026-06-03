from __future__ import annotations

import json
from pathlib import Path

from tools.generate_synthetic_whatsapp_fixtures import build_conversations, main, select_for_api_regression


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


def test_synthetic_whatsapp_generator_no_api_writes_fixtures_only(tmp_path: Path) -> None:
    out_dir = tmp_path / "data"
    report_dir = tmp_path / "reports"

    exit_code = main(["--messages", "22", "--no-api", "--out-dir", str(out_dir), "--engine-report-dir", str(report_dir)])

    assert exit_code == 0
    conversations = _read_jsonl(out_dir / "conversations.jsonl")
    assert sum(row["message_count"] for row in conversations) == 22
    assert not (out_dir / "evaluations.jsonl").exists()
    assert not (report_dir / "api_regression_report.md").exists()


def test_synthetic_whatsapp_api_limit_selection_is_deterministic_and_balanced() -> None:
    rows = build_conversations(1000)

    first = select_for_api_regression(rows, limit=100, seed=123)
    second = select_for_api_regression(rows, limit=100, seed=123)

    assert [row["fixture_id"] for row in first] == [row["fixture_id"] for row in second]
    assert len(first) == 100
    counts = {category: sum(1 for row in first if row["category"] == category) for category in {row["category"] for row in first}}
    assert set(counts.values()) == {10}
