from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_vibe_training_sources.py"
DOWNLOADER = ROOT / "scripts" / "download_research_datasets.py"
BUILDER = ROOT / "scripts" / "build_vibe_training_corpus.py"
TRAINER = ROOT / "scripts" / "train_research_vibe_baseline.py"
EXAMPLE = ROOT / "configs" / "vibe_training_sources.example.yml"
REQUIRED_FIELDS = {
    "source_id",
    "name",
    "modality",
    "task",
    "license_name",
    "license_url",
    "download_method",
    "access_notes",
    "training_use_allowed",
    "commercial_use_allowed",
    "research_only",
    "rights_tier",
    "safe_vibe_use",
    "blocked_vibe_use",
    "registry_status",
    "notes",
}


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_validator(path: Path, *, project_mode: str = "research_only") -> subprocess.CompletedProcess[str]:
    return run_script(VALIDATOR, "--config", str(path), "--project-mode", project_mode)


def load_example() -> dict:
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


def write_subset(tmp_path: Path, *source_ids: str) -> Path:
    rows = [row for row in load_example()["sources"] if row["source_id"] in source_ids]
    path = tmp_path / "subset.yml"
    path.write_text(yaml.safe_dump({"sources": rows}, sort_keys=False), encoding="utf-8")
    return path


def test_valid_research_only_config_passes() -> None:
    payload = load_example()

    assert payload["sources"]
    assert all(REQUIRED_FIELDS <= set(row) for row in payload["sources"])
    result = run_validator(EXAMPLE, project_mode="research_only")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "validation passed" in result.stdout
    assert "1 research training-ready source" in result.stdout


def test_validator_accepts_closed_beta_mode_alias() -> None:
    result = run_script(VALIDATOR, "--config", str(EXAMPLE), "--mode", "research")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "project_mode=research_only" in result.stdout


