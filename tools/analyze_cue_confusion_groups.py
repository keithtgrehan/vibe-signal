#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "cue_confusion_groups.yml"
DEFAULT_RESULTS = REPO_ROOT / "reports" / "engine_eval" / "synthetic_regression_results.jsonl"
DEFAULT_SPLIT_RESULTS_ROOT = REPO_ROOT / "reports" / "engine_eval" / "splits"
DEFAULT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "cue_confusion_groups.md"
DEFAULT_SUMMARY = REPO_ROOT / "reports" / "engine_eval" / "cue_confusion_groups.json"
SPLIT_NAMES = ("dev", "hard_negative", "heldout", "red_team")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_confusion_config(path: Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    groups = payload.get("confusion_groups", {})
    if not isinstance(groups, dict):
        raise ValueError("confusion_groups config must be a mapping")
    return groups


def _read_all_split_results(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in SPLIT_NAMES:
        rows.extend(read_jsonl(root / split / "synthetic_regression_results.jsonl"))
    return rows


def analyze(rows: list[dict[str, Any]], groups: dict[str, dict[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {"result_count": len(rows), "groups": {}}
    for group_name, group in groups.items():
        cues = {str(cue) for cue in group.get("cues", [])}
        unexpected = Counter()
        missing = Counter()
        substitutions = Counter()
        cofires = Counter()
        for row in rows:
            expected = {str(cue) for cue in row.get("expected_cues", [])}
            observed = {str(cue) for cue in row.get("observed_cues", [])}
            row_unexpected = {str(cue) for cue in row.get("unexpected_cues", [])}
            row_missing = {str(cue) for cue in row.get("missing_expected_cues", [])}
            unexpected.update(cue for cue in row_unexpected if cue in cues)
            missing.update(cue for cue in row_missing if cue in cues)
            for missed in row_missing:
                if missed not in cues:
                    continue
                for predicted in row_unexpected:
                    if predicted in cues:
                        substitutions[f"{predicted}_predicted_when_{missed}_expected"] += 1
            cofire = sorted(cue for cue in observed if cue in cues)
            if len(cofire) > 1:
                cofires["+".join(cofire)] += 1
            if expected & cues and observed & cues and not row_unexpected and not row_missing:
                continue
        payload["groups"][group_name] = {
            "cues": sorted(cues),
            "unexpected_within_group": dict(sorted(unexpected.items())),
            "missing_within_group": dict(sorted(missing.items())),
            "substitutions": dict(sorted(substitutions.items())),
            "cofires": dict(sorted(cofires.items())),
            "suggested_precedence_rule": str(group.get("suggested_precedence_rule", "")),
        }
    return payload


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Cue Confusion Groups",
        "",
        "These are bootstrap-only synthetic confusion findings. They are not human-reviewed accuracy, model-quality, or production-readiness claims.",
        "",
        f"- Result rows: `{summary['result_count']}`",
        "",
    ]
    for group_name, group in sorted(summary["groups"].items()):
        lines.extend(
            [
                f"## {group_name}",
                "",
                f"- Cues: `{', '.join(group['cues'])}`",
                f"- Suggested precedence rule: {group['suggested_precedence_rule']}",
                f"- Unexpected within group: `{group['unexpected_within_group']}`",
                f"- Missing within group: `{group['missing_within_group']}`",
                f"- Substitutions: `{group['substitutions']}`",
                f"- Co-fires: `{group['cofires']}`",
                "",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze cue confusion groups from synthetic regression results.")
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--summary-out", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--all-splits", action="store_true")
    parser.add_argument("--split-results-root", default=str(DEFAULT_SPLIT_RESULTS_ROOT))
    args = parser.parse_args(argv)

    rows = _read_all_split_results(Path(args.split_results_root)) if args.all_splits else read_jsonl(Path(args.results))
    summary = analyze(rows, read_confusion_config(Path(args.config)))
    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
