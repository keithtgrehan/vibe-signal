#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.transcript_nlp_local_research_common import (  # noqa: E402
    MELD_SOURCE_TIER,
    aggregate_row_counts,
    build_local_research_row,
    cues_from_meld,
    ensure_local_row_output_path,
    normalize_split,
    utc_now,
    validate_local_research_row,
    write_jsonl,
)


def _load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("source_tier") != MELD_SOURCE_TIER:
        raise ValueError("MELD manifest source_tier mismatch")
    if payload.get("license_id") != "gpl-3.0" or payload.get("license_metadata_confirmed") is not True:
        raise ValueError("MELD manifest must confirm GPL-3.0 metadata")
    required_false = (
        "audio_video_used",
        "commercial_training_allowed",
        "production_use_allowed",
        "model_quality_claims_allowed",
        "row_commit_allowed",
        "raw_rows_committed",
    )
    for field in required_false:
        if payload.get(field) is not False:
            raise ValueError(f"MELD manifest requires {field}=false")
    if payload.get("local_only") is not True or payload.get("text_only") is not True:
        raise ValueError("MELD manifest must be local_only and text_only")
    files = payload.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("MELD manifest missing files")
    return payload


def _read_split_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    label_counts: Counter[str] = Counter()
    skipped_empty_text = 0
    files = manifest["files"]
    for split, path_text in sorted(files.items()):
        for source_row in _read_split_rows(Path(path_text)):
            text = str(source_row.get("Utterance", "")).strip()
            if not text:
                skipped_empty_text += 1
                continue
            labels = [
                str(source_row.get("Emotion", "")).strip().lower(),
                str(source_row.get("Sentiment", "")).strip().lower(),
            ]
            labels = [label for label in labels if label]
            label_counts.update(labels)
            expected_cues, evidence = cues_from_meld(text, labels)
            source_row_id = f"{split}_{source_row.get('Dialogue_ID', 'd')}_{source_row.get('Utterance_ID', 'u')}"
            row = build_local_research_row(
                source_tier=MELD_SOURCE_TIER,
                row_number=len(rows) + 1,
                source_row_id=source_row_id,
                split=normalize_split(split),
                text=text,
                labels=labels,
                expected_cues=expected_cues,
                evidence_spans=evidence,
            )
            errors = validate_local_research_row(row, len(rows) + 1)
            if errors:
                raise ValueError("; ".join(errors[:20]))
            rows.append(row)
    summary = aggregate_row_counts(rows)
    summary.update(
        {
            "source_tier": MELD_SOURCE_TIER,
            "label_counts": dict(sorted(label_counts.items())),
            "skipped_empty_text": skipped_empty_text,
        }
    )
    return rows, summary


def _render_report(summary: dict[str, Any], manifest_path: Path) -> str:
    split_lines = "\n".join(f"- {split}: `{count}`" for split, count in summary["split_counts"].items())
    cue_lines = "\n".join(f"- {cue}: `{count}`" for cue, count in summary["cue_counts"].items())
    label_lines = "\n".join(f"- {label}: `{count}`" for label, count in summary["label_counts"].items())
    return f"""# MELD Local Research Augmentation Report

Generated at: `{utc_now()}`

This report is aggregate-only. It intentionally includes no MELD utterance text, dialogue examples, TV-show transcript snippets, media, model artifacts, vectors, embeddings, or production inference outputs.

## Source Gate

- Source tier: `{MELD_SOURCE_TIER}`
- Manifest: `{manifest_path}`
- License metadata confirmed: `gpl-3.0`
- Use: local, text-only, non-commercial research augmentation only
- Commercial training allowed: `false`
- Production use allowed: `false`
- Audio/video used: `false`

## Counts

- Rows converted: `{summary['row_count']}`
- Skipped empty text rows: `{summary['skipped_empty_text']}`

## Split Counts

{split_lines}

## Cue Candidate Counts

{cue_lines}

## Source Label Counts

{label_lines}

## Caveat

MELD labels are weak training signals only. They are not emotion truth, Vibe gold labels, product validation, or production model-quality proof.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build local-only MELD weak cue rows for Vibe research training.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    try:
        manifest_path = Path(args.manifest)
        manifest = _load_manifest(manifest_path)
        rows, summary = build_rows(manifest)
        ensure_local_row_output_path(Path(args.out))
        write_jsonl(Path(args.out), rows)
        Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_out).write_text(_render_report(summary, manifest_path), encoding="utf-8")
    except Exception as exc:
        print(f"MELD local research row build failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "built_meld_local_research_rows",
                "rows": summary["row_count"],
                "out": str(Path(args.out)),
                "report_out": str(Path(args.report_out)),
                "aggregate_only": True,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
