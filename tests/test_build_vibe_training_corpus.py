from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_vibe_training_corpus.py"


def run_builder(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_dry_run_builds_manifest_without_corpus_rows(tmp_path: Path) -> None:
    manifest = tmp_path / "corpus_manifest.json"
    out = tmp_path / "corpus.jsonl"
    result = run_builder(
        "--project-mode",
        "research_only",
        "--dry-run",
        "--output",
        str(out),
        "--manifest-out",
        str(manifest),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["dry_run"] is True
    assert payload["project_mode"] == "research_only"
    assert payload["row_count"] == 0
    assert payload["corpus_created"] is False
    assert payload["source_ids"] == ["synthetic_vibe_matching"]
    assert not out.exists()


def test_non_dry_run_corpus_creation_is_refused(tmp_path: Path) -> None:
    out = tmp_path / "derived" / "corpus.jsonl"
    result = run_builder(
        "--project-mode",
        "research_only",
        "--output",
        str(out),
    )

    assert result.returncode == 1
    assert "Only --dry-run is implemented" in result.stderr
    assert not out.exists()


def test_commercial_mode_blocks_research_only_sources(tmp_path: Path) -> None:
    result = run_builder(
        "--project-mode",
        "commercial",
        "--dry-run",
        "--manifest-out",
        str(tmp_path / "manifest.json"),
    )

    assert result.returncode == 1
    assert "commercial mode rejects rights_tier NC" in result.stderr
