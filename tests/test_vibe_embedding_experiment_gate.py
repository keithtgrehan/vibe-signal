from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_vibe_embedding_match_experiment.py"
CORPUS = ROOT / "data" / "vibe_matching" / "synthetic" / "synthetic_match_pairs.jsonl"


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_embedding_experiment_writes_skipped_report_without_local_model(tmp_path: Path) -> None:
    report = tmp_path / "embedding_experiment.json"
    markdown = tmp_path / "embedding_experiment.md"
    result = run_script(
        "--input",
        str(CORPUS),
        "--model-name",
        "sentence-transformers/not-a-real-local-model",
        "--json-out",
        str(report),
        "--markdown-out",
        str(markdown),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "SKIPPED"
    assert payload["provider_calls_made"] is False
    assert payload["model_downloaded"] is False
    assert payload["dataset_downloaded"] is False
    assert "No production claims" in markdown.read_text(encoding="utf-8")


def test_embedding_experiment_rejects_input_outside_synthetic_tree(tmp_path: Path) -> None:
    copied = tmp_path / "pairs.jsonl"
    copied.write_text(CORPUS.read_text(encoding="utf-8"), encoding="utf-8")

    result = run_script("--input", str(copied), "--json-out", str(tmp_path / "report.json"))

    assert result.returncode == 1
    assert "must be under data/vibe_matching/synthetic" in result.stderr
