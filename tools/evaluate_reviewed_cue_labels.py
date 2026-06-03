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
SPLIT_NAMES = ("dev", "hard_negative", "heldout", "red_team")
DEFAULT_SYNTHETIC_ROOT = REPO_ROOT / "data" / "synthetic" / "whatsapp"
DEFAULT_SPLIT_RESULTS_ROOT = REPO_ROOT / "reports" / "engine_eval" / "splits"
DEFAULT_BY_SPLIT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "bootstrap_metrics_by_split.md"
DEFAULT_BY_CUE = REPO_ROOT / "reports" / "engine_eval" / "bootstrap_metrics_by_cue.json"
DEFAULT_BY_SCENARIO = REPO_ROOT / "reports" / "engine_eval" / "bootstrap_metrics_by_scenario.json"


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


def _safe_divide(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def _f1(precision: float | None, recall: float | None) -> float | None:
    if precision is None or recall is None or precision + recall == 0:
        return None
    return round((2 * precision * recall) / (precision + recall), 4)


def _metric_from_counts(counts: dict[str, int]) -> dict[str, Any]:
    precision = _safe_divide(counts["tp"], counts["tp"] + counts["fp"])
    recall = _safe_divide(counts["tp"], counts["tp"] + counts["fn"])
    return {
        **counts,
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
        "false_positive_count": counts["fp"],
        "false_negative_count": counts["fn"],
    }


def _macro(per_item: dict[str, dict[str, Any]]) -> dict[str, float | None]:
    values = list(per_item.values())
    result: dict[str, float | None] = {}
    for metric in ("precision", "recall", "f1"):
        present = [float(item[metric]) for item in values if item.get(metric) is not None]
        result[metric] = round(sum(present) / len(present), 4) if present else None
    return result


def _empty_counts() -> dict[str, int]:
    return {"tp": 0, "fp": 0, "fn": 0, "tn": 0}


def _read_split_conversations(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in SPLIT_NAMES:
        path = root / split / "conversations.jsonl"
        rows.extend(read_jsonl(path))
    return rows


def _read_split_results(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in SPLIT_NAMES:
        path = root / split / "synthetic_regression_results.jsonl"
        rows.extend(read_jsonl(path))
    return rows


def _cue_universe(conversations: list[dict[str, Any]], results: list[dict[str, Any]]) -> list[str]:
    cues: set[str] = set()
    for row in conversations:
        cues.update(str(cue) for cue in row.get("expected_cues", []))
        cues.update(str(cue) for cue in row.get("allowed_extra_cues", []))
    for row in results:
        cues.update(str(cue) for cue in row.get("observed_cues", []))
    return sorted(cue for cue in cues if cue)


def bootstrap_labels_from_conversations(conversations: list[dict[str, Any]], cue_universe: list[str]) -> list[dict[str, Any]]:
    labels: list[dict[str, Any]] = []
    for conversation in conversations:
        expected = {str(cue) for cue in conversation.get("expected_cues", [])}
        evidence_text = " | ".join(str(message.get("text", "")) for message in conversation.get("messages", []))
        for cue in cue_universe:
            present = cue in expected
            labels.append(
                {
                    "label_id": f"{conversation['fixture_id']}_{cue}",
                    "fixture_id": conversation["fixture_id"],
                    "split": conversation.get("split", "legacy"),
                    "scenario": conversation.get("scenario", conversation.get("category", "")),
                    "source_type": "synthetic_fixture",
                    "reviewer": "synthetic_bootstrap",
                    "not_human_validated": True,
                    "cue_id": cue,
                    "cue_present": present,
                    "evidence_supports_cue": present,
                    "evidence_text": evidence_text if present else "",
                    "unsafe_wording_flag": False,
                    "low_signal_flag": conversation.get("expected_result_type") == "low_signal",
                }
            )
    return labels


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
    result_meta = {
        str(row.get("fixture_id", "")): {
            "split": str(row.get("split", "")),
            "scenario": str(row.get("scenario", row.get("category", ""))),
        }
        for row in results
    }
    cue_counts: dict[str, dict[str, int]] = defaultdict(_empty_counts)
    split_counts: dict[str, dict[str, int]] = defaultdict(_empty_counts)
    scenario_counts: dict[str, dict[str, int]] = defaultdict(_empty_counts)
    for label in labels:
        cue = str(label.get("cue_id", ""))
        if not cue:
            continue
        fixture_id = str(label.get("fixture_id", ""))
        split = str(label.get("split") or result_meta.get(fixture_id, {}).get("split") or "unspecified")
        scenario = str(label.get("scenario") or result_meta.get(fixture_id, {}).get("scenario") or "unspecified")
        actual_present = label.get("cue_present") is True
        predicted_present = cue in predictions.get(fixture_id, set())
        bucket_key: str
        if actual_present and predicted_present:
            bucket_key = "tp"
        elif not actual_present and predicted_present:
            bucket_key = "fp"
        elif actual_present and not predicted_present:
            bucket_key = "fn"
        else:
            bucket_key = "tn"
        cue_counts[cue][bucket_key] += 1
        split_counts[split][bucket_key] += 1
        scenario_counts[scenario][bucket_key] += 1

    per_cue: dict[str, dict[str, Any]] = {}
    total = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for cue, counts in sorted(cue_counts.items()):
        for key in total:
            total[key] += counts[key]
        per_cue[cue] = _metric_from_counts(counts)
    by_split = {split: _metric_from_counts(counts) for split, counts in sorted(split_counts.items())}
    by_scenario = {scenario: _metric_from_counts(counts) for scenario, counts in sorted(scenario_counts.items())}
    return {
        "status": "complete",
        "reviewed_label_status": status,
        "precision_recall_status": "human-reviewed" if status == "human-reviewed" else "bootstrap-only",
        "label_count": len(labels),
        "result_count": len(results),
        "micro": _metric_from_counts(total),
        "macro": _macro(per_cue),
        "per_cue": per_cue,
        "by_split": by_split,
        "by_scenario": by_scenario,
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
            f"- Micro F1: `{micro.get('f1')}`",
            f"- Macro precision: `{metrics.get('macro', {}).get('precision')}`",
            f"- Macro recall: `{metrics.get('macro', {}).get('recall')}`",
            f"- Macro F1: `{metrics.get('macro', {}).get('f1')}`",
            f"- TP/FP/FN/TN: `{micro['tp']}/{micro['fp']}/{micro['fn']}/{micro['tn']}`",
            "",
            "## Split Metrics",
            "",
            *[
                f"- `{split}`: precision `{row['precision']}`, recall `{row['recall']}`, F1 `{row['f1']}`, FP `{row['fp']}`, FN `{row['fn']}`"
                for split, row in sorted(metrics.get("by_split", {}).items())
            ],
            "",
            "Human-reviewed labels are required before any validation or quality claim.",
            "",
        ]
    )


def build_split_report(metrics: dict[str, Any]) -> str:
    split_lines = [
        f"| {split} | {row['precision']} | {row['recall']} | {row['f1']} | {row['fp']} | {row['fn']} |"
        for split, row in sorted(metrics.get("by_split", {}).items())
    ]
    cue_lines = [
        f"| {cue} | {row['precision']} | {row['recall']} | {row['f1']} | {row['fp']} | {row['fn']} |"
        for cue, row in sorted(metrics.get("per_cue", {}).items())
    ]
    micro = metrics.get("micro", {})
    macro = metrics.get("macro", {})
    return "\n".join(
        [
            "# Bootstrap Metrics By Split",
            "",
            "These are bootstrap-only synthetic metrics. They are not human-reviewed accuracy, model-quality, or production-readiness claims.",
            "",
            f"- Micro precision: `{micro.get('precision')}`",
            f"- Micro recall: `{micro.get('recall')}`",
            f"- Micro F1: `{micro.get('f1')}`",
            f"- Macro precision: `{macro.get('precision')}`",
            f"- Macro recall: `{macro.get('recall')}`",
            f"- Macro F1: `{macro.get('f1')}`",
            "",
            "## Splits",
            "",
            "| Split | Precision | Recall | F1 | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
            *split_lines,
            "",
            "## Per Cue",
            "",
            "| Cue | Precision | Recall | F1 | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
            *cue_lines,
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate reviewed cue labels against API regression results with fail-closed gates.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--metrics-out", default=str(DEFAULT_METRICS))
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--all-splits", action="store_true")
    parser.add_argument("--synthetic-root", default=str(DEFAULT_SYNTHETIC_ROOT))
    parser.add_argument("--split-results-root", default=str(DEFAULT_SPLIT_RESULTS_ROOT))
    parser.add_argument("--split-report-out", default=str(DEFAULT_BY_SPLIT_REPORT))
    parser.add_argument("--per-cue-out", default=str(DEFAULT_BY_CUE))
    parser.add_argument("--per-scenario-out", default=str(DEFAULT_BY_SCENARIO))
    args = parser.parse_args(argv)

    if args.bootstrap and args.all_splits:
        conversations = _read_split_conversations(Path(args.synthetic_root))
        results = _read_split_results(Path(args.split_results_root))
        labels = bootstrap_labels_from_conversations(conversations, _cue_universe(conversations, results))
    else:
        labels = read_jsonl(Path(args.labels))
        results = read_jsonl(Path(args.results))
    metrics = compute_metrics(labels, results)
    write_json(Path(args.metrics_out), metrics)
    if metrics.get("status") == "complete":
        write_json(Path(args.per_cue_out), metrics.get("per_cue", {}))
        write_json(Path(args.per_scenario_out), metrics.get("by_scenario", {}))
        split_report = Path(args.split_report_out)
        split_report.parent.mkdir(parents=True, exist_ok=True)
        split_report.write_text(build_split_report(metrics), encoding="utf-8")
    Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_out).write_text(build_report(metrics), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 1 if metrics["status"] == "gated" else 0


if __name__ == "__main__":
    raise SystemExit(main())
