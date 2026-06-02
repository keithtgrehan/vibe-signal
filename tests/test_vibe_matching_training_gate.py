from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAINER = ROOT / "scripts" / "train_vibe_matching_baseline.py"
EVALUATOR = ROOT / "scripts" / "evaluate_vibe_matching_baseline.py"
SOURCES_VALIDATOR = ROOT / "scripts" / "validate_vibe_training_sources.py"
CORPUS = ROOT / "data" / "vibe_matching" / "synthetic" / "synthetic_match_pairs.jsonl"
CONFIG = ROOT / "configs" / "vibe_training_sources.example.yml"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_training_sources_mark_only_synthetic_matching_as_training_ready() -> None:
    result = run_script(SOURCES_VALIDATOR, "--config", str(CONFIG), "--project-mode", "research_only", "--json-out", "/tmp/vibe_training_sources_test.json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(Path("/tmp/vibe_training_sources_test.json").read_text(encoding="utf-8"))
    assert payload["training_ready_source_ids"] == ["synthetic_vibe_matching"]


def test_research_only_training_runs_on_synthetic_corpus(tmp_path: Path) -> None:
    report = tmp_path / "baseline_eval.json"
    markdown = tmp_path / "baseline_eval.md"
    result = run_script(
        TRAINER,
        "--input",
        str(CORPUS),
        "--project-mode",
        "research_only",
        "--report-out",
        str(report),
        "--markdown-out",
        str(markdown),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "trained"
    assert payload["project_mode"] == "research_only"
    assert payload["row_count"] >= 150
    assert payload["provider_calls_made"] is False
    assert payload["model_artifacts_saved"] is False
    assert payload["source_id"] == "synthetic_vibe_matching"
    assert payload["split"]["strategy"] == "template_category_holdout"
    assert payload["split"]["test_template_categories"]
    assert payload["benchmark_scope"] == "synthetic_fixture_template_holdout"
    assert payload["production_claims"] is False
    assert payload["public_quality_claims_supported"] is False
    assert "hidden_intent" in payload["blocked_claims"]
    assert "communication_fit" in payload["metrics_by_label"]
    markdown_text = markdown.read_text(encoding="utf-8")
    assert "Synthetic-only" in markdown_text
    assert "Template-category holdout" in markdown_text


def test_commercial_training_fails_closed(tmp_path: Path) -> None:
    result = run_script(
        TRAINER,
        "--input",
        str(CORPUS),
        "--project-mode",
        "commercial",
        "--report-out",
        str(tmp_path / "report.json"),
    )

    assert result.returncode == 1
    assert "commercial mode is blocked" in result.stderr.lower()


def test_training_rejects_input_outside_synthetic_matching_tree(tmp_path: Path) -> None:
    copied = tmp_path / "synthetic_match_pairs.jsonl"
    copied.write_text(CORPUS.read_text(encoding="utf-8"), encoding="utf-8")

    result = run_script(
        TRAINER,
        "--input",
        str(copied),
        "--project-mode",
        "research_only",
    )

    assert result.returncode == 1
    assert "must be under data/vibe_matching/synthetic" in result.stderr


def test_evaluator_writes_markdown_from_baseline_report(tmp_path: Path) -> None:
    report = tmp_path / "baseline_eval.json"
    markdown = tmp_path / "baseline_eval.md"
    train = run_script(
        TRAINER,
        "--input",
        str(CORPUS),
        "--project-mode",
        "research_only",
        "--report-out",
        str(report),
    )
    evaluate = run_script(
        EVALUATOR,
        "--report",
        str(report),
        "--markdown-out",
        str(markdown),
    )

    assert train.returncode == 0, train.stdout + train.stderr
    assert evaluate.returncode == 0, evaluate.stdout + evaluate.stderr
    assert "Vibe Matching Baseline Evaluation" in markdown.read_text(encoding="utf-8")
