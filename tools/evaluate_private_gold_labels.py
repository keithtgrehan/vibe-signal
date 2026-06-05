#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from tools import validate_private_gold_labels as validator
from tools.private_gold_label_utils import (
    GOLD_LABEL_COLUMNS,
    LOW_SIGNAL_LABELS,
    PREDICTION_COLUMNS,
    REJECT_LABELS,
    PrivateGoldLabelError,
    ensure_restricted_report_path,
    first_present,
    normalize_label_set,
    read_table,
    safe_counter,
    RESTRICTED_ROOT,
)


def default_report_path(*, restricted_root: Path = RESTRICTED_ROOT) -> Path:
    return restricted_root / "reports" / "private_gold_eval_summary.md"


def evaluate_file(
    path: Path,
    *,
    output_path: Path | None = None,
    file_format: str | None = None,
    restricted_root: Path = RESTRICTED_ROOT,
) -> dict[str, Any]:
    fieldnames, rows = read_table(path, file_format=file_format, restricted_root=restricted_root)
    validation = validator.build_summary(fieldnames, rows)
    prediction_column = first_present(fieldnames, PREDICTION_COLUMNS)
    gold_column = first_present(fieldnames, GOLD_LABEL_COLUMNS)
    metrics = compute_metrics(rows, gold_column=gold_column, prediction_column=prediction_column)
    summary = {
        **validation,
        "mode": "prediction_comparison" if prediction_column else "schema/label QA only",
        "metrics_available": prediction_column is not None,
        **metrics,
        "readiness": readiness_gate(validation),
    }
    report_target = output_path or default_report_path(restricted_root=restricted_root)
    write_report(report_target, build_report(summary), restricted_root=restricted_root)
    return {**summary, "report_path": str(report_target)}


def compute_metrics(rows: list[dict[str, str]], *, gold_column: str | None, prediction_column: str | None) -> dict[str, Any]:
    if not gold_column or not prediction_column:
        return {
            "prediction_column": prediction_column,
            "disagreement_count": 0,
            "per_label_metrics": {},
            "confusion_matrix": {},
        }

    per_label_counts: dict[str, Counter[str]] = {}
    confusion: Counter[str] = Counter()
    disagreement_count = 0
    for row in rows:
        gold = normalize_label_set(row.get(gold_column, ""))
        pred = normalize_label_set(row.get(prediction_column, ""))
        if not gold or any(label in REJECT_LABELS for label in gold) or any(label in LOW_SIGNAL_LABELS for label in gold):
            continue
        if gold != pred:
            disagreement_count += 1
        all_labels = gold | pred
        for label in all_labels:
            counts = per_label_counts.setdefault(label, Counter())
            if label in gold and label in pred:
                counts["tp"] += 1
            elif label not in gold and label in pred:
                counts["fp"] += 1
            elif label in gold and label not in pred:
                counts["fn"] += 1
        if not pred:
            for gold_label in sorted(gold):
                confusion[f"{gold_label} -> missing_prediction"] += 1
        else:
            for gold_label in sorted(gold):
                for pred_label in sorted(pred):
                    confusion[f"{gold_label} -> {pred_label}"] += 1

    metrics: dict[str, dict[str, float | int]] = {}
    for label, counts in sorted(per_label_counts.items()):
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        metrics[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": tp + fn,
        }
    return {
        "prediction_column": prediction_column,
        "disagreement_count": disagreement_count,
        "per_label_metrics": metrics,
        "confusion_matrix": safe_counter(confusion),
    }


def readiness_gate(summary: dict[str, Any]) -> dict[str, Any]:
    total_rows = int(summary.get("total_rows", 0))
    if total_rows <= 30:
        status = "schema/evaluator smoke only"
        message = "30 rows = schema/evaluator smoke only; production training remains blocked."
    elif total_rows < 100:
        status = "schema/evaluator smoke only"
        message = "Fewer than 100 rows supports schema QA only; production training remains blocked."
    elif total_rows < 600:
        status = "not training-ready"
        message = "Minimum row count for a broad cue-family baseline has not been met."
    else:
        status = "research review required"
        message = "Row count alone is insufficient; per-cue support, legal/privacy gates, and safety gates are still required."
    return {
        "status": status,
        "message": message,
        "minimum_rows_per_cue_family_before_training": 80,
        "minimum_leaf_cue_rows_before_leaf_model": "separate reviewed positive and hard-negative support required",
        "production_training_blocked": True,
    }


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Private Gold Label Evaluation Summary",
        "",
        "Status: local-only; aggregate metrics only; no raw private text included; no model trained; not for production model claims.",
        "",
        "This report contains no row-level details.",
        "",
        "## Overview",
        "",
        f"- Mode: `{summary['mode']}`",
        f"- Total rows: `{summary['total_rows']}`",
        f"- Usable rows: `{summary['usable_rows']}`",
        f"- Rejected rows: `{summary['rejected_rows']}`",
        f"- Low-signal rows: `{summary['low_signal_rows']}`",
        f"- Missing evidence-span count: `{summary['missing_evidence_span_count']}`",
        f"- Disagreement count: `{summary['disagreement_count']}`",
        f"- Readiness: `{summary['readiness']['status']}`",
        f"- Readiness note: {summary['readiness']['message']}",
        "",
        "## Label Distribution",
        "",
        *_counter_lines(summary["cue_distribution"]),
        "",
        "## Severity Distribution",
        "",
        *_counter_lines(summary["severity_distribution"]),
        "",
        "## Safe Next Step Distribution",
        "",
        *_counter_lines(summary["safe_next_step_distribution"]),
        "",
    ]
    if summary["metrics_available"]:
        lines.extend(["## Per-Label Metrics", ""])
        for label, metric in summary["per_label_metrics"].items():
            lines.append(
                f"- `{label}`: precision `{metric['precision']}`, recall `{metric['recall']}`, "
                f"F1 `{metric['f1']}`, support `{metric['support']}`"
            )
        lines.extend(["", "## Confusion Matrix", ""])
        lines.extend(_counter_lines(summary["confusion_matrix"]))
        lines.append("")
    else:
        lines.extend(["## Prediction Metrics", "", "- Not available; no prediction column was present.", ""])
    return "\n".join(lines)


def _counter_lines(payload: dict[str, int]) -> list[str]:
    if not payload:
        return ["- None"]
    return [f"- `{key}`: `{value}`" for key, value in sorted(payload.items())]


def write_report(path: Path, report: str, *, restricted_root: Path = RESTRICTED_ROOT) -> Path:
    safe_path = ensure_restricted_report_path(path, kind="output", restricted_root=restricted_root)
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text(report, encoding="utf-8")
    return safe_path


def main(argv: list[str] | None = None, *, restricted_root: Path = RESTRICTED_ROOT) -> int:
    parser = argparse.ArgumentParser(description="Evaluate local-only private gold-review labels in aggregate.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--format", choices=("csv", "xlsx"))
    args = parser.parse_args(argv)

    try:
        summary = evaluate_file(
            Path(args.input),
            output_path=Path(args.output) if args.output else None,
            file_format=args.format,
            restricted_root=restricted_root,
        )
    except PrivateGoldLabelError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    printable = {
        "status": summary["status"],
        "mode": summary["mode"],
        "total_rows": summary["total_rows"],
        "usable_rows": summary["usable_rows"],
        "rejected_rows": summary["rejected_rows"],
        "low_signal_rows": summary["low_signal_rows"],
        "disagreement_count": summary["disagreement_count"],
        "readiness": summary["readiness"],
        "report_written": True,
    }
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0 if summary["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
