from __future__ import annotations

import json
from pathlib import Path

from tools import analyze_cue_confusion_groups as confusion


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_cue_confusion_groups_reports_substitutions_and_cofires(tmp_path: Path) -> None:
    results = tmp_path / "results.jsonl"
    report = tmp_path / "confusion.md"
    summary = tmp_path / "confusion.json"
    _write_jsonl(
        results,
        [
            {
                "fixture_id": "f1",
                "split": "hard_negative",
                "category": "urgency_without_pressure",
                "expected_cues": ["urgency"],
                "observed_cues": ["urgency", "pressure"],
                "unexpected_cues": ["pressure"],
                "missing_expected_cues": [],
            },
            {
                "fixture_id": "f2",
                "split": "dev",
                "category": "answer_evasion_pattern",
                "expected_cues": ["answer_evasion_pattern"],
                "observed_cues": ["topic_shift"],
                "unexpected_cues": ["topic_shift"],
                "missing_expected_cues": ["answer_evasion_pattern"],
            },
        ],
    )

    exit_code = confusion.main(
        [
            "--results",
            str(results),
            "--report-out",
            str(report),
            "--summary-out",
            str(summary),
        ]
    )

    assert exit_code == 0
    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["result_count"] == 2
    assert payload["groups"]["urgency_vs_pressure"]["unexpected_within_group"]["pressure"] == 1
    assert payload["groups"]["topic_shift_vs_evasion"]["missing_within_group"]["answer_evasion_pattern"] == 1
    assert payload["groups"]["urgency_vs_pressure"]["cofires"]["pressure+urgency"] == 1
    assert "suggested precedence rule" in report.read_text(encoding="utf-8").lower()
