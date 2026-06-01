#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vibesignal_ai.matching.model_io import render_baseline_markdown  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render Vibe matching baseline evaluation reports.")
    parser.add_argument("--report", required=True)
    parser.add_argument("--markdown-out", required=True)
    args = parser.parse_args(argv)

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    out = Path(args.markdown_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_baseline_markdown(report), encoding="utf-8")
    print(json.dumps({"status": "written", "markdown_out": str(out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
