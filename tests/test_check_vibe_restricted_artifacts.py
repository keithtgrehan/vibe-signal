from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_vibe_restricted_artifacts.py"


def run_checker(*paths: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_blocks_raw_chat_audio_video_transcript_paths() -> None:
    result = run_checker(
        "raw/chat.txt",
        "downloads/provider_outputs/session.json",
        "screenshots/private_chat.png",
        "audio/private-note.mp3",
        "transcripts/export.vtt",
    )

    assert result.returncode == 1
    assert "raw/chat.txt" in result.stderr
    assert "provider_outputs/session.json" in result.stderr
    assert "screenshots/private_chat.png" in result.stderr
    assert "private-note.mp3" in result.stderr
    assert "export.vtt" in result.stderr


def test_allows_safe_metadata_docs_configs_schemas_and_fixtures() -> None:
    result = run_checker(
        "docs/transcripts/policy.md",
        "configs/raw/example.yml",
        "schemas/provider_outputs.schema.json",
        "tests/fixtures/whatsapp/example.json",
        "data/vibe_gold/example_gold_labels.jsonl",
        "data/review/.gitkeep",
        "reports/.gitkeep",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed" in result.stdout


def test_staged_mode_runs_without_requiring_paths() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--staged"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode in {0, 1}
    assert "artifact check" in (result.stdout + result.stderr).lower()
