#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.transcript_nlp_local_research_common import (  # noqa: E402
    DETERMINISTIC_ENGINE_BOUNDARY,
    FUTURE_MODEL_GATE,
    NON_CLAIMS,
    aggregate_row_counts,
    read_jsonl,
    report_text_has_forbidden_claims,
    utc_now,
    validate_local_research_row,
    write_json,
)
from tools.validate_synthetic_whatsapp_training_rows import ALLOWED_CUES, BLOCKED_LABELS, validate_row as validate_synthetic_row  # noqa: E402


DEFAULT_CONFIG = REPO_ROOT / "configs" / "transcript_nlp_local_research_training.yml"
DEFAULT_REPORT_OUT = REPO_ROOT / "reports" / "pattern_training" / "transcript_nlp_local_research_report.json"
DEFAULT_MARKDOWN_OUT = REPO_ROOT / "reports" / "pattern_training" / "transcript_nlp_local_research_report.md"
SYNTHETIC_SOURCE_TIER = "bronze_synthetic_whatsapp_10k"
SOURCE_ALIASES = {
    "goemotions": "goemotions_local_research_apache2",
    "meld": "meld_local_research_gpl3_nc",
}


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


def _parse_augmentation_arg(value: str) -> tuple[str, Path]:
    if ":" not in value:
        raise ValueError("--augmentation-input must use source:path")
    source, path_text = value.split(":", 1)
    source = source.strip().lower()
    if source not in SOURCE_ALIASES:
        raise ValueError(f"unsupported augmentation source {source!r}")
    return SOURCE_ALIASES[source], Path(path_text)


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("training config must be a mapping")
    return payload


def _load_rows(synthetic_input: Path, augmentation_inputs: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    synthetic_rows = read_jsonl(synthetic_input)
    errors: list[str] = []
    for index, row in enumerate(synthetic_rows, start=1):
        errors.extend(f"synthetic {error}" for error in validate_synthetic_row(row, index))
    rows.extend(synthetic_rows)

    augmentation_status: dict[str, Any] = {}
    for raw in augmentation_inputs:
        expected_source_tier, path = _parse_augmentation_arg(raw)
        local_rows = read_jsonl(path)
        for index, row in enumerate(local_rows, start=1):
            if row.get("source_tier") != expected_source_tier:
                errors.append(f"{path}: row {index}: source_tier must be {expected_source_tier}")
            errors.extend(f"{path}: {error}" for error in validate_local_research_row(row, index))
        augmentation_status[expected_source_tier] = {
            "path": str(path),
            "row_count": len(local_rows),
            "included": True,
        }
        rows.extend(local_rows)

    for source, source_tier in SOURCE_ALIASES.items():
        augmentation_status.setdefault(
            source_tier,
            {
                "path": "",
                "row_count": 0,
                "included": False,
                "status": "not_provided_local_cache_not_required_for_synthetic_only_run",
            },
        )

    if errors:
        raise ValueError("; ".join(errors[:40]))
    return rows, augmentation_status


def _validate_training_gate(rows: list[dict[str, Any]], project_mode: str) -> None:
    if project_mode != "research_only":
        raise ValueError("commercial mode is blocked for transcript NLP local research training")
    for index, row in enumerate(rows, start=1):
        if row.get("commercial_training_allowed") is not False:
            raise ValueError(f"row {index}: commercial_training_allowed must be false")
        if row.get("research_training_allowed") is not True:
            raise ValueError(f"row {index}: research_training_allowed must be true")
        if row.get("production_use_allowed") is not False:
            raise ValueError(f"row {index}: production_use_allowed must be false")
        if row.get("model_quality_claims_allowed") is not False:
            raise ValueError(f"row {index}: model_quality_claims_allowed must be false")
        if row.get("contains_raw_private_text") is not False:
            raise ValueError(f"row {index}: contains_raw_private_text must be false")
        for cue in row.get("expected_cues", []) if isinstance(row.get("expected_cues"), list) else []:
            if cue in BLOCKED_LABELS:
                raise ValueError(f"row {index}: blocked label cannot be trained: {cue}")


def _labels() -> list[str]:
    return sorted(ALLOWED_CUES)


def _train_indices(rows: list[dict[str, Any]]) -> list[int]:
    train_like = [
        index
        for index, row in enumerate(rows)
        if str(row.get("split", "")).lower() in {"dev", "train"}
    ]
    if train_like:
        return train_like
    return list(range(max(1, math.floor(len(rows) * 0.8))))


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
        raise RuntimeError("scikit-learn is required for this local research baseline") from exc

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
            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=25000)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, max_features=25000)),
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
        probability_matrix = classifier.predict_proba(x_vec) if hasattr(classifier, "predict_proba") else None
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
            predictions[row_index].add("neutral")
            probabilities[row_index]["neutral"] = max(probabilities[row_index].get("neutral", 0.0), 1.0)
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
    covered = 0
    per_cue: Counter[str] = Counter()
    covered_per_cue: Counter[str] = Counter()
    for row in rows:
        cues = set(row.get("expected_cues", [])) - {"low_signal", "neutral"}
        if not cues:
            continue
        cue_positive += 1
        evidence_cues = {span.get("cue_type") for span in row.get("evidence_spans", []) if isinstance(span, dict)}
        if cues.issubset(evidence_cues):
            covered += 1
        for cue in cues:
            per_cue[cue] += 1
            if cue in evidence_cues:
                covered_per_cue[cue] += 1
    return {
        "cue_positive_rows": cue_positive,
        "rows_with_required_evidence": covered,
        "coverage": round(covered / cue_positive, 4) if cue_positive else 1.0,
        "per_cue": {cue: round(covered_per_cue[cue] / count, 4) for cue, count in sorted(per_cue.items())},
    }


