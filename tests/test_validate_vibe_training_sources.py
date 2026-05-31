from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_vibe_training_sources.py"
EXAMPLE = ROOT / "configs" / "vibe_training_sources.example.yml"


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--path", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_example() -> dict:
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


def test_training_sources_example_validates() -> None:
    result = run_validator(EXAMPLE)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed" in result.stdout


def test_external_dataset_raw_body_fails(tmp_path: Path) -> None:
    payload = load_example()
    payload["sources"][0]["raw_body_allowed"] = True
    payload["sources"][0]["metadata_only"] = False
    path = tmp_path / "raw_allowed.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "external research dataset cannot allow raw_body_allowed by default" in result.stdout


def test_training_yes_without_explicit_notes_fails(tmp_path: Path) -> None:
    payload = load_example()
    payload["sources"][1]["allowed_training_use"] = "yes"
    payload["sources"][1]["notes"] = ""
    path = tmp_path / "training_yes.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "training yes requires explicit approval notes" in result.stdout


def test_metadata_raw_conflict_blocked_use_and_unsafe_safe_use_fail(tmp_path: Path) -> None:
    payload = load_example()
    row = payload["sources"][2]
    row["raw_body_allowed"] = True
    row["metadata_only"] = True
    row["blocked_vibe_use"] = []
    row["safe_vibe_use"] = ["infer true emotion from text"]
    path = tmp_path / "bad_use.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "metadata_only cannot also allow raw_body_allowed" in result.stdout
    assert "blocked_vibe_use cannot be empty" in result.stdout
    assert "safe_vibe_use implies a disallowed claim" in result.stdout
