#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_vibe_training_sources import build_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "vibe_training_sources.example.yml"


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run Vibe baseline training gate without fitting or saving artifacts.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--project-mode", choices=("research_only", "commercial"), default="research_only")
    parser.add_argument("--input")
    parser.add_argument("--task", default="cue_label")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report-out")
    parser.add_argument("--model-out")
    parser.add_argument("--vector-out")
    args = parser.parse_args(argv)

    if not args.dry_run:
        print("Only --dry-run is implemented; model training is blocked.", file=sys.stderr)
        return 1

    summary = build_summary(Path(args.config), args.project_mode)
    if summary["errors"]:
        print("Vibe trainer dry-run refused by rights validator:", file=sys.stderr)
        for error in summary["errors"]:
            print(f"- {error}", file=sys.stderr)
        return 1

    report = {
        "dry_run": True,
        "status": "DRY_RUN_NO_TRAINING",
        "project_mode": args.project_mode,
        "task": args.task,
        "input": args.input,
        "trained": False,
        "model_saved": False,
        "vector_artifacts_created": False,
        "provider_calls_made": False,
        "training_ready_source_ids": summary["training_ready_source_ids"],
        "model_out": args.model_out,
        "vector_out": args.vector_out,
    }
    if args.report_out:
        _write_report(Path(args.report_out), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
