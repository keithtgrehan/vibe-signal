from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_vibe_resource_registry.py"
EXAMPLE = ROOT / "configs" / "vibe_resource_registry.example.yml"


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


def test_example_registry_validates() -> None:
    result = run_validator(EXAMPLE)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed" in result.stdout


def test_unknown_or_empty_rights_fail_closed(tmp_path: Path) -> None:
    payload = load_example()
    payload["resources"][0]["rights_tier"] = ""
    path = tmp_path / "empty_rights.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "invalid rights_tier" in result.stdout


def test_duplicate_source_id_fails(tmp_path: Path) -> None:
    payload = load_example()
    payload["resources"][1]["source_id"] = payload["resources"][0]["source_id"]
    path = tmp_path / "duplicate.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "duplicate source_id" in result.stdout


def test_restricted_source_cannot_allow_raw_commit_training_or_eval(tmp_path: Path) -> None:
    payload = load_example()
    row = payload["resources"][0]
    row["rights_tier"] = "restricted"
    row["raw_body_allowed"] = True
    row["allowed_commit"] = True
    row["allowed_training_use"] = "yes"
    row["allowed_eval_use"] = "benchmark_only"
    path = tmp_path / "restricted_bad.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "restricted source cannot allow raw_body_allowed" in result.stdout
    assert "restricted source cannot allow commit" in result.stdout
    assert "restricted source cannot allow training/eval" in result.stdout


def test_malformed_boolean_metadata_conflict_and_pending_hash_fail(tmp_path: Path) -> None:
    payload = load_example()
    row = payload["resources"][0]
    row["metadata_only"] = "false"
    row["raw_body_allowed"] = True
    row["provenance_hash"] = "pending"
    path = tmp_path / "bad_booleans.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "malformed boolean metadata_only" in result.stdout
    assert "provenance_hash" in result.stdout
