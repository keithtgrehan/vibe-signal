#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
DEFAULT_INPUT = RESTRICTED_ROOT / "processed" / "private_label_review_100.csv"
DEFAULT_OUTPUT_DIR = RESTRICTED_ROOT / "models"
DEFAULT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "private_weak_label_model_experiment.md"
WARNING = "Weak-label local experiment only. Not human-reviewed. Not production. Not a model-quality claim."


def ensure_restricted_path(path: Path, *, kind: str = "path") -> Path:
    resolved = path.resolve()
    restricted = RESTRICTED_ROOT.resolve()
    if resolved != restricted and restricted not in resolved.parents:
        raise ValueError(f"{kind} must be under {RESTRICTED_ROOT.relative_to(REPO_ROOT)}")
    return resolved


def split_labels(value: str) -> list[str]:
    normalized = value.replace("|", ";").replace(",", ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def read_rows(path: Path) -> list[dict[str, str]]:
    safe_path = ensure_restricted_path(path, kind="input CSV")
    if not safe_path.exists():
        raise FileNotFoundError(f"input CSV not found: {path}")
    with safe_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def choose_targets(row: dict[str, str]) -> list[str]:
    reviewed = split_labels(row.get("review_label", ""))
    return reviewed or split_labels(row.get("candidate_labels", ""))


def label_summary(rows: list[dict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(choose_targets(row))
    return counts


def _sklearn_modules() -> dict[str, Any] | None:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import classification_report
        from sklearn.model_selection import train_test_split
        from sklearn.multiclass import OneVsRestClassifier
        from sklearn.preprocessing import MultiLabelBinarizer
    except ImportError:
        return None
    return {
        "TfidfVectorizer": TfidfVectorizer,
        "LogisticRegression": LogisticRegression,
        "classification_report": classification_report,
        "train_test_split": train_test_split,
        "OneVsRestClassifier": OneVsRestClassifier,
        "MultiLabelBinarizer": MultiLabelBinarizer,
    }


def train(rows: list[dict[str, str]], output_dir: Path) -> dict[str, Any]:
    safe_output_dir = ensure_restricted_path(output_dir, kind="output directory")
    safe_output_dir.mkdir(parents=True, exist_ok=True)
    usable = [(row.get("text_window_redacted", ""), choose_targets(row)) for row in rows if choose_targets(row)]
    counts = label_summary(rows)
    summary: dict[str, Any] = {
        "status": "skipped",
        "warning": WARNING,
        "row_count": len(rows),
        "usable_rows": len(usable),
        "label_counts": dict(sorted(counts.items())),
        "artifact_dir": str(safe_output_dir.relative_to(REPO_ROOT)),
    }
    modules = _sklearn_modules()
    if modules is None:
        summary["reason"] = "sklearn unavailable"
        write_restricted_summary(safe_output_dir, summary)
        return summary
    if len(usable) < 4 or len(counts) < 2:
        summary["reason"] = "not enough weak-label rows"
        write_restricted_summary(safe_output_dir, summary)
        return summary

    texts = [text for text, _labels in usable]
    labels = [labels for _text, labels in usable]
    mlb = modules["MultiLabelBinarizer"]()
    y = mlb.fit_transform(labels)
    stratify = None
    x_train, x_test, y_train, y_test = modules["train_test_split"](texts, y, test_size=0.25, random_state=42, stratify=stratify)
    vectorizer = modules["TfidfVectorizer"](ngram_range=(1, 2), min_df=1, max_features=2000)
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)
    classifier = modules["OneVsRestClassifier"](modules["LogisticRegression"](max_iter=500, class_weight="balanced"))
    classifier.fit(x_train_vec, y_train)
    predicted = classifier.predict(x_test_vec)
    metrics = modules["classification_report"](y_test, predicted, target_names=list(mlb.classes_), output_dict=True, zero_division=0)
    with (safe_output_dir / "weak_label_baseline.pkl").open("wb") as handle:
        pickle.dump({"vectorizer": vectorizer, "classifier": classifier, "labels": list(mlb.classes_)}, handle)
    summary.update(
        {
            "status": "complete",
            "train_rows": len(x_train),
            "test_rows": len(x_test),
            "labels": list(mlb.classes_),
            "metrics": metrics,
            "model_artifact": str((safe_output_dir / "weak_label_baseline.pkl").relative_to(REPO_ROOT)),
        }
    )
    write_restricted_summary(safe_output_dir, summary)
    return summary


def write_restricted_summary(output_dir: Path, summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "weak_label_baseline_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(summary: dict[str, Any]) -> str:
    label_lines = [f"- `{label}`: `{count}`" for label, count in summary.get("label_counts", {}).items()] or ["- None"]
    metric_lines: list[str] = []
    metrics = summary.get("metrics", {})
    if isinstance(metrics, dict):
        for label, row in sorted(metrics.items()):
            if not isinstance(row, dict) or label in {"micro avg", "macro avg", "weighted avg", "samples avg"}:
                continue
            metric_lines.append(
                f"- `{label}`: precision `{round(float(row.get('precision', 0.0)), 4)}`, recall `{round(float(row.get('recall', 0.0)), 4)}`, F1 `{round(float(row.get('f1-score', 0.0)), 4)}`"
            )
    if not metric_lines:
        metric_lines = ["- Not available."]
    return "\n".join(
        [
            "# Private Weak-Label Model Experiment",
            "",
            WARNING,
            "",
            f"- Status: `{summary.get('status')}`",
            f"- Rows: `{summary.get('row_count')}`",
            f"- Usable weak-label rows: `{summary.get('usable_rows')}`",
            f"- Train rows: `{summary.get('train_rows', 0)}`",
            f"- Test rows: `{summary.get('test_rows', 0)}`",
            f"- Restricted artifact directory: `{summary.get('artifact_dir')}`",
            "",
            "## Label Counts",
            "",
            *label_lines,
            "",
            "## Per-Label Metrics",
            "",
            *metric_lines,
            "",
            "The artifact is not loaded by backend runtime and must remain under the restricted ignored directory.",
            "",
        ]
    )


def write_report(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_report(summary), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train a restricted local weak-label cue baseline experiment.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    args = parser.parse_args(argv)

    try:
        rows = read_rows(Path(args.input))
        summary = train(rows, Path(args.output_dir))
        write_report(Path(args.report_out), summary)
    except (FileNotFoundError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    printable = {
        "status": summary.get("status"),
        "row_count": summary.get("row_count"),
        "usable_rows": summary.get("usable_rows"),
        "label_count": len(summary.get("label_counts", {})),
    }
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
