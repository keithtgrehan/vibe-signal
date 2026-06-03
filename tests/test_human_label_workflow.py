from __future__ import annotations

import json
from pathlib import Path

from tools import evaluate_human_reviewed_labels as human_eval
from tools import prepare_human_label_review as prepare
from tools import validate_human_labels as validator


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_prepare_human_label_review_writes_blank_rows(tmp_path: Path) -> None:
    packet = tmp_path / "packet.jsonl"
    csv_out = tmp_path / "labels.csv"
    jsonl_out = tmp_path / "labels.jsonl"
    _write_jsonl(
        packet,
        [
            {
                "review_id": "r1",
                "conversation_id": "c1",
                "split": "dev",
                "scenario": "clear_direct_ask",
                "candidate_cues": ["directness", "pressure"],
            }
        ],
    )

    exit_code = prepare.main(["--packet", str(packet), "--csv-out", str(csv_out), "--jsonl-out", str(jsonl_out)])

    assert exit_code == 0
    rows = [json.loads(line) for line in jsonl_out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    assert rows[0]["reviewer"] == ""
    assert "observable wording" in rows[0]["notes"].lower()
    assert csv_out.exists()


def test_validate_human_labels_fails_closed_without_human_rows(tmp_path: Path) -> None:
    labels = tmp_path / "labels.jsonl"
    _write_jsonl(labels, [])

    summary = validator.validate_rows([], require_human=True)

    assert summary["status"] == "fail"
    assert summary["errors"][0]["reason"] == "No human-reviewed labels available."


def test_validate_human_labels_rejects_blocked_inference_categories() -> None:
    summary = validator.validate_rows(
        [
            {
                "cue_id": "hidden_intent",
                "reviewer": "human_a",
                "not_human_validated": False,
                "cue_present": True,
                "evidence_supports_cue": True,
                "unsafe_wording_flag": False,
                "reviewer_confidence": "medium",
            }
        ],
        require_human=True,
    )

    assert summary["status"] == "fail"
    assert any(error["reason"] == "blocked_inference_category" for error in summary["errors"])


def test_human_reviewed_evaluator_fails_closed_without_human_labels(tmp_path: Path) -> None:
    labels = tmp_path / "bootstrap_labels.jsonl"
    results = tmp_path / "results.jsonl"
    metrics = tmp_path / "human_metrics.json"
    report = tmp_path / "human_report.md"
    _write_jsonl(
        labels,
        [
            {
                "fixture_id": "f1",
                "reviewer": "synthetic_bootstrap",
                "not_human_validated": True,
                "cue_id": "directness",
                "cue_present": True,
            }
        ],
    )
    _write_jsonl(results, [{"fixture_id": "f1", "observed_cues": ["directness"]}])

    exit_code = human_eval.main(["--labels", str(labels), "--results", str(results), "--metrics-out", str(metrics), "--report-out", str(report)])

    assert exit_code == 1
    payload = json.loads(metrics.read_text(encoding="utf-8"))
    assert payload["precision_recall_status"] == "gated"
    assert "No human-reviewed labels available" in report.read_text(encoding="utf-8")
