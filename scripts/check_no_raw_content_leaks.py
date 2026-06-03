#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_PATHS = (
    "backend",
    "src",
    "scripts",
    "tools",
    "mobile/src",
    "mobile/scripts",
    "web/src",
    "docs/proof",
    "reports",
)
TEXT_SUFFIXES = {".py", ".js", ".jsx", ".mjs", ".md", ".json", ".jsonl", ".yml", ".yaml"}
SAFE_CONSOLE_FILES = {"mobile/scripts/verify_backend_event_acceptance.mjs"}
SAFE_PATTERN_LINES: set[tuple[str, str, str]] = {
    (
        "scripts/smoke_test_deployed_backend.py",
        "feedback_comment_hash",
        'if "comment_sha256" in stored_feedback:',
    ),
}
RISK_PATTERNS: dict[str, str] = {
    "feedback_comment_hash": r"\bcomment_sha256\b|\b_hash_text\(",
    "python_logs_raw_payload": r"\b(?:print|logger\.(?:debug|info|warning|error|exception)|LOGGER\.(?:debug|info|warning|error|exception))\s*\([^\\n]*(?:payload|messages|comment|body|raw_text|request\.body|response\.text|private|secret)",
    "js_console_raw_payload": r"\bconsole\.(?:log|warn|error|info)\s*\([^\\n]*(?:payload|messages|comment|body|rawText|raw_text|responseText|private|secret)",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    pattern_id: str
    excerpt: str


def _iter_paths(paths: list[str] | None = None) -> list[Path]:
    selected: list[Path] = []
    for raw in paths or list(SCAN_PATHS):
        path = (REPO_ROOT / raw).resolve()
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            selected.append(path)
        elif path.is_dir():
            selected.extend(item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in TEXT_SUFFIXES)
    return sorted(set(selected))


def scan_paths(paths: list[str] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_paths(paths):
        try:
            rel = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if rel in SAFE_CONSOLE_FILES and "console.log" in line:
                continue
            for pattern_id, pattern in RISK_PATTERNS.items():
                if rel == "scripts/check_no_raw_content_leaks.py" and pattern_id == "feedback_comment_hash":
                    continue
                if (rel, pattern_id, line.strip()) in SAFE_PATTERN_LINES:
                    continue
                if re.search(pattern, line, flags=re.IGNORECASE):
                    findings.append(Finding(rel, line_number, pattern_id, line.strip()[:180]))
    return findings


def build_summary(findings: list[Finding]) -> dict[str, Any]:
    return {
        "status": "pass" if not findings else "fail",
        "finding_count": len(findings),
        "findings": [finding.__dict__ for finding in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check for raw Vibe content leakage in logs, feedback metadata, reports, and scripts.")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    summary = build_summary(scan_paths(args.paths or None))
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if summary["status"] != "pass":
        print(f"No-raw-content leak check failed: {summary['finding_count']} finding(s).", file=sys.stderr)
        for finding in summary["findings"]:
            print(f"- {finding['path']}:{finding['line']} {finding['pattern_id']}: {finding['excerpt']}", file=sys.stderr)
        return 1
    print("No-raw-content leak check passed: 0 finding(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
