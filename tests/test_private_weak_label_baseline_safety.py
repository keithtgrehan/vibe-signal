from __future__ import annotations

import csv
import shutil
from pathlib import Path

from tools import train_private_weak_label_baseline as trainer


ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_TEST_DIR = ROOT / "data" / "restricted" / "private_whatsapp" / "pytest_weak_model"


def _cleanup() -> None:
    shutil.rmtree(RESTRICTED_TEST_DIR, ignore_errors=True)


def _write_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "example_id": "r1",
            "split": "test",
            "speaker_roles": "self|other",
            "text_window_redacted": "self: Can you confirm the plan?\nother: Maybe later.",
            "candidate_labels": "direct_ask;unclear_timing",
            "evidence_hint": "question or direct request marker;unclear timing marker",
            "review_label": "",
            "severity": "",
            "safe_next_step": "",
            "reviewer_notes": "",
        },
        {
            "example_id": "r2",
            "split": "test",
            "speaker_roles": "self|other",
            "text_window_redacted": "self: No pressure if not.\nother: All good.",
            "candidate_labels": "reassurance",
            "evidence_hint": "reassurance wording marker",
            "review_label": "",
            "severity": "",
            "safe_next_step": "",
            "reviewer_notes": "",
        },
        {
            "example_id": "r3",
            "split": "test",
            "speaker_roles": "self|other",
            "text_window_redacted": "self: You have to answer right now!!\nother: I need a minute.",
            "candidate_labels": "pressure_urgency;escalation_risk",
            "evidence_hint": "urgency or pressure wording marker;conflict intensity marker",
            "review_label": "",
            "severity": "",
            "safe_next_step": "",
            "reviewer_notes": "",
        },
        {
            "example_id": "r4",
            "split": "test",
            "speaker_roles": "self|other",
            "text_window_redacted": "self: My bad, let me clarify.\nother: Thanks.",
            "candidate_labels": "repair_attempt",
            "evidence_hint": "repair wording marker",
            "review_label": "",
            "severity": "",
            "safe_next_step": "",
            "reviewer_notes": "",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_refuses_input_outside_restricted_folder(tmp_path: Path) -> None:
    csv_path = tmp_path / "labels.csv"
    _write_csv(csv_path)

    exit_code = trainer.main(["--input", str(csv_path), "--output-dir", str(RESTRICTED_TEST_DIR)])

    assert exit_code == 2


def test_tiny_synthetic_csv_does_not_print_text_and_writes_restricted_artifacts(capsys) -> None:
    _cleanup()
    try:
        csv_path = RESTRICTED_TEST_DIR / "private_label_review.csv"
        report_path = ROOT / "reports" / "engine_eval" / "pytest_private_weak_label_model_experiment.md"
        _write_csv(csv_path)

        exit_code = trainer.main(["--input", str(csv_path), "--output-dir", str(RESTRICTED_TEST_DIR / "models"), "--report-out", str(report_path)])
        output = capsys.readouterr()

        assert exit_code == 0
        assert "Maybe later" not in output.out
        assert "Maybe later" not in output.err
        assert (RESTRICTED_TEST_DIR / "models" / "weak_label_baseline_summary.json").exists()
        assert "Weak-label local experiment only" in report_path.read_text(encoding="utf-8")
    finally:
        report_path = ROOT / "reports" / "engine_eval" / "pytest_private_weak_label_model_experiment.md"
        if report_path.exists():
            report_path.unlink()
        _cleanup()
