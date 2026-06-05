#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ALLOWLIST = REPO_ROOT / "configs" / "public_copy_safety_allowlist.yml"
DEFAULT_SCAN_PATHS = (
    "README.md",
    "web/src/App.jsx",
    "web/src/api.js",
    "web/src/resultViewModel.js",
    "web/src/trustContent.js",
    "web/index.html",
    "web/public/opengraph.svg",
    "mobile/src/screens/VibeSignalApp.js",
    "mobile/src/screens/ProviderSettingsScreen.js",
    "mobile/src/screens/providerScreenModel.js",
    "mobile/src/screens/matchScreenModel.js",
    "mobile/src/components/paywallViewModel.js",
    "backend/routes/legal.py",
    "backend/routes/analyze.py",
    "docs/privacy_policy_draft.md",
    "docs/terms_draft.md",
    "docs/data_deletion_request_draft.md",
    "docs/data_export_request_draft.md",
    "docs/match_usage_consent_disclaimer.md",
    "docs/closed_beta_tester_instructions.md",
    "docs/ios/app_review_notes.md",
    "docs/ios/beta_tester_instructions.md",
    "docs/ios/testflight_metadata.md",
)
BLOCKED_PATTERNS: dict[str, str] = {
    "secretly": r"\bsecretly\b",
    "they_like_you": r"\bthey\s+like\s+you\b",
    "hidden_intent": r"\bhidden\s+intent\b",
    "cheating_detector": r"\b(?:cheating\s+detector|detects?\s+cheating|catch(?:es)?\s+cheating)\b",
    "lying_or_lies": r"\b(?:lying|detects?\s+lies?|lie\s+detector)\b",
    "diagnose": r"\bdiagnos(?:e|es|is|ing)\b",
    "narcissist": r"\bnarcissist(?:ic)?\b",
    "attachment_style": r"\battachment\s+style\b",
    "autism": r"\bautis(?:m|tic)\b",
    "adhd": r"\badhd\b",
    "manipulate": r"\bmanipulat(?:e|es|ing|ion|ive)\b",
    "make_them": r"\bmake\s+them\b",
    "win_them_back": r"\bwin\s+them\s+back\b",
    "guaranteed": r"\bguaranteed\b",
    "this_proves": r"\bthis\s+proves\b",
    "emotional_truth": r"\bemotional\s+truth\b",
    "find_out_think": r"\bfind\s+out\s+what\s+they\s+really\s+think\b",
    "decode_true_feelings": r"\bdecode\s+their\s+true\s+feelings\b",
    "rizz": r"\brizz\b",
    "dating_wingman": r"\bdating\s+wingman\b",
}
ALLOWED_NEGATED_PUBLIC_COPY_PHRASES = (
    "Built for clarity, not manipulation",
    "Whether someone is cheating",
    "Whether someone is lying",
    "What someone secretly means",
    "Someone’s diagnosis, attachment style, neurotype, or personality",
    "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
    "Prohibited use includes stalking, harassment, coercion, manipulation, or trying to make someone respond.",
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    pattern_id: str
    excerpt: str
    allowlisted: bool = False
    reason: str = ""


def _load_allowlist(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = payload.get("allow", [])
    if not isinstance(rows, list):
        raise ValueError("public copy allowlist must contain an allow list")
    normalized: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict) or not row.get("path") or not row.get("reason"):
            raise ValueError("each public copy allowlist row needs path and reason")
        normalized.append({"path": str(row["path"]), "reason": str(row["reason"])})
    return normalized


def _is_allowlisted(path: str, allowlist: list[dict[str, str]]) -> tuple[bool, str]:
    for row in allowlist:
        if fnmatch.fnmatch(path, row["path"]):
            return True, row["reason"]
    return False, ""


def _strip_allowed_negated_copy(line: str) -> str:
    cleaned = line
    for phrase in ALLOWED_NEGATED_PUBLIC_COPY_PHRASES:
        cleaned = cleaned.replace(phrase, "")
    return cleaned


def _iter_paths(paths: list[str]) -> list[Path]:
    selected: list[Path] = []
    for raw in paths:
        path = (REPO_ROOT / raw).resolve()
        if path.is_file():
            selected.append(path)
        elif path.is_dir():
            selected.extend(
                item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in {".md", ".py", ".js", ".jsx", ".html", ".svg"}
            )
    return sorted(set(selected))


def scan_paths(paths: list[str] | None = None, *, allowlist_path: Path = DEFAULT_ALLOWLIST) -> list[Finding]:
    allowlist = _load_allowlist(allowlist_path)
    selected = _iter_paths(paths or list(DEFAULT_SCAN_PATHS))
    findings: list[Finding] = []
    for path in selected:
        try:
            rel = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        allowed, reason = _is_allowlisted(rel, allowlist)
        for line_number, line in enumerate(text.splitlines(), start=1):
            line_for_scan = _strip_allowed_negated_copy(line)
            for pattern_id, pattern in BLOCKED_PATTERNS.items():
                if re.search(pattern, line_for_scan, flags=re.IGNORECASE):
                    findings.append(
                        Finding(
                            path=rel,
                            line=line_number,
                            pattern_id=pattern_id,
                            excerpt=line.strip()[:180],
                            allowlisted=allowed,
                            reason=reason,
                        )
                    )
    return findings


def build_summary(findings: list[Finding]) -> dict[str, Any]:
    unallowed = [finding for finding in findings if not finding.allowlisted]
    return {
        "status": "pass" if not unallowed else "fail",
        "finding_count": len(findings),
        "unallowed_count": len(unallowed),
        "allowlisted_count": len(findings) - len(unallowed),
        "findings": [finding.__dict__ for finding in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check public Vibe Signal copy for unsafe relationship/product claims.")
    parser.add_argument("paths", nargs="*", help="Optional repo-relative files/directories. Defaults to public surfaces.")
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST))
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    summary = build_summary(scan_paths(args.paths or None, allowlist_path=Path(args.allowlist)))
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if summary["status"] != "pass":
        print(f"Public copy safety check failed: {summary['unallowed_count']} unallowlisted finding(s).", file=sys.stderr)
        for finding in summary["findings"]:
            if finding["allowlisted"]:
                continue
            print(f"- {finding['path']}:{finding['line']} {finding['pattern_id']}: {finding['excerpt']}", file=sys.stderr)
        return 1
    print(
        f"Public copy safety check passed: {summary['finding_count']} finding(s), "
        f"{summary['allowlisted_count']} allowlisted, 0 unallowlisted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
