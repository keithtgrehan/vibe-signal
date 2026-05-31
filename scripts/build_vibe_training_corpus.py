#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_vibe_training_sources import build_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "vibe_training_sources.example.yml"


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run Vibe corpus planning without writing training rows.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--project-mode", choices=("research_only", "commercial"), default="research_only")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--manifest-out")
    args = parser.parse_args(argv)

    if not args.dry_run:
        print("Only --dry-run is implemented; corpus row creation is blocked.", file=sys.stderr)
        return 1

    summary = build_summary(Path(args.config), args.project_mode)
    if summary["errors"]:
        print("Vibe corpus dry-run refused by rights validator:", file=sys.stderr)
        for error in summary["errors"]:
            print(f"- {error}", file=sys.stderr)
        return 1

    manifest = {
        "dry_run": True,
        "project_mode": args.project_mode,
        "source_ids": summary["training_ready_source_ids"],
        "row_count": 0,
        "corpus_created": False,
        "output_path": args.output,
    }
    if args.manifest_out:
        _write_manifest(Path(args.manifest_out), manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
