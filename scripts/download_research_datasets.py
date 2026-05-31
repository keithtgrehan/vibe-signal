#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_vibe_training_sources import is_research_training_ready, read_structured, source_rows, validate_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "vibe_training_sources.example.yml"


def _select_rows(rows: list[dict[str, Any]], source_id: str | None, all_approved_research: bool) -> list[dict[str, Any]]:
    if source_id:
        return [row for row in rows if row.get("source_id") == source_id]
    if all_approved_research:
        return [row for row in rows if is_research_training_ready(row)]
    return []


def _write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run Vibe research source access without fetching raw rows.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--project-mode", choices=("research_only", "commercial"), default="research_only")
    parser.add_argument("--source-id")
    parser.add_argument("--all-approved-research", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cache-dir", default="data/external")
    parser.add_argument("--manifest-out")
    args = parser.parse_args(argv)

    if not args.dry_run:
        print("Only --dry-run is implemented; real source download is blocked.", file=sys.stderr)
        return 1

    rows = source_rows(read_structured(Path(args.config)))
    selected = _select_rows(rows, args.source_id, args.all_approved_research)
    if args.source_id and not selected:
        print(f"source_id {args.source_id!r} was not found in the registry.", file=sys.stderr)
        return 1
    if not selected:
        print("No approved research-only sources were selected.", file=sys.stderr)
        return 1

    errors = validate_rows(selected, args.project_mode)
    if errors:
        print("Vibe dry-run source access refused by rights validator:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    not_approved = [row["source_id"] for row in selected if not is_research_training_ready(row)]
    if args.project_mode == "research_only" and not_approved:
        print(f"Selected source is not approved for download dry-run: {', '.join(not_approved)}", file=sys.stderr)
        return 1

    manifest = {
        "dry_run": True,
        "project_mode": args.project_mode,
        "selected_source_ids": [row["source_id"] for row in selected],
        "downloaded": False,
        "raw_data_committed": False,
        "cache_dir": args.cache_dir,
        "cache_dir_created": False,
    }
    if args.manifest_out:
        _write_manifest(Path(args.manifest_out), manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
