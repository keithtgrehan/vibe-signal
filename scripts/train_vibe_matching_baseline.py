#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scripts.validate_vibe_match_pairs import build_summary as build_pair_validation_summary  # noqa: E402
from scripts.validate_vibe_training_sources import build_summary as build_source_summary  # noqa: E402
from vibesignal_ai.matching.model_io import MATCHING_LABELS, load_match_pairs, pair_text, render_baseline_markdown, write_json  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "vibe_training_sources.example.yml"
SYNTHETIC_ROOT = (ROOT / "data" / "vibe_matching" / "synthetic").resolve()


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent)
    except ValueError:
        return False
    return True


def validate_training_gate(input_path: Path, project_mode: str, config: Path = DEFAULT_CONFIG) -> list[str]:
    errors: list[str] = []
    if project_mode == "commercial":
        return ["commercial mode is blocked for Vibe matching baseline training"]
    if project_mode != "research_only":
        return [f"invalid project mode {project_mode!r}"]
    if not input_path.exists():
        errors.append(f"input path does not exist: {input_path}")
    if not _is_under(input_path, SYNTHETIC_ROOT):
        errors.append("input path must be under data/vibe_matching/synthetic/")

    source_summary = build_source_summary(config, project_mode)
    if source_summary["errors"]:
        errors.extend(f"training-source gate: {error}" for error in source_summary["errors"])
    if source_summary.get("training_ready_source_ids") != ["synthetic_vibe_matching"]:
        errors.append("training-source gate must expose only synthetic_vibe_matching as training-ready")

    if input_path.exists():
        pair_summary = build_pair_validation_summary(input_path)
        if pair_summary["errors"]:
            errors.extend(f"match-pair gate: {error}" for error in pair_summary["errors"])
    return errors


def _fallback_metric(y_true: list[int]) -> dict[str, Any]:
    majority = 1 if sum(y_true) >= len(y_true) / 2 else 0
    correct = sum(1 for value in y_true if value == majority)
    accuracy = correct / len(y_true) if y_true else 0.0
    return {
        "trained": False,
        "accuracy": round(accuracy, 4),
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "confusion_matrix": [],
        "note": "Skipped classifier because only one class was present.",
    }


def _template_category(row: dict[str, Any]) -> str:
    return str(row.get("provenance", {}).get("template_category", "")).strip()


def train_baseline(rows: list[dict[str, Any]], *, project_mode: str) -> dict[str, Any]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
        from sklearn.pipeline import FeatureUnion
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("scikit-learn is required for the research-only matching baseline") from exc

    texts = [pair_text(row) for row in rows]
    template_categories = sorted({_template_category(row) for row in rows if _template_category(row)})
    test_template_categories = set(template_categories[::4])
    if not test_template_categories and template_categories:
        test_template_categories = {template_categories[-1]}

    train_indices = [
        index
        for index, row in enumerate(rows)
        if _template_category(row) not in test_template_categories
    ]
    test_indices = [index for index in range(len(rows)) if index not in set(train_indices)]
    if not train_indices or not test_indices:
        raise ValueError("template-category holdout split requires at least one train and test category")

    x_train = [texts[index] for index in train_indices]
    x_test = [texts[index] for index in test_indices]

    metrics_by_label: dict[str, Any] = {}
    for label in MATCHING_LABELS:
        y = [int(row["features"][label]) for row in rows]
        y_train = [y[index] for index in train_indices]
        y_test = [y[index] for index in test_indices]
        if len(set(y_train)) < 2 or len(set(y_test)) < 2:
            metrics_by_label[label] = _fallback_metric(y_test)
            continue
        vectorizer = FeatureUnion(
            [
                ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)),
            ]
        )
        x_train_vec = vectorizer.fit_transform(x_train)
        x_test_vec = vectorizer.transform(x_test)
        clf = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
        clf.fit(x_train_vec, y_train)
        pred = clf.predict(x_test_vec)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, pred, average="binary", zero_division=0)
        metrics_by_label[label] = {
            "trained": True,
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
            "confusion_matrix": confusion_matrix(y_test, pred, labels=[0, 1]).tolist(),
        }

    f1_values = [row["f1"] for row in metrics_by_label.values() if row.get("trained")]
    return {
        "status": "trained",
        "project_mode": project_mode,
        "row_count": len(rows),
        "source_id": "synthetic_vibe_matching",
        "split": {
            "strategy": "template_category_holdout",
            "train_rows": len(train_indices),
            "test_rows": len(test_indices),
            "test_template_categories": sorted(test_template_categories),
        },
        "metrics_by_label": metrics_by_label,
        "macro_f1_trained_labels": round(sum(f1_values) / len(f1_values), 4) if f1_values else 0.0,
        "benchmark_scope": "synthetic_fixture_template_holdout",
        "production_claims": False,
        "public_quality_claims_supported": False,
        "blocked_claims": [
            "deception",
            "hidden_intent",
            "attraction",
            "cheating",
            "diagnosis",
            "neurotype",
            "attachment_style",
            "manipulation",
            "emotional_truth",
            "relationship_success",
        ],
        "provider_calls_made": False,
        "model_artifacts_saved": False,
        "vector_artifacts_created": False,
        "training_data": "synthetic_vibe_matching_only",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train a research-only sklearn Vibe matching baseline on synthetic fixtures.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--project-mode", choices=("research_only", "commercial"), default="research_only")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--report-out")
    parser.add_argument("--markdown-out")
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    errors = validate_training_gate(input_path, args.project_mode, Path(args.config))
    if errors:
        print("Vibe matching baseline training refused:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    rows = load_match_pairs(input_path)
    report = train_baseline(rows, project_mode=args.project_mode)
    if args.report_out:
        write_json(args.report_out, report)
    if args.markdown_out:
        out = Path(args.markdown_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_baseline_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
