#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
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
from vibesignal_ai.matching.model_io import load_match_pairs, write_json  # noqa: E402


SYNTHETIC_ROOT = (ROOT / "data" / "vibe_matching" / "synthetic").resolve()
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent)
    except ValueError:
        return False
    return True


def _skipped(reason: str, *, input_path: Path, model_name: str) -> dict[str, Any]:
    return {
        "status": "SKIPPED",
        "reason": reason,
        "input": str(input_path),
        "model_name": model_name,
        "provider_calls_made": False,
        "model_downloaded": False,
        "dataset_downloaded": False,
        "production_claims": False,
    }


def _pearson(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return 0.0
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_den = math.sqrt(sum((a - left_mean) ** 2 for a in left))
    right_den = math.sqrt(sum((b - right_mean) ** 2 for b in right))
    if not left_den or not right_den:
        return 0.0
    return numerator / (left_den * right_den)


def run_experiment(input_path: Path, model_name: str) -> dict[str, Any]:
    if not _is_under(input_path, SYNTHETIC_ROOT):
        raise ValueError("input path must be under data/vibe_matching/synthetic/")

    pair_summary = build_pair_validation_summary(input_path)
    if pair_summary["errors"]:
        raise ValueError("; ".join(pair_summary["errors"]))

    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        return _skipped("sentence-transformers is unavailable in this environment", input_path=input_path, model_name=model_name)

    try:
        model = SentenceTransformer(model_name, local_files_only=True)
    except Exception:
        return _skipped("requested embedding model is not available in the local cache", input_path=input_path, model_name=model_name)

    rows = load_match_pairs(input_path)
    left_texts = [str(row["text_a"]) for row in rows]
    right_texts = [str(row["text_b"]) for row in rows]
    left_embeddings = model.encode(left_texts, normalize_embeddings=True)
    right_embeddings = model.encode(right_texts, normalize_embeddings=True)
    similarities: list[float] = []
    for left, right in zip(left_embeddings, right_embeddings):
        similarities.append(float(sum(float(a) * float(b) for a, b in zip(left, right))))

    labels = [float(row["features"]["communication_fit"]) for row in rows]
    return {
        "status": "completed",
        "input": str(input_path),
        "model_name": model_name,
        "row_count": len(rows),
        "communication_fit_similarity_correlation": round(_pearson(similarities, labels), 4),
        "mean_similarity": round(sum(similarities) / len(similarities), 4) if similarities else 0.0,
        "provider_calls_made": False,
        "model_downloaded": False,
        "dataset_downloaded": False,
        "production_claims": False,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Vibe Embedding Experiment",
        "",
        "No production claims. This is an optional local-only research diagnostic on synthetic fixtures.",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Model: `{report.get('model_name')}`",
        f"- Provider calls made: `{report.get('provider_calls_made')}`",
        f"- Model downloaded: `{report.get('model_downloaded')}`",
        f"- Dataset downloaded: `{report.get('dataset_downloaded')}`",
    ]
    if report.get("status") == "SKIPPED":
        lines.append(f"- Reason: {report.get('reason')}")
    else:
        lines.append(f"- Communication-fit similarity correlation: `{report.get('communication_fit_similarity_correlation')}`")
    lines.extend(
        [
            "",
            "Blocked uses: deception, attraction, diagnosis, hidden intent, neurotype, attachment style, emotional truth, and response optimization.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an optional local-only Vibe embedding match experiment.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--model-name", default=DEFAULT_MODEL)
    parser.add_argument("--json-out")
    parser.add_argument("--markdown-out")
    args = parser.parse_args(argv)

    try:
        report = run_experiment(Path(args.input).expanduser().resolve(), args.model_name)
    except Exception as exc:
        print(f"Vibe embedding experiment refused: {exc}", file=sys.stderr)
        return 1

    if args.json_out:
        write_json(args.json_out, report)
    if args.markdown_out:
        out = Path(args.markdown_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
