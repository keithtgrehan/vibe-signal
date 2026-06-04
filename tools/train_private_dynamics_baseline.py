#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_ROOT = REPO_ROOT / "data" / "restricted" / "private_whatsapp"
SYNTHETIC_ROOT = REPO_ROOT / "data" / "synthetic" / "private_inspired"
ENGINE_REPORT_DIR = REPO_ROOT / "reports" / "engine_eval"
DEFAULT_INPUT = SYNTHETIC_ROOT / "dynamics_fixtures.jsonl"
DEFAULT_REPORT = ENGINE_REPORT_DIR / "private_dynamics_baseline_experiment.md"
DEFAULT_MODEL_OUTPUT = RESTRICTED_ROOT / "models" / "private_dynamics_baseline.pkl"
DISCLAIMER = "Weak-label/synthetic local experiment only. Not human-reviewed. Not production. Not a model-quality claim."


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def _is_under(path: Path, root: Path) -> bool:
    try:
        _resolve(path).relative_to(_resolve(root))
        return True
    except ValueError:
        return False


def _is_restricted_review_csv(path: Path) -> bool:
    name = path.name.lower()
    return _is_under(path, RESTRICTED_ROOT) and path.suffix.lower() == ".csv" and ("review" in name or "label" in name)


def _is_synthetic_fixture(path: Path) -> bool:
    return _is_under(path, SYNTHETIC_ROOT) and path.suffix.lower() in {".jsonl", ".json"}


def _input_allowed(path: Path) -> bool:
    return _is_restricted_review_csv(path) or _is_synthetic_fixture(path)


def _report_allowed(path: Path, source_kind: str) -> bool:
    if source_kind == "restricted_review_csv":
        return _is_under(path, RESTRICTED_ROOT)
    return _is_under(path, ENGINE_REPORT_DIR) or _is_under(path, RESTRICTED_ROOT)


def _model_allowed(path: Path) -> bool:
    return _is_under(path, RESTRICTED_ROOT)


def _safe_error(message: str) -> None:
    print(message, file=sys.stderr)


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _row_text(row: dict[str, Any]) -> str:
    if row.get("text"):
        return str(row["text"])
    messages = row.get("messages")
    if isinstance(messages, list):
        return " ".join(str(message.get("text", "")) for message in messages if isinstance(message, dict))
    return ""


def _row_label(row: dict[str, Any]) -> str:
    for key in ("weak_label", "category", "cue_id", "label"):
        if row.get(key):
            return str(row[key])
    cue_labels = row.get("cue_labels")
    if isinstance(cue_labels, list) and cue_labels:
        return str(cue_labels[0])
    return ""


def _load_examples(path: Path) -> tuple[list[str], list[str], str]:
    texts: list[str] = []
    labels: list[str] = []
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                text = str(row.get("text", row.get("evidence_text", "")) or "")
                label = str(row.get("weak_label", row.get("cue_id", row.get("label", ""))) or "")
                if text and label:
                    texts.append(text)
                    labels.append(label)
        return texts, labels, "restricted_review_csv"
    rows = _read_jsonl_rows(path)
    for row in rows:
        text = _row_text(row)
        label = _row_label(row)
        if text and label:
            texts.append(text)
            labels.append(label)
    return texts, labels, "synthetic_fixture"


def _write_report(path: Path, *, status: str, source_kind: str, sample_count: int, labels: list[str], details: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Private Dynamics Baseline Experiment",
        "",
        DISCLAIMER,
        "",
        f"- Status: `{status}`",
        f"- Source kind: `{source_kind}`",
        f"- Samples used: `{sample_count}`",
        f"- Label count: `{len(set(labels))}`",
        f"- Labels: `{', '.join(sorted(set(labels))) if labels else 'none'}`",
        "- Raw text printed: `false`",
        "- External API calls: `false`",
        "- Production integration: `false`",
        "",
        "Details:",
        *[f"- {item}" for item in details],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _train_with_sklearn(texts: list[str], labels: list[str], model_output: Path) -> list[str]:
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
    except Exception:
        return ["sklearn unavailable; skipped fitting gracefully."]

    if len(texts) < 4 or len(set(labels)) < 2:
        return ["Insufficient weak-label examples for fitting; skipped fitting gracefully."]

    pipeline = Pipeline(
        [
            ("vectorizer", CountVectorizer(ngram_range=(1, 2), min_df=1)),
            ("classifier", LogisticRegression(max_iter=200, class_weight="balanced")),
        ]
    )
    pipeline.fit(texts, labels)
    model_output.parent.mkdir(parents=True, exist_ok=True)
    with model_output.open("wb") as handle:
        pickle.dump(pipeline, handle)
    return ["Fitted sklearn weak-label baseline locally.", "Restricted model artifact written under the ignored private WhatsApp model directory."]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train a local weak-label/synthetic WhatsApp dynamics baseline.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--model-output", default=str(DEFAULT_MODEL_OUTPUT))
    args = parser.parse_args(argv)

    input_path = _resolve(Path(args.input))
    report_out = _resolve(Path(args.report_out))
    model_output = _resolve(Path(args.model_output))

    if not input_path.exists():
        _safe_error("Baseline input was not found.")
        return 1
    if not _input_allowed(input_path):
        _safe_error("Refusing baseline input that is neither a restricted review CSV nor a synthetic dynamics fixture.")
        return 1
    source_kind = "restricted_review_csv" if _is_restricted_review_csv(input_path) else "synthetic_fixture"
    if not _report_allowed(report_out, source_kind):
        _safe_error("Refusing baseline report path outside reports/engine_eval or restricted private WhatsApp tree.")
        return 1
    if not _model_allowed(model_output):
        _safe_error("Refusing model output outside the restricted private WhatsApp tree.")
        return 1

    try:
        texts, labels, source_kind = _load_examples(input_path)
        details = _train_with_sklearn(texts, labels, model_output)
        status = "skipped" if any("skipped" in item for item in details) else "trained"
        _write_report(report_out, status=status, source_kind=source_kind, sample_count=len(texts), labels=labels, details=details)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        _safe_error(f"Private dynamics baseline failed: {exc}")
        return 1

    print(
        json.dumps(
            {
                "status": status,
                "samples_used": len(texts),
                "label_count": len(set(labels)),
                "report": str(report_out),
                "raw_text_printed": False,
                "external_api_calls": False,
                "production_integration": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