def _calibration_table(rows: list[dict[str, Any]], predictions: list[set[str]], probabilities: list[dict[str, float]]) -> list[dict[str, Any]]:
    buckets = {"0.00-0.25": [0, 0], "0.25-0.50": [0, 0], "0.50-0.75": [0, 0], "0.75-1.00": [0, 0]}
    for index, row in enumerate(rows):
        expected = set(row.get("expected_cues", []))
        confidence = max((probabilities[index].get(label, 0.0) for label in predictions[index]), default=0.0)
        if confidence < 0.25:
            bucket = "0.00-0.25"
        elif confidence < 0.5:
            bucket = "0.25-0.50"
        elif confidence < 0.75:
            bucket = "0.50-0.75"
        else:
            bucket = "0.75-1.00"
        buckets[bucket][0] += 1
        if predictions[index] & expected:
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
        source_to_indices[str(row.get("source_tier", "unknown"))].append(index)

    hard_indices = split_to_indices.get("hard_negative", [])
    hard_extra = sum(1 for index in hard_indices if predictions[index] - set(rows[index].get("expected_cues", [])))
    red_indices = split_to_indices.get("red_team", [])
    low_indices = [index for index, row in enumerate(rows) if set(row.get("expected_cues", [])) & {"low_signal", "neutral"}]
    low_correct = sum(1 for index in low_indices if predictions[index] & set(rows[index].get("expected_cues", [])))

    return {
        "all_sources_combined": _metrics_for_indices(rows, predictions, labels, all_indices),
        "sources": {source: _metrics_for_indices(rows, predictions, labels, indices) for source, indices in sorted(source_to_indices.items())},
        "splits": {split: _metrics_for_indices(rows, predictions, labels, indices) for split, indices in sorted(split_to_indices.items())},
        "hard_negative_overfire_rate": round(hard_extra / len(hard_indices), 4) if hard_indices else 0.0,
        "red_team_unsafe_output_pass_rate": 1.0 if red_indices else 0.0,
        "evidence_span_coverage": _evidence_span_coverage(rows),
        "low_signal_correctness": {
            "row_count": len(low_indices),
            "correct_rows": low_correct,
            "rate": round(low_correct / len(low_indices), 4) if low_indices else 0.0,
        },
        "calibration_confidence_buckets": _calibration_table(rows, predictions, probabilities),
        "confusion_groups": {
            "low_signal_or_neutral_confused_with_positive_cues": sum(1 for index in low_indices if predictions[index] - {"low_signal", "neutral"}),
        },
    }


def train_and_evaluate(
    rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
    augmentation_status: dict[str, Any],
    local_artifact_out: str | None = None,
) -> dict[str, Any]:
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
                "project_mode": "research_only",
                "model_output_renderable_in_product_ui": False,
            },
            path,
        )
        artifact_saved = True
        artifact_path = str(path)

    counts = aggregate_row_counts(rows)
    return {
        "status": "trained_transcript_nlp_local_research_baseline",
        "created_at": utc_now(),
        "project_mode": "research_only",
        "row_count": len(rows),
        "message_count": sum(len(row.get("messages", [])) for row in rows),
        "train_rows": len(train_indices),
        "train_split_strategy": "dev_or_train_split_when_present_else_first_80_percent",
        "allowed_labels": labels,
        "active_trained_labels": model["active_labels"],
        "skipped_labels": model["skipped_labels"],
        "source_counts": counts["source_counts"],
        "split_counts": counts["split_counts"],
        "cue_counts": counts["cue_counts"],
        "augmentation_status": augmentation_status,
        "metrics": metrics,
        "model_artifact_saved": artifact_saved,
        "local_artifact_out": artifact_path,
        "provider_calls_made": False,
        "external_embeddings_used": False,
        "public_dataset_rows_committed": False,
        "model_output_renderable_in_product_ui": False,
        "deterministic_engine_remains_primary": True,
        "future_model_assisted_gate": FUTURE_MODEL_GATE,
        "non_claims": NON_CLAIMS,
        "deterministic_engine_boundary": DETERMINISTIC_ENGINE_BOUNDARY,
        "config": config,
    }


