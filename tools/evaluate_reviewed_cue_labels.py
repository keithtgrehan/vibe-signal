#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LABELS = REPO_ROOT / "data" / "review" / "seed_reviewed_labels.jsonl"
DEFAULT_RESULTS = REPO_ROOT / "reports" / "engine_eval" / "api_regression_results.jsonl"
DEFAULT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "reviewed_label_evaluation.md"
DEFAULT_METRICS = REPO_ROOT / "reports" / "engine_eval" / "reviewed_label_metrics.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def reviewed_label_status(labels: list[dict[str, Any]]) -> str:
    if not labels:
        return "none"
    if any(row.get("reviewer") != "synthetic_bootstrap" and row.get("not_human_validated") is not True for row in labels):
        return "human-reviewed"
    return "bootstrap"


def result_cue_map(results: list[dict[str, Any]]) -> dict[str, set[str]]:
    return {
        str(row.get("fixture_id", "")): {str(cue) for cue in row.get("observed_cues", [])}
        for row in results
        if row.get("fixture_id")
    }


def compute_metrics(labels: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    status = reviewed_label_status(labels)
    if status == "none":
        return {
            "status": "gated",
            "reviewed_label_status": "none",
            "precision_recall_status": "gated",
            "reason": "no reviewed or bootstrap label rows found",
        }

    predictions = result_cue_map(results)
    cue_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    for label in labels:
        cue = str(label.get("cue_id", ""))
        if not cue:
            continue
        fixture_id = str(label.get("fixture_id", ""))
        actual_present = label.get("cue_present") is True
        predicted_present = cue in predictions.get(fixture_id, set())
        if actual_present and predicted_present:
            cue_counts[cue]["tp"] += 1
        elif not actual_present and predicted_present:
            cue_counts[cue]["fp"] += 1
        elif actual_present and not predicted_present:
            cue_counts[cue]["fn"] += 1
        else:
            cue_counts[cue]["tn"] += 1

    per_cue: dict[str, dict[str, Any]] = {}
    total = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for cue, counts in sorted(cue_counts.items()):
        for key in total:
            total[key] += counts[key]
        precision_denominator = counts["tp"] + counts["fp"]
        recall_denominator = counts["tp"] + counts["fn"]
        per_cue[cue] = {
            **counts,
            "precision": round(counts["tp"] / precision_denominator, 4) if precision_denominator else None,
            "recall": round(counts["tp"] / recall_denominator, 4) if recall_denominator else None,
        }
    precision_denominator = total["tp"] + total["fp"]
    recall_denominator = total["tp"] + total["fn"]
    return {
        "status": "complete",
        "reviewed_label_status": status,
        "precision_recall_status": "human-reviewed" if status == "human-reviewed" else "bootstrap-only",
        "label_count": len(labels),
        "result_count": len(results),
        "micro": {
            **total,
            "precision": round(total["tp"] / precision_denominator, 4) if precision_denominator else None,
            "recall": round(total["tp"] / recall_denominator, 4) if recall_denominator else None,
        },
        "per_cue": per_cue,
        "non_claims": [
            "Bootstrap metrics are not human-reviewed labels.",
            "Metrics are not real-world accuracy, model-quality proof, or production readiness.",
        ],
    }


def build_report(metrics: dict[str, Any]) -> str:
    if metrics["status"] == "gated":
        return "\n".join(
            [
                "# Reviewed Label Evaluation",
                "",
                "Status: `GATED`.",
                "",
                "No reviewed or bootstrap cue-label rows were found. Precision/recall reporting is fail-closed.",
                "",
                "This is not an accuracy claim, model-quality proof, or production-readiness claim.",
                "",
            ]
        )
    micro = metrics["micro"]
    return "\n".join(
        [
            "# Reviewed Label Evaluation",
            "",
            f"Status: `{metrics['precision_recall_status']}`.",
            "",
            "These metrics compare engine/API observed cue IDs against synthetic bootstrap or future human-reviewed cue labels. They are not real-world accuracy or model-quality proof.",
            "",
            f"- Label status: `{metrics['reviewed_label_status']}`",
            f"- Label rows: `{metrics['label_count']}`",
            f"- API result rows: `{metrics['result_count']}`",
            f"- Micro precision: `{micro['precision']}`",
            f"- Micro recall: `{micro['recall']}`",
            f"- TP/FP/FN/TN: `{micro['tp']}/{micro['fp']}/{micro['fn']}/{micro['tn']}`",
            "",
            "Human-reviewed labels are required before any validation or quality claim.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate reviewed cue labels against API regression results with fail-closed gates.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--metrics-out", default=str(DEFAULT_METRICS))
    args = parser.parse_args(argv)

    labels = read_jsonl(Path(args.labels))
    results = read_jsonl(Path(args.results))
    metrics = compute_metrics(labels, results)
    write_json(Path(args.metrics_out), metrics)
    Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_out).write_text(build_report(metrics), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 1 if metrics["status"] == "gated" else 0


if __name__ == "__main__":
    raise SystemExit(main())
