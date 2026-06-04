from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.check_vibe_restricted_artifacts import find_restricted


ROOT = Path(__file__).resolve().parents[1]


def test_private_whatsapp_tree_is_gitignored() -> None:
    result = subprocess.run(
        ["git", "check-ignore", "-q", "data/restricted/private_whatsapp/processed/private_messages_redacted.jsonl"],
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0


def test_restricted_scanner_blocks_private_whatsapp_artifacts_by_path() -> None:
    flagged = find_restricted(
        [
            "data/restricted/private_whatsapp/raw/export.txt",
            "data/restricted/private_whatsapp/processed/private_messages.jsonl",
            "data/restricted/private_whatsapp/reports/whatsapp_dynamics_report.json",
            "data/restricted/private_whatsapp/models/private_dynamics_baseline.pkl",
        ]
    )

    assert flagged == [
        "data/restricted/private_whatsapp/raw/export.txt",
        "data/restricted/private_whatsapp/processed/private_messages.jsonl",
        "data/restricted/private_whatsapp/reports/whatsapp_dynamics_report.json",
        "data/restricted/private_whatsapp/models/private_dynamics_baseline.pkl",
    ]


def test_synthetic_private_inspired_fixture_path_is_allowed() -> None:
    assert find_restricted(["data/synthetic/private_inspired/dynamics_fixtures.jsonl"]) == []
