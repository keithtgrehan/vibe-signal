from __future__ import annotations

import json
from pathlib import Path

from tools import analyze_cue_false_positives as analysis


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_false_positive_analysis_reports_missing_and_unexpected_cues(tmp_path: Path) -> None:
    results = tmp_path / "api_regression_results.jsonl"
    report = tmp_path / "false_positive_analysis.md"
    backlog = tmp_path / "cue_improvement_backlog.md"
    _write_jsonl(
        results,
        [
            {
                "fixture_id": "f1",
                "missing_expected_cues": ["answer_evasion_pattern"],
                "unexpected_cues": ["directness"],
                "low_signal_correct": True,
                "evidence_complete": True,
                "unsafe_output_hits": [],
            },
            {
                "fixture_id": "f2",
                "missing_expected_cues": ["answer_evasion_pattern"],
                "unexpected_cues": [],
                "low_signal_correct": False,
                "evidence_complete": False,
                "unsafe_output_hits": [],
            },
        ],
    )

    exit_code = analysis.main(["--results", str(results), "--report-out", str(report), "--backlog-out", str(backlog)])

    assert exit_code == 0
    report_text = report.read_text(encoding="utf-8")
    backlog_text = backlog.read_text(encoding="utf-8")
    assert "`answer_evasion_pattern`: `2`" in report_text
    assert "`directness`: `1`" in report_text
    assert "Low-signal failures: `1`" in report_text
    assert "Candidate False Negatives" in backlog_text
    assert "Candidate False Positives" in backlog_text
