#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = REPO_ROOT / "reports" / "engine_eval" / "api_regression_results.jsonl"
DEFAULT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "false_positive_analysis.md"
DEFAULT_BACKLOG = REPO_ROOT / "reports" / "engine_eval" / "cue_improvement_backlog.md"
DEFAULT_SPLIT_RESULTS_ROOT = REPO_ROOT / "reports" / "engine_eval" / "splits"
SPLIT_NAMES = ("dev", "hard_negative", "heldout", "red_team")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_all_split_results(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in SPLIT_NAMES:
        path = root / split / "synthetic_regression_results.jsonl"
        if path.exists():
            rows.extend(read_jsonl(path))
    return rows


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    missing = Counter()
    unexpected = Counter()
    low_signal_failures: list[str] = []
    evidence_missing: list[str] = []
    unsafe_hits: list[str] = []
    for row in rows:
        missing.update(str(cue) for cue in row.get("missing_expected_cues", []))
        unexpected.update(str(cue) for cue in row.get("unexpected_cues", []))
        if row.get("low_signal_correct") is False:
            low_signal_failures.append(str(row.get("fixture_id", "")))
        if row.get("evidence_complete") is False:
            evidence_missing.append(str(row.get("fixture_id", "")))
        if row.get("unsafe_output_hits"):
            unsafe_hits.append(str(row.get("fixture_id", "")))
    return {
        "result_count": len(rows),
        "top_missing_cues": missing.most_common(20),
        "top_unexpected_cues": unexpected.most_common(20),
        "low_signal_failure_count": len(low_signal_failures),
        "low_signal_failures": low_signal_failures[:50],
        "evidence_missing_count": len(evidence_missing),
        "evidence_missing_cases": evidence_missing[:50],
        "unsafe_output_hit_count": len(unsafe_hits),
        "unsafe_output_cases": unsafe_hits[:50],
    }


def build_report(summary: dict[str, Any]) -> str:
    missing_lines = [f"- `{cue}`: `{count}`" for cue, count in summary["top_missing_cues"]] or ["- None"]
    unexpected_lines = [f"- `{cue}`: `{count}`" for cue, count in summary["top_unexpected_cues"]] or ["- None"]
    return "\n".join(
        [
            "# Cue False-Positive / False-Negative Analysis",
            "",
            "Status: synthetic API regression analysis only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, or diagnosis.",
            "",
            f"- API result rows: `{summary['result_count']}`",
            f"- Low-signal failures: `{summary['low_signal_failure_count']}`",
            f"- Evidence missing cases: `{summary['evidence_missing_count']}`",
            f"- Unsafe-output hits: `{summary['unsafe_output_hit_count']}`",
            "",
            "## Top Missing Expected Cues",
            "",
            *missing_lines,
            "",
            "## Top Unexpected Cues",
            "",
            *unexpected_lines,
            "",
        ]
    )


def build_backlog(summary: dict[str, Any]) -> str:
    lines = [
        "# Cue Improvement Backlog",
        "",
        "This backlog is generated from synthetic API regression findings. It is not an accuracy claim.",
        "",
    ]
    if summary["top_missing_cues"]:
        lines.extend(
            [
                "## Candidate False Negatives",
                "",
                "- Decide whether `/api/analyze` should expose match-specific cues such as answer evasion, specificity drop, contradiction, and unsupported claim shifts.",
                "- Add API-level evidence spans before treating any missing cue as an engine bug.",
                "",
            ]
        )
    if summary["top_unexpected_cues"]:
        lines.extend(
            [
                "## Candidate False Positives",
                "",
                "- Review high-frequency unexpected cues for overly broad regexes or expected-fixture metadata gaps.",
                "- Keep urgency separate from pressure and ambiguity separate from hidden motive claims.",
                "",
            ]
        )
    if summary["low_signal_failure_count"]:
        lines.extend(["## Low-Signal", "", "- Tighten low-signal handling for short/context-light synthetic cases.", ""])
    lines.extend(
        [
            "## Next Fixture Types",
            "",
            "- Direct ask without deadline.",
            "- Deadline without pressure.",
            "- Reassurance without identity or anxiety labels.",
            "- Commitment change with explicit explanation.",
            "- Topic shift that is normal rather than evasive.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze synthetic API regression cue false positives and false negatives.")
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--backlog-out", default=str(DEFAULT_BACKLOG))
    parser.add_argument("--all-splits", action="store_true")
    parser.add_argument("--split-results-root", default=str(DEFAULT_SPLIT_RESULTS_ROOT))
    args = parser.parse_args(argv)

    if args.all_splits:
        rows = read_all_split_results(Path(args.split_results_root))
        if args.report_out == str(DEFAULT_REPORT):
            args.report_out = str(REPO_ROOT / "reports" / "engine_eval" / "false_positive_analysis_10k.md")
        if args.backlog_out == str(DEFAULT_BACKLOG):
            args.backlog_out = str(REPO_ROOT / "reports" / "engine_eval" / "next_engine_improvement_backlog.md")
    else:
        rows = read_jsonl(Path(args.results))
    summary = analyze(rows)
    report_path = Path(args.report_out)
    backlog_path = Path(args.backlog_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(summary), encoding="utf-8")
    backlog_path.parent.mkdir(parents=True, exist_ok=True)
    backlog_path.write_text(build_backlog(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
