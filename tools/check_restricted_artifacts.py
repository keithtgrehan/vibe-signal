#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_vibe_restricted_artifacts import find_restricted, staged_paths  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compatibility wrapper for Vibe restricted-artifact checks.")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Check the selected paths without changing git state.")
    parser.add_argument("--cwd", default=".")
    args = parser.parse_args(argv)

    paths = list(args.paths)
    if args.staged or not paths:
        paths = staged_paths(Path(args.cwd))

    flagged = find_restricted(paths)
    if flagged:
        print("Vibe restricted artifact check failed. Raw personal data or model/data artifacts must stay out of git:", file=sys.stderr)
        for path in flagged:
            print(f"- {path}", file=sys.stderr)
        return 1
    mode = "dry-run" if args.dry_run else "checked"
    print(f"Vibe restricted artifact check passed ({mode}): {len(paths)} path(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
