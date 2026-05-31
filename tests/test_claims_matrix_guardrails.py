from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_claims_matrix.py"
EXAMPLE = ROOT / "configs" / "claims_matrix.example.yml"


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


def test_claims_matrix_example_validates() -> None:
    result = run_validator(EXAMPLE)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed" in result.stdout


def test_supported_claim_cannot_use_red_line_terms(tmp_path: Path) -> None:
    payload = load_example()
    payload["claims"][0]["claim_text"] = "This detects deception from replies."
    path = tmp_path / "bad_claims.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "supported/gated claim contains disallowed term" in result.stdout


def test_statistical_significance_requires_explicit_gate(tmp_path: Path) -> None:
    payload = load_example()
    payload["claims"][3]["claim_text"] = "Future reviewer study may discuss statistical significance."
    path = tmp_path / "stats_claims.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "statistical-significance language requires explicit gate" in result.stdout


def test_duplicate_claim_id_fails(tmp_path: Path) -> None:
    payload = load_example()
    payload["claims"][1]["claim_id"] = payload["claims"][0]["claim_id"]
    path = tmp_path / "duplicate.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "duplicate claim_id" in result.stdout
