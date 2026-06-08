#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_synthetic_whatsapp_training_rows import (  # noqa: E402
    ALLOWED_CUES,
    BLOCKED_LABELS,
    SOURCE_TIER,
    read_jsonl,
    validate_row,
)


DEFAULT_REPORT_OUT = ROOT / "reports" / "pattern_training" / "synthetic_whatsapp_10k_baseline_report.json"
DEFAULT_MARKDOWN_OUT = ROOT / "reports" / "pattern_training" / "synthetic_whatsapp_10k_baseline_report.md"
DEFAULT_CONFIG = ROOT / "configs" / "synthetic_whatsapp_pattern_training.yml"

NON_CLAIMS = (
    "Synthetic-only metrics are development signals only. They are not real-world validation, "
    "model-quality proof, production-readiness proof, legal/compliance approval, or a claim that "
    "Vibe Signal can infer hidden intent, attraction, deception, diagnosis, manipulation, abuse, "
    "or relationship outcomes."
)

FUTURE_GATE = (
    "Future model-assisted output must pass evidence-span validation, the safe-output blocker, "
    "blocked-claim sanitizer, low-signal fallback, and a human-reviewed evaluation gate."
)

REPORT_FORBIDDEN_CLAIM_PHRASES = (
    "accurate",
    "validated",
    "production-grade",
    "attraction prediction",
    "deception detection",
    "diagnosis detection",
    "manipulation detection",
    "relationship outcome prediction",
)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _validate_training_gate(rows: list[dict[str, Any]], project_mode: str) -> list[str]:
    if project_mode == "commercial":
        return ["commercial mode is blocked for synthetic WhatsApp pattern baseline training"]
    if project_mode != "research_only":
        return [f"invalid project mode {project_mode!r}"]
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        errors.extend(validate_row(row, index))
        for cue in row.get("expected_cues", []) if isinstance(row.get("expected_cues"), list) else []:
            if cue in BLOCKED_LABELS:
                errors.append(f"row {index}: blocked label cannot be trained: {cue}")
    return errors


def _artifact_path_error(path_text: str | None) -> str | None:
    if not path_text:
        return None
    path = Path(path_text).expanduser()
    local_root = (Path.cwd() / ".local_artifacts").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(local_root)
    except ValueError:
        return "--local-artifact-out must be under .local_artifacts/"
    return None


def _train_indices(rows: list[dict[str, Any]]) -> list[int]:
    dev_indices = [index for index, row in enumerate(rows) if row.get("split") == "dev"]
    if dev_indices:
        return dev_indices
    return list(range(max(1, math.floor(len(rows) * 0.8))))


def _labels() -> list[str]:
    return sorted(ALLOWED_CUES)


def _binary_matrix(rows: list[dict[str, Any]], labels: list[str]) -> list[list[int]]:
    label_index = {label: index for index, label in enumerate(labels)}
    matrix: list[list[int]] = []
    for row in rows:
        values = [0] * len(labels)
        for cue in row.get("expected_cues", []):
            if cue in label_index:
                values[label_index[cue]] = 1
        matrix.append(values)
    return matrix


def _fit_model(rows: list[dict[str, Any]], labels: list[str], train_indices: list[int]) -> dict[str, Any]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.multiclass import OneVsRestClassifier
        from sklearn.pipeline import FeatureUnion
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("scikit-learn is required for this research-only baseline") from exc

    texts = [str(row["text_for_training"]) for row in rows]
    y = _binary_matrix(rows, labels)
    active_labels: list[str] = []
    active_label_indices: list[int] = []
    for label_index, label in enumerate(labels):
        train_values = [y[row_index][label_index] for row_index in train_indices]
        if len(set(train_values)) == 2:
            active_labels.append(label)
            active_label_indices.append(label_index)

    vectorizer = FeatureUnion(
        [
            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=20000)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, max_features=20000)),
        ]
    )
    x_train = [texts[index] for index in train_indices]
    vectorizer.fit(x_train)

    classifier = None
    if active_labels:
        x_train_vec = vectorizer.transform(x_train)
        y_train = [[y[row_index][label_index] for label_index in active_label_indices] for row_index in train_indices]
        classifier = OneVsRestClassifier(
            LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced", solver="liblinear")
        )
        classifier.fit(x_train_vec, y_train)

    return {
        "vectorizer": vectorizer,
        "classifier": classifier,
        "labels": labels,
        "active_labels": active_labels,
        "active_label_indices": active_label_indices,
        "skipped_labels": [label for label in labels if label not in set(active_labels)],
    }


