from __future__ import annotations

import json
from pathlib import Path

from tools import evaluate_reviewed_cue_labels as evaluator


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_reviewed_label_evaluator_fails_closed_without_labels(tmp_path: Path) -> None:
    report = tmp_path / "reviewed_label_evaluation.md"
    metrics = tmp_path / "metrics.json"

    exit_code = evaluator.main(
        [
            "--labels",
            str(tmp_path / "missing.jsonl"),
            "--results",
            str(tmp_path / "missing_results.jsonl"),
            "--report-out",
            str(report),
            "--metrics-out",
            str(metrics),
        ]
    )

    assert exit_code == 1
    payload = json.loads(metrics.read_text(encoding="utf-8"))
    assert payload["precision_recall_status"] == "gated"
    assert "GATED" in report.read_text(encoding="utf-8")


def test_reviewed_label_evaluator_reports_bootstrap_only_metrics(tmp_path: Path) -> None:
    labels = tmp_path / "labels.jsonl"
    results = tmp_path / "results.jsonl"
    report = tmp_path / "reviewed_label_evaluation.md"
    metrics = tmp_path / "metrics.json"
    _write_jsonl(
        labels,
        [
            {
                "label_id": "l1",
                "fixture_id": "f1",
                "source_type": "synthetic_fixture",
                "reviewer": "synthetic_bootstrap",
                "not_human_validated": True,
                "cue_id": "directness",
                "cue_present": True,
                "evidence_supports_cue": True,
                "evidence_text": "Can you",
                "unsafe_wording_flag": False,
                "low_signal_flag": False,
                "blocked_inference_guard": {
                    "no_hidden_intent": True,
                    "no_cheating": True,
                    "no_attraction": True,
                    "no_diagnosis": True,
                    "no_true_emotion": True,
                    "no_attachment_style_or_neurotype": True,
                },
            }
        ],
    )
    _write_jsonl(results, [{"fixture_id": "f1", "observed_cues": ["directness"]}])

    exit_code = evaluator.main(["--labels", str(labels), "--results", str(results), "--report-out", str(report), "--metrics-out", str(metrics)])

    assert exit_code == 0
    payload = json.loads(metrics.read_text(encoding="utf-8"))
    assert payload["precision_recall_status"] == "bootstrap-only"
    assert payload["micro"]["precision"] == 1.0
    assert payload["micro"]["recall"] == 1.0


def test_reviewed_label_evaluator_reports_macro_and_split_metrics(tmp_path: Path) -> None:
    labels = tmp_path / "labels.jsonl"
    results = tmp_path / "results.jsonl"
    metrics = tmp_path / "metrics.json"
    report = tmp_path / "metrics.md"
    _write_jsonl(
        labels,
        [
            {
                "label_id": "dev_direct",
                "fixture_id": "f1",
                "split": "dev",
                "scenario": "clear_direct_ask",
                "reviewer": "synthetic_bootstrap",
                "not_human_validated": True,
                "cue_id": "directness",
                "cue_present": True,
            },
            {
                "label_id": "dev_pressure_negative",
                "fixture_id": "f1",
                "split": "dev",
                "scenario": "clear_direct_ask",
                "reviewer": "synthetic_bootstrap",
                "not_human_validated": True,
                "cue_id": "pressure",
                "cue_present": False,
            },
            {
                "label_id": "hard_negative_pressure",
                "fixture_id": "f2",
                "split": "hard_negative",
                "scenario": "urgency_without_pressure",
                "reviewer": "synthetic_bootstrap",
                "not_human_validated": True,
                "cue_id": "pressure",
                "cue_present": False,
            },
        ],
    )
    _write_jsonl(
        results,
        [
            {"fixture_id": "f1", "split": "dev", "scenario": "clear_direct_ask", "observed_cues": ["directness"]},
            {"fixture_id": "f2", "split": "hard_negative", "scenario": "urgency_without_pressure", "observed_cues": ["pressure"]},
        ],
    )

    exit_code = evaluator.main(["--labels", str(labels), "--results", str(results), "--metrics-out", str(metrics), "--report-out", str(report)])

    assert exit_code == 0
    payload = json.loads(metrics.read_text(encoding="utf-8"))
    assert payload["micro"]["precision"] == 0.5
    assert payload["micro"]["recall"] == 1.0
    assert payload["micro"]["f1"] == 0.6667
    assert payload["macro"]["precision"] is not None
    assert set(payload["by_split"]) == {"dev", "hard_negative"}
    assert payload["by_split"]["hard_negative"]["false_positive_count"] == 1
    assert "clear_direct_ask" in payload["by_scenario"]


def test_macro_f1_is_average_of_per_cue_f1_not_harmonic_of_macro_precision_recall() -> None:
    labels = [
        {
            "fixture_id": "f1",
            "reviewer": "synthetic_bootstrap",
            "not_human_validated": True,
            "cue_id": "cue_a",
            "cue_present": True,
        },
        {
            "fixture_id": "f2",
            "reviewer": "synthetic_bootstrap",
            "not_human_validated": True,
            "cue_id": "cue_a",
            "cue_present": True,
        },
        {
            "fixture_id": "f1",
            "reviewer": "synthetic_bootstrap",
            "not_human_validated": True,
            "cue_id": "cue_b",
            "cue_present": False,
        },
        {
            "fixture_id": "f2",
            "reviewer": "synthetic_bootstrap",
            "not_human_validated": True,
            "cue_id": "cue_b",
            "cue_present": False,
        },
    ]
    results = [
        {"fixture_id": "f1", "observed_cues": ["cue_a", "cue_b"]},
        {"fixture_id": "f2", "observed_cues": []},
    ]

    metrics = evaluator.compute_metrics(labels, results)

    assert metrics["per_cue"]["cue_a"]["f1"] == 0.6667
    assert metrics["per_cue"]["cue_b"]["f1"] is None
    assert metrics["macro"]["precision"] == 0.5
    assert metrics["macro"]["recall"] == 0.5
    assert metrics["macro"]["f1"] == 0.6667
