from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

from tools import evaluate_private_gold_labels as evaluator
from tools import validate_private_gold_labels as validator


ROOT = Path(__file__).resolve().parents[1]
RAW_MESSAGE = "SYNTHETIC RAW MESSAGE MUST NOT LEAK"
RAW_EVIDENCE = "SYNTHETIC EVIDENCE MUST NOT LEAK"
RAW_NOTE = "SYNTHETIC REVIEWER NOTE MUST NOT LEAK"


FIELDNAMES = [
    "example_id",
    "text_window_redacted",
    "evidence_hint",
    "candidate_labels",
    "review_label",
    "severity",
    "safe_next_step",
    "reviewer_notes",
]


def _fake_restricted_root(tmp_path: Path) -> Path:
    return tmp_path / "data" / "restricted" / "private_whatsapp"


def _write_csv(path: Path, rows: list[dict[str, str]], *, fieldnames: list[str] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = fieldnames or FIELDNAMES
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in headers})
    return path


def _valid_row(index: int = 1, *, review_label: str = "direct_ask", candidate_labels: str = "direct_ask") -> dict[str, str]:
    return {
        "example_id": f"synthetic_{index:03d}",
        "text_window_redacted": RAW_MESSAGE,
        "evidence_hint": RAW_EVIDENCE,
        "candidate_labels": candidate_labels,
        "review_label": review_label,
        "severity": "low",
        "safe_next_step": "direct_ask: Answer the ask directly or ask one clarifying question.",
        "reviewer_notes": RAW_NOTE,
    }


def test_validator_rejects_input_outside_restricted_root(tmp_path: Path) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    outside = _write_csv(tmp_path / "outside.csv", [_valid_row()])

    with pytest.raises(ValueError, match="input must be under restricted private root"):
        validator.validate_file(outside, restricted_root=restricted_root)


def test_evaluator_rejects_output_outside_restricted_root(tmp_path: Path) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    input_path = _write_csv(restricted_root / "processed" / "synthetic_review.csv", [_valid_row()])

    with pytest.raises(ValueError, match="output must be under restricted private root"):
        evaluator.evaluate_file(input_path, output_path=tmp_path / "report.md", restricted_root=restricted_root)


def test_evaluator_rejects_output_outside_restricted_reports_root(tmp_path: Path) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    input_path = _write_csv(restricted_root / "processed" / "synthetic_review.csv", [_valid_row()])

    with pytest.raises(ValueError, match="output must be under restricted private reports root"):
        evaluator.evaluate_file(
            input_path,
            output_path=restricted_root / "processed" / "summary.md",
            restricted_root=restricted_root,
        )