def test_validator_rejects_private_or_tester_chat_training_sources(tmp_path: Path) -> None:
    payload = load_example()
    synthetic = next(row for row in payload["sources"] if row["source_id"] == "synthetic_vibe_matching")
    private_row = {
        **synthetic,
        "source_id": "tester_private_chats",
        "name": "Tester private chats",
        "access_notes": "User/tester/private chat content must not be used.",
        "registry_status": "research_training_allowed",
    }
    path = tmp_path / "private_source.yml"
    path.write_text(yaml.safe_dump({"sources": [private_row]}, sort_keys=False), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "private or tester chat sources are never allowed for Vibe training" in result.stdout


def test_commercial_mode_rejects_nc_rows(tmp_path: Path) -> None:
    result = run_validator(write_subset(tmp_path, "dailydialog"), project_mode="commercial")

    assert result.returncode == 1
    assert "dailydialog" in result.stdout
    assert "commercial mode rejects rights_tier NC" in result.stdout
    assert "commercial mode rejects research-only source" in result.stdout


def test_external_benchmark_registry_rows_are_not_training_ready() -> None:
    rows = {row["source_id"]: row for row in load_example()["sources"]}

    assert rows["goemotions"]["usage"] == "local_research_augmentation_only"
    assert rows["goemotions"]["training_use_allowed"] is True
    assert rows["goemotions"]["commercial_use_allowed"] is False
    assert rows["goemotions"]["rights_tier"] == "apache_2_local_research"
    assert "Reddit-derived English comments" in rows["goemotions"]["access_notes"]
    assert "27 emotion categories or neutral" in rows["goemotions"]["access_notes"]

    assert rows["tweeteval_sentiment"]["usage"] == "sentiment_benchmark_metadata_only"
    assert rows["tweeteval_sentiment"]["training_use_allowed"] is False
    assert "positive, neutral, and negative labels" in rows["tweeteval_sentiment"]["access_notes"]

    assert rows["dailydialog"]["usage"] == "metadata_eval_only"
    assert rows["dailydialog"]["training_use_allowed"] is False

    assert rows["dair_ai_emotion"]["usage"] == "blocked_pending_license_review"
    assert rows["empathetic_dialogues"]["usage"] == "blocked_pending_license_review"
    assert rows["dair_ai_emotion"]["training_use_allowed"] is False
    assert rows["empathetic_dialogues"]["training_use_allowed"] is False

    assert rows["meld"]["usage"] == "local_noncommercial_research_augmentation_only"
    assert rows["meld"]["training_use_allowed"] is True
    assert rows["meld"]["commercial_use_allowed"] is False
    assert rows["meld"]["rights_tier"] == "gpl_3_local_nc_research"


def test_research_mode_reports_local_augmentation_sources_without_marking_training_ready(tmp_path: Path) -> None:
    summary = tmp_path / "summary.json"
    result = run_script(
        VALIDATOR,
        "--config",
        str(EXAMPLE),
        "--project-mode",
        "research_only",
        "--json-out",
        str(summary),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["training_ready_source_ids"] == ["synthetic_vibe_matching"]
    assert payload["local_augmentation_source_ids"] == ["goemotions", "meld"]


def test_research_mode_rejects_non_synthetic_training_ready_rows(tmp_path: Path) -> None:
    payload = load_example()
    row = next(row for row in payload["sources"] if row["source_id"] == "dailydialog")
    row["training_use_allowed"] = True
    row["usage"] = "research_only"
    row["registry_status"] = "research_training_allowed"
    path = tmp_path / "external_training_ready.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    result = run_validator(path, project_mode="research_only")

    assert result.returncode == 1
    assert "non-synthetic training-ready sources must use an approved local research augmentation gate" in result.stdout


def test_commercial_mode_rejects_manual_review_rows(tmp_path: Path) -> None:
    result = run_validator(write_subset(tmp_path, "consent_coercion_safety_placeholder"), project_mode="commercial")

    assert result.returncode == 1
    assert "consent_coercion_safety_placeholder" in result.stdout
    assert "commercial mode rejects rights_tier manual-review" in result.stdout


def test_commercial_mode_rejects_restricted_rows(tmp_path: Path) -> None:
    result = run_validator(write_subset(tmp_path, "cmu_mosei"), project_mode="commercial")

    assert result.returncode == 1
    assert "cmu_mosei" in result.stdout
    assert "commercial mode rejects rights_tier restricted" in result.stdout


def test_commercial_mode_rejects_local_research_augmentation_rows(tmp_path: Path) -> None:
    result = run_validator(write_subset(tmp_path, "meld"), project_mode="commercial")

    assert result.returncode == 1
    assert "meld" in result.stdout
    assert "commercial mode rejects rights_tier gpl_3_local_nc_research" in result.stdout


def test_missing_required_field_fails(tmp_path: Path) -> None:
    payload = load_example()
    del payload["sources"][0]["license_url"]
    path = tmp_path / "missing.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "missing required field license_url" in result.stdout


def test_unknown_rights_fail_closed(tmp_path: Path) -> None:
    payload = load_example()
    row = next(row for row in payload["sources"] if row["source_id"] == "dailydialog")
    row["rights_tier"] = "unknown"
    row["license_name"] = "unknown"
    path = tmp_path / "unknown.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "unknown or ambiguous rights fail closed" in result.stdout
    assert "unknown or ambiguous license_name fails closed" in result.stdout


@pytest.mark.parametrize(
    ("source_id", "rights_tier"),
    [
        ("cmu_mosei", "restricted"),
        ("tweeteval_sentiment", "manual-review"),
    ],
)
def test_blocked_rights_tiers_never_pass_training_readiness(tmp_path: Path, source_id: str, rights_tier: str) -> None:
    payload = {"sources": [row for row in load_example()["sources"] if row["source_id"] == source_id]}
    payload["sources"][0]["training_use_allowed"] = True
    payload["sources"][0]["registry_status"] = "research_training_allowed"
    path = tmp_path / f"{source_id}.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert f"{rights_tier} source cannot be training-ready" in result.stdout


def test_local_augmentation_gate_rejects_goemotions_wrong_license_tier(tmp_path: Path) -> None:
    payload = {"sources": [row for row in load_example()["sources"] if row["source_id"] == "goemotions"]}
    payload["sources"][0]["rights_tier"] = "eval-only"
    path = tmp_path / "goemotions_wrong_tier.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "non-synthetic training-ready sources must use an approved local research augmentation gate" in result.stdout


def test_local_augmentation_gate_rejects_meld_commercial_use(tmp_path: Path) -> None:
    payload = {"sources": [row for row in load_example()["sources"] if row["source_id"] == "meld"]}
    payload["sources"][0]["commercial_use_allowed"] = True
    path = tmp_path / "meld_commercial.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 1
    assert "non-synthetic training-ready sources must use an approved local research augmentation gate" in result.stdout


def test_dry_run_downloader_does_not_download(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    manifest = tmp_path / "download_manifest.json"
    result = run_script(
        DOWNLOADER,
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
    assert payload["downloaded"] is False
    assert payload["raw_data_committed"] is False
    assert payload["selected_source_ids"] == ["synthetic_vibe_matching"]
    assert not cache_dir.exists()


def test_dry_run_downloader_refuses_commercial_mode(tmp_path: Path) -> None:
    result = run_script(
        DOWNLOADER,
        "--source-id",
        "synthetic_vibe_matching",
        "--project-mode",
        "commercial",
        "--dry-run",
        "--cache-dir",
        str(tmp_path / "cache"),
    )

    assert result.returncode == 1
    assert "commercial dataset access is blocked" in result.stderr.lower()


@pytest.mark.parametrize(
    "source_id",
    [
        "goemotions",
        "tweeteval_sentiment",
        "dailydialog",
        "dair_ai_emotion",
        "empathetic_dialogues",
    ],
)
def test_dry_run_downloader_refuses_external_candidates(source_id: str, tmp_path: Path) -> None:
    result = run_script(
        DOWNLOADER,
        "--source-id",
        source_id,
        "--project-mode",
        "research_only",
        "--dry-run",
        "--cache-dir",
        str(tmp_path / "cache"),
    )

    assert result.returncode == 1
    assert "not approved for download dry-run" in result.stderr


def test_dry_run_trainer_does_not_train(tmp_path: Path) -> None:
    report = tmp_path / "dry_run_report.json"
    model_out = tmp_path / "models" / "baseline.pkl"
    vector_out = tmp_path / "vectors" / "baseline.index"
    result = run_script(
        TRAINER,
        "--dry-run",
        "--project-mode",
        "research_only",
        "--report-out",
        str(report),
        "--model-out",
        str(model_out),
        "--vector-out",
        str(vector_out),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["trained"] is False
    assert payload["model_saved"] is False
    assert payload["vector_artifacts_created"] is False
    assert payload["provider_calls_made"] is False
    assert not model_out.exists()
    assert not vector_out.exists()


def test_no_raw_model_vector_provider_or_training_outputs_are_created(tmp_path: Path) -> None:
    raw_cache = tmp_path / "data" / "external"
    corpus_out = tmp_path / "data" / "vibe_training" / "derived" / "corpus.jsonl"
    corpus_manifest = tmp_path / "corpus_manifest.json"
    model_out = tmp_path / "models" / "dry_run.bin"
    vector_out = tmp_path / "vectors" / "dry_run.faiss"
    provider_out = tmp_path / "provider_outputs" / "response.json"
    trainer_report = tmp_path / "trainer_report.json"

    download = run_script(
        DOWNLOADER,
        "--source-id",
        "synthetic_vibe_matching",
        "--project-mode",
        "research_only",
        "--dry-run",
        "--cache-dir",
        str(raw_cache),
    )
    build = run_script(
        BUILDER,
        "--project-mode",
        "research_only",
        "--dry-run",
        "--output",
        str(corpus_out),
        "--manifest-out",
        str(corpus_manifest),
    )
    train = run_script(
        TRAINER,
        "--project-mode",
        "research_only",
        "--dry-run",
        "--report-out",
        str(trainer_report),
        "--model-out",
        str(model_out),
        "--vector-out",
        str(vector_out),
    )

    assert download.returncode == 0, download.stdout + download.stderr
    assert build.returncode == 0, build.stdout + build.stderr
    assert train.returncode == 0, train.stdout + train.stderr
    assert not raw_cache.exists()
    assert not corpus_out.exists()
    assert not model_out.exists()
    assert not vector_out.exists()
    assert not provider_out.exists()
    assert json.loads(corpus_manifest.read_text(encoding="utf-8"))["corpus_created"] is False
