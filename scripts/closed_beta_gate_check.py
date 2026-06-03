#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "docs" / "proof" / "closed_beta" / "closed_beta_gate_report.md"


def _run(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
        return {"command": " ".join(command), "status": "PASS" if completed.returncode == 0 else "FAIL", "returncode": completed.returncode, "output": completed.stdout[-2000:]}
    except Exception as exc:  # noqa: BLE001 - gate command must report bounded failures.
        return {"command": " ".join(command), "status": "FAIL", "returncode": None, "output": exc.__class__.__name__}


def _exists(path: str) -> bool:
    return (REPO_ROOT / path).exists()


def build_gate_summary(*, deploy_status: str = "unverified") -> dict[str, Any]:
    scanner_results = {
        "public_copy_scanner": _run([sys.executable, "scripts/check_public_copy_safety.py"]),
        "no_raw_content_scanner": _run([sys.executable, "scripts/check_no_raw_content_leaks.py"]),
        "restricted_artifact_scanner": _run([sys.executable, "scripts/check_vibe_restricted_artifacts.py", "--staged"]),
    }
    gates: dict[str, dict[str, str]] = {
        "safety_scanners": {
            "status": "PASS" if all(row["status"] == "PASS" for row in scanner_results.values()) else "FAIL",
            "notes": "Public-copy and no-raw-content scanners run by this gate.",
        },
        "restricted_artifacts": {
            "status": scanner_results["restricted_artifact_scanner"]["status"],
            "notes": "Restricted-artifact scanner result for staged changes.",
        },
        "synthetic_regression_report": {
            "status": "PASS" if _exists("reports/engine_eval/10k_precision_hardening_comparison.md") else "FAIL",
            "notes": "10k synthetic regression hardening report presence check.",
        },
        "human_reviewed_labels": {
            "status": "MANUAL_REQUIRED",
            "notes": "Human-reviewed labels are pending; bootstrap labels do not unlock this gate.",
        },
        "legal_privacy_review": {
            "status": "MANUAL_REQUIRED",
            "notes": "Legal/privacy packet exists for human review; approval is not claimed.",
        },
        "real_device_qa": {
            "status": "MANUAL_REQUIRED",
            "notes": "Real-device iPhone/TestFlight QA evidence is required before invites.",
        },
        "deployed_backend_version": {
            "status": "PASS" if deploy_status == "current" else "MANUAL_REQUIRED",
            "notes": f"Deploy metadata status: {deploy_status}.",
        },
        "metadata_only_monitoring": {
            "status": "PASS" if _exists("docs/proof/closed_beta/metadata_only_monitoring_gate.md") else "FAIL",
            "notes": "Structured metadata-only monitoring contract and docs.",
        },
    }
    blocking_statuses = {row["status"] for row in gates.values()}
    invite_decision = "ALLOWED" if blocking_statuses <= {"PASS"} else "BLOCKED"
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "gates": gates,
        "scanner_results": scanner_results,
        "tester_invite_decision": invite_decision,
        "non_claims": [
            "This is not production-readiness approval.",
            "This is not legal/privacy approval.",
            "This is not human-reviewed model validation.",
        ],
    }


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Closed-Beta Gate Report",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        f"Final tester invite decision: `{summary['tester_invite_decision']}`",
        "",
        "## Gate Matrix",
        "",
        "| Gate | Status | Notes |",
        "| --- | --- | --- |",
    ]
    for name, gate in summary["gates"].items():
        lines.append(f"| `{name}` | `{gate['status']}` | {gate['notes']} |")
    lines.extend(
        [
            "",
            "## Scanner Results",
            "",
        ]
    )
    for name, result in summary["scanner_results"].items():
        lines.append(f"- `{name}`: `{result['status']}` via `{result['command']}`")
    lines.extend(
        [
            "",
            "## Decision Rule",
            "",
            "Tester invites remain `BLOCKED` unless real-device QA evidence exists, legal/privacy review is completed by a human reviewer, deployed backend metadata proves the intended commit, P0 metadata-only monitoring is accepted, and safety scanners pass.",
            "",
            "This report does not claim production launch, App Store release, legal/GDPR compliance, human-reviewed validation, or real-world accuracy.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the Vibe Signal closed-beta release gate report.")
    parser.add_argument("--deploy-status", choices=("current", "stale", "unverified"), default="unverified")
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    summary = build_gate_summary(deploy_status=args.deploy_status)
    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(summary), encoding="utf-8")
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(build_report(summary))
    has_failed_gate = any(gate["status"] == "FAIL" for gate in summary["gates"].values())
    has_failed_scanner = any(result["status"] == "FAIL" for result in summary["scanner_results"].values())
    return 1 if has_failed_gate or has_failed_scanner else 0


if __name__ == "__main__":
    raise SystemExit(main())
