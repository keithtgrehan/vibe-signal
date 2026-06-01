from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "download_research_datasets.py"


def run_downloader(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_dry_run_all_approved_research_writes_manifest_metadata(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    manifest = tmp_path / "download_manifest.json"
    result = run_downloader(
        "--all-approved-research",
        "--project-mode",
        "research_only",
        "--dry-run",
        "--cache-dir",
        str(cache_dir),
        "--manifest-out",
        str(manifest),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["dry_run"] is True
    assert payload["project_mode"] == "research_only"
    assert payload["selected_source_ids"] == ["synthetic_vibe_matching"]
    assert payload["downloaded"] is False
    assert payload["raw_data_committed"] is False
    assert payload["cache_dir_created"] is False
    assert not cache_dir.exists()


def test_non_dry_run_download_is_refused(tmp_path: Path) -> None:
    result = run_downloader(
        "--source-id",
        "dailydialog",
        "--project-mode",
        "research_only",
        "--cache-dir",
        str(tmp_path / "cache"),
    )

    assert result.returncode == 1
    assert "Only --dry-run is implemented" in result.stderr


def test_commercial_mode_refuses_nc_source(tmp_path: Path) -> None:
    result = run_downloader(
        "--source-id",
        "dailydialog",
        "--project-mode",
        "commercial",
        "--dry-run",
        "--cache-dir",
        str(tmp_path / "cache"),
    )

    assert result.returncode == 1
    assert "commercial mode rejects rights_tier NC" in result.stderr


def test_restricted_or_manual_review_source_is_refused(tmp_path: Path) -> None:
    result = run_downloader(
        "--source-id",
        "meld",
        "--project-mode",
        "research_only",
        "--dry-run",
        "--cache-dir",
        str(tmp_path / "cache"),
    )

    assert result.returncode == 1
    assert "not approved for download dry-run" in result.stderr
