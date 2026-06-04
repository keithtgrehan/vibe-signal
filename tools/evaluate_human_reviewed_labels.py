#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools import evaluate_reviewed_cue_labels as evaluator
except ImportError:  # pragma: no cover
    import evaluate_reviewed_cue_labels as evaluator


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LABELS = REPO_ROOT / "data" / "review" / "human_reviewed_labels.jsonl"
DEFAULT_RESULTS = REPO_ROOT / "reports" / "engine_eval" / "api_regression_results.jsonl"
DEFAULT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "human_reviewed_label_evaluation.md"
DEFAULT_METRICS = REPO_ROOT / "reports" / "engine_eval" / "human_reviewed_label_metrics.json"


def human_rows(labels: list[dict]) -> list[dict]:
    return [
        row
        for row in labels
        if row.get("reviewer") not in {"", None, "synthetic_bootstrap"} and row.get("not_human_validated") is not True
    ]


def build_gated_report() -> str:
    return "\n".join(
        [
            "# Human-Reviewed Label Evaluation",
            "",
            "Status: `GATED`.",
            "",
            "No human-reviewed labels available.",
            "",
            "Bootstrap labels and fixture expectations are not human-reviewed validation. Precision/recall reporting remains gated until observable-cue labels are completed by a human reviewer.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate only human-reviewed cue labels; fail closed when none exist.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--metrics-out", default=str(DEFAULT_METRICS))
    args = parser.parse_args(argv)

    labels = evaluator.read_jsonl(Path(args.labels))
    reviewed = human_rows(labels)
    report_path = Path(args.report_out)
    metrics_path = Path(args.metrics_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    if not reviewed:
        payload = {
            "status": "gated",
            "reviewed_label_status": "none",
            "precision_recall_status": "gated",
            "reason": "No human-reviewed labels available.",
        }
        metrics_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report_path.write_text(build_gated_report(), encoding="utf-8")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1

    results = evaluator.read_jsonl(Path(args.results))
    metrics = evaluator.compute_metrics(reviewed, results)
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(evaluator.build_report(metrics), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0 if metrics.get("status") == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
