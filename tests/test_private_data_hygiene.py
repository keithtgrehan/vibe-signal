from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_INGESTION_TEST = ROOT / "tests" / "test_private_whatsapp_ingestion_safety.py"
AUDIT_NOTE = ROOT / "docs" / "security" / "private_data_exposure_audit.md"
PRIVATE_SOURCE_EXAMPLE = ROOT / "configs" / "private_training_sources.example.yml"
PRIVATE_METADATA_CHECK = ROOT / "scripts" / "check_private_metadata_exposure.py"
N8N_ROOT = ROOT / "ops" / "n8n"
SAFETY_WORKFLOW = ROOT / ".github" / "workflows" / "safety.yml"
WEB_WORKFLOW = ROOT / ".github" / "workflows" / "web.yml"
BACKEND_ROOT = ROOT / "backend"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_metadata_check(*paths: Path) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(PRIVATE_METADATA_CHECK)]
    args.extend(str(path) for path in paths)
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def _prior_real_name_source_id() -> str:
    first = "".join(chr(code) for code in (108, 97, 117, 114, 97))
    second = "".join(chr(code) for code in (98, 105, 98, 105))
    return f"private_whatsapp_{first}_{second}"


def _restricted_private_path(area: str, filename: str) -> str:
    return "/".join(("data", "restricted", "private_whatsapp", area, filename))


def _iter_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for key, nested in value.items():
            strings.extend(_iter_strings(key))
            strings.extend(_iter_strings(nested))
        return strings
    if isinstance(value, list):
        strings: list[str] = []
        for nested in value:
            strings.extend(_iter_strings(nested))
        return strings
    return []


def test_private_metadata_exposure_script_exists_and_passes_current_tracked_repo() -> None:
    assert PRIVATE_METADATA_CHECK.exists()

    result = _run_metadata_check()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Private metadata exposure check passed" in result.stdout


def test_private_metadata_exposure_script_rejects_prior_real_name_source_identifier(tmp_path: Path) -> None:
    probe = tmp_path / "probe.yml"
    probe.write_text(f"{_prior_real_name_source_id()}:\n  source_type: whatsapp_export\n", encoding="utf-8")

    result = _run_metadata_check(probe)

    assert result.returncode == 1
    assert "real_person_private_source_identifier" in result.stdout
    assert _prior_real_name_source_id() not in result.stdout


def test_private_metadata_exposure_script_rejects_private_artifact_paths(tmp_path: Path) -> None:
    blocked_paths = (
        _restricted_private_path("raw", "local_export.zip"),
        _restricted_private_path("processed", "private_messages.jsonl"),
        _restricted_private_path("models", "weak_label_baseline.pkl"),
        _restricted_private_path("reports", "private_report.md"),
    )
    for index, blocked_path in enumerate(blocked_paths):
        probe = tmp_path / f"probe_{index}.yml"
        probe.write_text(f"private_whatsapp_source_001:\n  path: {blocked_path}\n", encoding="utf-8")

        result = _run_metadata_check(probe)

        assert result.returncode == 1
        assert "private_artifact_path" in result.stdout
        assert blocked_path not in result.stdout


def test_private_metadata_exposure_script_allows_neutral_ids_and_operator_name(tmp_path: Path) -> None:
    probe = tmp_path / "safe.md"
    probe.write_text(
        "Legal operator: Keith Grehan\n\nprivate_whatsapp_source_001:\n  source_type: whatsapp_export\n",
        encoding="utf-8",
    )

    result = _run_metadata_check(probe)

    assert result.returncode == 0, result.stdout + result.stderr


def test_private_metadata_exposure_script_rejects_n8n_private_metadata_examples(tmp_path: Path) -> None:
    probe = tmp_path / "workflow.json"
    payload = (
        '{"nodes":[{"parameters":{"samplePath":"'
        + _restricted_private_path("raw", "local_export.zip")
        + '",'
        f'"source":"{_prior_real_name_source_id()}"'
        "}}]}\n"
    )
    probe.write_text(payload, encoding="utf-8")

    result = _run_metadata_check(probe)

    assert result.returncode == 1
    assert "private_artifact_path" in result.stdout
    assert "real_person_private_source_identifier" in result.stdout


