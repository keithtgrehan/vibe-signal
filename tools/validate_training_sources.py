#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_vibe_training_sources import main as validate_main  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and not args[0].startswith("-"):
        args = ["--config", args[0], *args[1:]]
    return validate_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