def test_valid_synthetic_csv_schema_passes_without_leaking_content(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    input_path = _write_csv(restricted_root / "processed" / "synthetic_review.csv", [_valid_row()])

    exit_code = validator.main(["--input", str(input_path)], restricted_root=restricted_root)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"status": "valid"' in captured.out
    assert '"total_rows": 1' in captured.out
    assert RAW_MESSAGE not in captured.out
    assert RAW_EVIDENCE not in captured.out
    assert RAW_NOTE not in captured.out
    assert RAW_MESSAGE not in captured.err


def test_missing_row_id_and_gold_label_columns_fail(tmp_path: Path) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    no_row_id = _write_csv(
        restricted_root / "processed" / "missing_row_id.csv",
        [{"review_label": "direct_ask"}],
        fieldnames=["review_label"],
    )
    no_gold = _write_csv(
        restricted_root / "processed" / "missing_gold.csv",
        [{"example_id": "synthetic_001"}],
        fieldnames=["example_id"],
    )

    row_id_summary = validator.validate_file(no_row_id, restricted_root=restricted_root)
    gold_summary = validator.validate_file(no_gold, restricted_root=restricted_root)

    assert row_id_summary["status"] == "invalid"
    assert row_id_summary["missing_required_columns"] == ["row_id"]
    assert gold_summary["status"] == "invalid"
    assert gold_summary["missing_required_columns"] == ["gold_label"]


def test_invalid_labels_and_unknown_columns_are_counted_without_values(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    headers = FIELDNAMES + ["unexpected_context"]
    input_path = _write_csv(
        restricted_root / "processed" / "invalid_label.csv",
        [
            {
                **_valid_row(),
                "review_label": "not_allowed_label",
                "unexpected_context": "SYNTHETIC UNKNOWN CELL MUST NOT LEAK",
            }
        ],
        fieldnames=headers,
    )

    exit_code = validator.main(["--input", str(input_path)], restricted_root=restricted_root)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert '"invalid_label_rows": 1' in captured.out
    assert '"unknown_column_count": 1' in captured.out
    assert "not_allowed_label" not in captured.out
    assert "unexpected_context" not in captured.out
    assert "SYNTHETIC UNKNOWN CELL MUST NOT LEAK" not in captured.out
    assert RAW_MESSAGE not in captured.out
    assert RAW_EVIDENCE not in captured.out
    assert RAW_NOTE not in captured.out


def test_evaluator_writes_aggregate_only_report_without_raw_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    input_path = _write_csv(
        restricted_root / "processed" / "synthetic_review.csv",
        [
            _valid_row(1, review_label="direct_ask", candidate_labels="direct_ask"),
            _valid_row(2, review_label="ambiguity", candidate_labels="direct_ask"),
            _valid_row(3, review_label="low_signal", candidate_labels=""),
        ],
    )
    output_path = restricted_root / "reports" / "summary.md"

    exit_code = evaluator.main(["--input", str(input_path), "--output", str(output_path)], restricted_root=restricted_root)

    captured = capsys.readouterr()
    report = output_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert '"mode": "prediction_comparison"' in captured.out
    assert '"disagreement_count": 1' in captured.out
    assert "## Per-Label Metrics" in report
    assert "## Confusion Matrix" in report
    assert "local-only" in report
    assert "no raw private text included" in report
    assert "no model trained" in report
    assert "not for production model claims" in report
    for text in (RAW_MESSAGE, RAW_EVIDENCE, RAW_NOTE):
        assert text not in captured.out
        assert text not in captured.err
        assert text not in report


def test_evaluator_runs_schema_qa_only_without_prediction_columns(tmp_path: Path) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    headers = [field for field in FIELDNAMES if field != "candidate_labels"]
    input_path = _write_csv(
        restricted_root / "processed" / "schema_only.csv",
        [_valid_row(1), _valid_row(2, review_label="low_signal")],
        fieldnames=headers,
    )

    summary = evaluator.evaluate_file(input_path, restricted_root=restricted_root)

    assert summary["mode"] == "schema/label QA only"
    assert summary["metrics_available"] is False
    assert summary["disagreement_count"] == 0


def test_thirty_rows_are_schema_smoke_only_not_training_ready(tmp_path: Path) -> None:
    restricted_root = _fake_restricted_root(tmp_path)
    rows = [_valid_row(index) for index in range(1, 31)]
    input_path = _write_csv(restricted_root / "processed" / "thirty_rows.csv", rows)

    summary = evaluator.evaluate_file(input_path, restricted_root=restricted_root)

    assert summary["readiness"]["status"] == "schema/evaluator smoke only"
    assert summary["readiness"]["production_training_blocked"] is True
    assert "30 rows = schema/evaluator smoke only" in summary["readiness"]["message"]


def test_default_report_path_resolves_under_restricted_reports(tmp_path: Path) -> None:
    restricted_root = _fake_restricted_root(tmp_path)

    report_path = evaluator.default_report_path(restricted_root=restricted_root)

    assert report_path == restricted_root / "reports" / "private_gold_eval_summary.md"


def test_generated_report_path_pattern_is_gitignored_without_creating_report() -> None:
    restricted_rel = Path("data") / "restricted" / "private_whatsapp"
    report_rel = restricted_rel / "reports" / "private_gold_eval_summary.md"

    result = subprocess.run(
        ["git", "check-ignore", "-q", str(report_rel)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert not (ROOT / report_rel).exists()


def test_optional_xlsx_support_uses_existing_openpyxl_only(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    restricted_root = _fake_restricted_root(tmp_path)
    xlsx_path = restricted_root / "processed" / "synthetic_review.xlsx"
    xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(FIELDNAMES)
    row = _valid_row()
    sheet.append([row.get(field, "") for field in FIELDNAMES])
    workbook.save(xlsx_path)

    summary = validator.validate_file(xlsx_path, file_format="xlsx", restricted_root=restricted_root)

    assert summary["status"] == "valid"
    assert summary["total_rows"] == 1


def test_private_metadata_guard_still_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_private_metadata_exposure.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_no_n8n_raw_content_or_private_metadata_path_is_introduced() -> None:
    paths = [
        ROOT / "tools" / "private_gold_label_utils.py",
        ROOT / "tools" / "validate_private_gold_labels.py",
        ROOT / "tools" / "evaluate_private_gold_labels.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists()).lower()

    assert "n8n" not in combined
    assert "raw private chat" not in combined
    assert "private source metadata" not in combined
