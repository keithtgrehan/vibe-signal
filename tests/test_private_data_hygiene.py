from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_INGESTION_TEST = ROOT / "tests" / "test_private_whatsapp_ingestion_safety.py"
AUDIT_NOTE = ROOT / "docs" / "security" / "private_data_exposure_audit.md"
PRIVATE_SOURCE_EXAMPLE = ROOT / "configs" / "private_training_sources.example.yml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def test_private_ingestion_safety_fixtures_use_neutral_speaker_names() -> None:
    text = _read(PRIVATE_INGESTION_TEST)

    assert "Person A:" in text
    assert "Person B:" in text
    assert not re.search(r"\b(?:Keith|Bibi):", text)


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


def test_private_data_exposure_audit_note_exists_with_required_boundaries() -> None:
    text = _read(AUDIT_NOTE)
    lowered = text.lower()

    assert "audit found no exposure in checked surfaces" in lowered
    assert "private data must remain local-only" in lowered
    assert "n8n must not receive raw private chat content unless future rights review allows it" in lowered
    assert "keep n8n no-raw-content unless future rights/legal review allows it" in lowered
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