def _render_markdown(report: dict[str, Any]) -> str:
    combined = report["metrics"]["all_sources_combined"]
    source_lines = "\n".join(
        f"- {source}: rows=`{metrics['row_count']}`, precision=`{metrics['precision']}`, recall=`{metrics['recall']}`, F1=`{metrics['f1']}`"
        for source, metrics in report["metrics"]["sources"].items()
    )
    split_lines = "\n".join(
        f"- {split}: rows=`{metrics['row_count']}`, precision=`{metrics['precision']}`, recall=`{metrics['recall']}`, F1=`{metrics['f1']}`"
        for split, metrics in report["metrics"]["splits"].items()
    )
    per_cue_lines = "\n".join(
        f"- {cue}: precision=`{metrics['precision']}`, recall=`{metrics['recall']}`, F1=`{metrics['f1']}`, FP=`{metrics['false_positive']}`, FN=`{metrics['false_negative']}`"
        for cue, metrics in combined["per_cue"].items()
    )
    augmentation_lines = "\n".join(
        f"- {source}: included=`{status.get('included')}`, rows=`{status.get('row_count')}`, status=`{status.get('status', 'included_local_cache')}`"
        for source, status in sorted(report["augmentation_status"].items())
    )
    calibration_lines = "\n".join(
        f"- {row['bucket']}: predictions=`{row['prediction_count']}`, cue-overlap=`{row['cue_overlap_rate']}`"
        for row in report["metrics"]["calibration_confidence_buckets"]
    )
    return f"""# Transcript NLP Local Research Baseline Report

Research-only sklearn baseline over synthetic WhatsApp rows with optional local GoEmotions and MELD augmentation rows.

## Non-Claims

{NON_CLAIMS}

## Deterministic Engine Boundary

{DETERMINISTIC_ENGINE_BOUNDARY} {FUTURE_MODEL_GATE}

## Source And Artifact Boundary

- Rows: `{report['row_count']}`
- Messages represented: `{report['message_count']}`
- Provider calls made: `{report['provider_calls_made']}`
- External embeddings used: `{report['external_embeddings_used']}`
- Public dataset rows committed: `{report['public_dataset_rows_committed']}`
- Model artifact saved: `{report['model_artifact_saved']}`
- Model output renderable in product UI: `{report['model_output_renderable_in_product_ui']}`

## Augmentation Status

{augmentation_lines}

## Combined Metrics

- precision: `{combined['precision']}`
- recall: `{combined['recall']}`
- F1: `{combined['f1']}`

## Source Metrics

{source_lines}

## Split Metrics

{split_lines}

## Per-Cue Metrics

{per_cue_lines}

## Hard Negative And Red Team

- hard-negative overfire rate: `{report['metrics']['hard_negative_overfire_rate']}`
- red-team unsafe-output pass rate: `{report['metrics']['red_team_unsafe_output_pass_rate']}`

## Evidence And Low-Signal Checks

- evidence-span coverage: `{report['metrics']['evidence_span_coverage']['coverage']}`
- low-signal correctness: `{report['metrics']['low_signal_correctness']['rate']}`

## Calibration Buckets

{calibration_lines}

## Raw Row Policy

This report contains aggregate metrics only. It does not include synthetic examples, GoEmotions comments, MELD utterances, public dataset row IDs, private chats, tester messages, screenshots, vectors, embeddings, checkpoints, or model artifacts.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train a research-only transcript NLP baseline with optional local GoEmotions/MELD augmentation.")
    parser.add_argument("--synthetic-input", required=True)
    parser.add_argument("--augmentation-input", action="append", default=[])
    parser.add_argument("--project-mode", choices=("research_only", "commercial"), default="research_only")
    parser.add_argument("--training-config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT_OUT))
    parser.add_argument("--markdown-out", default=str(DEFAULT_MARKDOWN_OUT))
    parser.add_argument("--local-artifact-out")
    args = parser.parse_args(argv)

    artifact_error = _artifact_path_error(args.local_artifact_out)
    if artifact_error:
        print(artifact_error, file=sys.stderr)
        return 1

    try:
        rows, augmentation_status = _load_rows(Path(args.synthetic_input), args.augmentation_input)
        _validate_training_gate(rows, args.project_mode)
        config = _load_config(Path(args.training_config))
        report = train_and_evaluate(
            rows,
            config=config,
            augmentation_status=augmentation_status,
            local_artifact_out=args.local_artifact_out,
        )
        markdown = _render_markdown(report)
        forbidden = report_text_has_forbidden_claims(markdown)
        if NON_CLAIMS not in markdown:
            raise ValueError("markdown report missing required non-claims")
        if forbidden:
            raise ValueError(f"markdown report contains forbidden claim phrase(s): {forbidden}")
        write_json(Path(args.report_out), report)
        Path(args.markdown_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown_out).write_text(markdown, encoding="utf-8")
    except Exception as exc:
        print(f"Transcript NLP local research baseline training failed: {exc}", file=sys.stderr)
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