def test_private_ingestion_safety_fixtures_use_neutral_speaker_names() -> None:
    text = _read(PRIVATE_INGESTION_TEST)
    old_self = "".join(chr(code) for code in (75, 101, 105, 116, 104))
    old_other = "".join(chr(code) for code in (66, 105, 98, 105))

    assert "Person A:" in text
    assert "Person B:" in text
    assert not re.search(rf"\b(?:{old_self}|{old_other}):", text)


def test_private_training_source_example_uses_neutral_metadata_only_ids() -> None:
    payload = yaml.safe_load(_read(PRIVATE_SOURCE_EXAMPLE))
    assert isinstance(payload, dict)

    source_ids = list(payload)
    assert source_ids == ["private_whatsapp_source_001"]
    for source_id in source_ids:
        assert re.fullmatch(r"private_whatsapp_source_\d{3}", source_id)

    combined = "\n".join(_iter_strings(payload))
    forbidden_patterns = (
        r"data/restricted/private_whatsapp/(?:raw|processed|models|reports)\b",
        r"\bprivate_label_review_100\b",
        r"\bprivate_label_review.*\.(?:csv|xlsx)\b",
        r"\b\w+_\w+_whatsapp_export\b",
        r"\bprivate_whatsapp_(?!source_\d{3}\b)[a-z0-9_]+\b",
    )
    for pattern in forbidden_patterns:
        assert not re.search(pattern, combined, flags=re.IGNORECASE)


def test_n8n_assets_do_not_contain_private_content_or_metadata_markers() -> None:
    result = _run_metadata_check(N8N_ROOT)

    assert result.returncode == 0, result.stdout + result.stderr
    combined = "\n".join(path.read_text(encoding="utf-8") for path in N8N_ROOT.rglob("*") if path.is_file())
    lowered = combined.lower()
    assert "raw private chat content or private source metadata" in lowered
    assert "future rights/legal review" in lowered


def test_backend_routes_do_not_expose_restricted_private_artifacts_or_source_ids() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in BACKEND_ROOT.rglob("*.py"))

    assert "data/restricted/private_whatsapp" not in combined
    assert "private_whatsapp_source_001" not in combined
    assert "private_label_review" not in combined
    assert "private_messages.jsonl" not in combined


def test_ci_runs_private_metadata_exposure_guardrails() -> None:
    safety = _read(SAFETY_WORKFLOW)
    web = _read(WEB_WORKFLOW)

    assert "python scripts/check_private_metadata_exposure.py" in safety
    assert "python ../scripts/check_private_metadata_exposure.py --include-web-dist" in web


def test_private_data_exposure_audit_note_exists_with_required_boundaries() -> None:
    text = _read(AUDIT_NOTE)
    lowered = text.lower()

    assert "audit found no exposure in checked surfaces" in lowered
    assert "private data must remain local-only" in lowered
    assert "n8n must not receive raw private chat content unless future rights review allows it" in lowered
    assert "keep n8n no-raw-content unless future rights/legal review allows it" in lowered
    assert "private data and private metadata must remain local-only" in lowered
    assert "raw private chat content or private source metadata unless future rights/legal review allows it" in lowered
    assert "remaining uncertainty" in lowered
    assert "do not paste private message content" in lowered


def test_private_data_exposure_audit_note_records_metadata_remediation_and_final_pass() -> None:
    text = _read(AUDIT_NOTE)
    lowered = text.lower()

    assert "metadata exposure remediation" in lowered
    assert "tracked metadata" in lowered
    assert "private_whatsapp_source_001" in text
    assert "history rewrite was not performed in this pr" in lowered
    assert "no raw private whatsapp/gold-review content found in checked repo/site/artifact surfaces" in lowered
    assert "one metadata-only exposure was found and remediated in current tracked files" in lowered
    assert "historical metadata exposure remains in git history unless a separate history rewrite is approved" in lowered


def test_private_data_exposure_audit_note_avoids_absolute_certainty() -> None:
    text = _read(AUDIT_NOTE)

    forbidden_patterns = (
        r"\bguarantees?\s+no\s+exposure\b",
        r"\bproves?\s+no\s+exposure\b",
        r"\ball\s+possible\s+surfaces\b",
        r"\bcomplete\s+certainty\b",
        r"\bexhaustive\s+proof\b",
    )
    for pattern in forbidden_patterns:
        assert not re.search(pattern, text, flags=re.IGNORECASE)