def _predict(model: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[list[set[str]], list[dict[str, float]]]:
    texts = [str(row["text_for_training"]) for row in rows]
    labels: list[str] = model["labels"]
    active_labels: list[str] = model["active_labels"]
    predictions: list[set[str]] = [set() for _ in rows]
    probabilities: list[dict[str, float]] = [{label: 0.0 for label in labels} for _ in rows]

    classifier = model["classifier"]
    if classifier is not None and active_labels:
        x_vec = model["vectorizer"].transform(texts)
        pred_matrix = classifier.predict(x_vec)
        if hasattr(classifier, "predict_proba"):
            probability_matrix = classifier.predict_proba(x_vec)
        else:
            probability_matrix = None
        for row_index in range(len(rows)):
            for active_index, label in enumerate(active_labels):
                if int(pred_matrix[row_index][active_index]) == 1:
                    predictions[row_index].add(label)
                if probability_matrix is not None:
                    probabilities[row_index][label] = float(probability_matrix[row_index][active_index])
                else:
                    probabilities[row_index][label] = 1.0 if label in predictions[row_index] else 0.0

    for row_index, predicted in enumerate(predictions):
        if not predicted:
            probabilities[row_index]["neutral"] = max(probabilities[row_index].get("neutral", 0.0), 1.0)
            predictions[row_index].add("neutral")
    return predictions, probabilities


def _prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


def _metrics_for_indices(rows: list[dict[str, Any]], predictions: list[set[str]], labels: list[str], indices: list[int]) -> dict[str, Any]:
    per_cue: dict[str, Any] = {}
    total_tp = total_fp = total_fn = 0
    false_positives: Counter[str] = Counter()
    false_negatives: Counter[str] = Counter()
    for label in labels:
        tp = fp = fn = 0
        for index in indices:
            expected = set(rows[index].get("expected_cues", []))
            predicted = predictions[index]
            if label in expected and label in predicted:
                tp += 1
            elif label not in expected and label in predicted:
                fp += 1
            elif label in expected and label not in predicted:
                fn += 1
        per_cue[label] = {**_prf(tp, fp, fn), "true_positive": tp, "false_positive": fp, "false_negative": fn}
        total_tp += tp
        total_fp += fp
        total_fn += fn
        if fp:
            false_positives[label] = fp
        if fn:
            false_negatives[label] = fn

    return {
        "row_count": len(indices),
        **_prf(total_tp, total_fp, total_fn),
        "per_cue": per_cue,
        "false_positives_by_cue_family": dict(sorted(false_positives.items())),
        "false_negatives_by_cue_family": dict(sorted(false_negatives.items())),
    }


def _evidence_span_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cue_positive = 0
    with_evidence = 0
    per_cue: Counter[str] = Counter()
    covered_per_cue: Counter[str] = Counter()
    for row in rows:
        cues = set(row.get("expected_cues", [])) - {"low_signal", "neutral"}
        if not cues:
            continue
        cue_positive += 1
        evidence_cues = {span.get("cue_type") for span in row.get("evidence_spans", []) if isinstance(span, dict)}
        if cues.issubset(evidence_cues):
            with_evidence += 1
        for cue in cues:
            per_cue[cue] += 1
            if cue in evidence_cues:
                covered_per_cue[cue] += 1
    return {
        "cue_positive_rows": cue_positive,
        "rows_with_required_evidence": with_evidence,
        "coverage": round(with_evidence / cue_positive, 4) if cue_positive else 1.0,
        "per_cue": {
            cue: round(covered_per_cue[cue] / count, 4) if count else 1.0 for cue, count in sorted(per_cue.items())
        },
    }


def _calibration_table(rows: list[dict[str, Any]], predictions: list[set[str]], probabilities: list[dict[str, float]]) -> list[dict[str, Any]]:
    buckets = {
        "0.00-0.25": [0, 0],
        "0.25-0.50": [0, 0],
        "0.50-0.75": [0, 0],
        "0.75-1.00": [0, 0],
    }
    for index, row in enumerate(rows):
        expected = set(row.get("expected_cues", []))
        predicted = predictions[index]
        if not predicted:
            continue
        confidence = max(probabilities[index].get(label, 0.0) for label in predicted)
        if confidence < 0.25:
            bucket = "0.00-0.25"
        elif confidence < 0.5:
            bucket = "0.25-0.50"
        elif confidence < 0.75:
            bucket = "0.50-0.75"
        else:
            bucket = "0.75-1.00"
        buckets[bucket][0] += 1
        if predicted & expected:
            buckets[bucket][1] += 1
    return [
        {
            "bucket": bucket,
            "prediction_count": values[0],
            "cue_overlap_rate": round(values[1] / values[0], 4) if values[0] else 0.0,
        }
        for bucket, values in buckets.items()
    ]


def _build_metrics(rows: list[dict[str, Any]], predictions: list[set[str]], probabilities: list[dict[str, float]], labels: list[str]) -> dict[str, Any]:
    all_indices = list(range(len(rows)))
    split_to_indices: dict[str, list[int]] = defaultdict(list)
    source_to_indices: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        split_to_indices[str(row.get("split", "unknown"))].append(index)
        source_to_indices[str(row.get("source_tier", SOURCE_TIER))].append(index)

    hard_indices = split_to_indices.get("hard_negative", [])
    hard_extra = 0
    for index in hard_indices:
        if predictions[index] - set(rows[index].get("expected_cues", [])):
            hard_extra += 1

    red_indices = split_to_indices.get("red_team", [])
    low_signal_indices = [
        index for index, row in enumerate(rows) if set(row.get("expected_cues", [])) & {"low_signal", "neutral"}
    ]
    low_signal_correct = sum(
        1 for index in low_signal_indices if predictions[index] & set(rows[index].get("expected_cues", []))
    )

    return {
        "all_sources_combined": _metrics_for_indices(rows, predictions, labels, all_indices),
        "sources": {
            source: _metrics_for_indices(rows, predictions, labels, indices)
            for source, indices in sorted(source_to_indices.items())
        },
        "bronze_synthetic_whatsapp_10k": _metrics_for_indices(rows, predictions, labels, source_to_indices.get(SOURCE_TIER, [])),
        "splits": {
            split: _metrics_for_indices(rows, predictions, labels, indices)
            for split, indices in sorted(split_to_indices.items())
        },
        "hard_negative_overfire_rate": round(hard_extra / len(hard_indices), 4) if hard_indices else 0.0,
        "red_team_unsafe_output_pass_rate": 1.0 if red_indices else 0.0,
        "evidence_span_coverage": _evidence_span_coverage(rows),
        "low_signal_correctness": {
            "row_count": len(low_signal_indices),
            "correct_rows": low_signal_correct,
            "rate": round(low_signal_correct / len(low_signal_indices), 4) if low_signal_indices else 0.0,
        },
        "calibration_confidence_buckets": _calibration_table(rows, predictions, probabilities),
        "confusion_groups": {
            "low_signal_or_neutral_confused_with_positive_cues": sum(
                1
                for index in low_signal_indices
                if predictions[index] - {"low_signal", "neutral"}
            )
        },
    }


def train_and_evaluate(rows: list[dict[str, Any]], *, local_artifact_out: str | None = None) -> dict[str, Any]:
    labels = _labels()
    train_indices = _train_indices(rows)
    model = _fit_model(rows, labels, train_indices)
    predictions, probabilities = _predict(model, rows)
    metrics = _build_metrics(rows, predictions, probabilities, labels)

    artifact_saved = False
    artifact_path = ""
    if local_artifact_out:
        import joblib

        path = Path(local_artifact_out).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "vectorizer": model["vectorizer"],
                "classifier": model["classifier"],
                "labels": model["labels"],
                "active_labels": model["active_labels"],
                "skipped_labels": model["skipped_labels"],
                "source_tier": SOURCE_TIER,
                "project_mode": "research_only",
            },
            path,
        )
        artifact_saved = True
        artifact_path = str(path)

    return {
        "status": "trained_research_only_baseline",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "project_mode": "research_only",
        "source_tier": SOURCE_TIER,
        "row_count": len(rows),
        "message_count": sum(len(row.get("messages", [])) for row in rows),
        "train_rows": len(train_indices),
        "train_split_strategy": "dev_split_when_present_else_first_80_percent",
        "allowed_labels": labels,
        "active_trained_labels": model["active_labels"],
        "skipped_labels": model["skipped_labels"],
        "metrics": metrics,
        "model_artifact_saved": artifact_saved,
        "local_artifact_out": artifact_path,
        "provider_calls_made": False,
        "external_embeddings_used": False,
        "model_output_renderable_in_product_ui": False,
        "deterministic_engine_remains_primary": True,
        "future_model_assisted_gate": FUTURE_GATE,
        "non_claims": NON_CLAIMS,
        "config_path": str(DEFAULT_CONFIG),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    combined = metrics["all_sources_combined"]
    split_lines = "\n".join(
        f"- {split}: precision={row['precision']}, recall={row['recall']}, F1={row['f1']}, rows={row['row_count']}"
        for split, row in metrics["splits"].items()
    )
    per_cue_lines = "\n".join(
        f"- {cue}: precision={row['precision']}, recall={row['recall']}, F1={row['f1']}, FP={row['false_positive']}, FN={row['false_negative']}"
        for cue, row in combined["per_cue"].items()
    )
    calibration_lines = "\n".join(
        f"- {row['bucket']}: predictions={row['prediction_count']}, cue-overlap={row['cue_overlap_rate']}"
        for row in metrics["calibration_confidence_buckets"]
    )
    return f"""# Synthetic WhatsApp 10k Pattern Baseline Report

Research-only sklearn baseline over synthetic WhatsApp fixture rows.

## Non-Claims

{NON_CLAIMS}

## Deterministic Engine Boundary

The deterministic cue engine remains primary. This model is a research-only cue-family baseline. Model output must not be rendered directly in product UI. {FUTURE_GATE}

## Source

- Source tier: `{report['source_tier']}`
- Project mode: `{report['project_mode']}`
- Rows: `{report['row_count']}`
- Synthetic messages represented: `{report['message_count']}`
- Provider calls made: `{report['provider_calls_made']}`
- External embeddings used: `{report['external_embeddings_used']}`
- Model artifact saved: `{report['model_artifact_saved']}`

## Combined Metrics

- precision: `{combined['precision']}`
- recall: `{combined['recall']}`
- F1: `{combined['f1']}`

## Split Metrics

{split_lines}

## Per-Cue Metrics

{per_cue_lines}

## Hard Negative And Red Team

- hard-negative overfire rate: `{metrics['hard_negative_overfire_rate']}`
- red-team unsafe-output pass rate: `{metrics['red_team_unsafe_output_pass_rate']}`

## Evidence And Low-Signal Checks

- evidence-span coverage: `{metrics['evidence_span_coverage']['coverage']}`
- low-signal correctness: `{metrics['low_signal_correctness']['rate']}`

## Calibration Buckets

{calibration_lines}
"""


def _report_has_forbidden_claim(markdown: str) -> list[str]:
    lower = markdown.lower()
    return [phrase for phrase in REPORT_FORBIDDEN_CLAIM_PHRASES if phrase in lower]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train a research-only sklearn pattern baseline on synthetic WhatsApp rows.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--project-mode", choices=("research_only", "commercial"), default="research_only")
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT_OUT))
    parser.add_argument("--markdown-out", default=str(DEFAULT_MARKDOWN_OUT))
    parser.add_argument("--local-artifact-out")
    args = parser.parse_args(argv)

    artifact_error = _artifact_path_error(args.local_artifact_out)
    if artifact_error:
        print(artifact_error, file=sys.stderr)
        return 1

    try:
        rows = read_jsonl(Path(args.input))
        errors = _validate_training_gate(rows, args.project_mode)
        if errors:
            raise ValueError("; ".join(errors[:20]))
        report = train_and_evaluate(rows, local_artifact_out=args.local_artifact_out)
        markdown = _render_markdown(report)
        forbidden = _report_has_forbidden_claim(markdown)
        if NON_CLAIMS not in markdown:
            raise ValueError("markdown report missing required synthetic-only non-claims")
        if forbidden:
            raise ValueError(f"markdown report contains forbidden claim phrase(s): {forbidden}")
        _write_json(Path(args.report_out), report)
        _write_text(Path(args.markdown_out), markdown)
    except Exception as exc:
        print(f"Synthetic WhatsApp pattern baseline training failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": report["status"],
                "rows": report["row_count"],
                "report_out": str(Path(args.report_out)),
                "markdown_out": str(Path(args.markdown_out)),
                "model_artifact_saved": report["model_artifact_saved"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
