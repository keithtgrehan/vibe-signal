from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "train_research_vibe_baseline.py"


def run_trainer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_dry_run_helpful_without_input() -> None:
    result = run_trainer("--dry-run")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["dry_run"] is True
    assert payload["trained"] is False
    assert payload["model_saved"] is False


def test_non_dry_run_training_is_refused(tmp_path: Path) -> None:
    model_out = tmp_path / "models" / "baseline.pkl"
    result = run_trainer("--model-out", str(model_out))

    assert result.returncode == 1
    assert "Only --dry-run is implemented" in result.stderr
    assert not model_out.exists()


def test_dry_run_report_has_no_training_or_artifacts(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    model_out = tmp_path / "model.pkl"
    vector_out = tmp_path / "vectors.faiss"
    result = run_trainer(
        "--dry-run",
        "--report-out",
        str(report),
        "--model-out",
        str(model_out),
        "--vector-out",
        str(vector_out),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "DRY_RUN_NO_TRAINING"
    assert payload["trained"] is False
    assert payload["model_saved"] is False
    assert payload["vector_artifacts_created"] is False
    assert payload["provider_calls_made"] is False
    assert not model_out.exists()
    assert not vector_out.exists()


def test_commercial_mode_fails_closed() -> None:
    result = run_trainer("--dry-run", "--project-mode", "commercial")

    assert result.returncode == 1
    assert "commercial mode rejects rights_tier NC" in result.stderr
