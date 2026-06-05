from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_INGESTION_TEST = ROOT / "tests" / "test_private_whatsapp_ingestion_safety.py"
AUDIT_NOTE = ROOT / "docs" / "security" / "private_data_exposure_audit.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_private_ingestion_safety_fixtures_use_neutral_speaker_names() -> None:
    text = _read(PRIVATE_INGESTION_TEST)

    assert "Person A:" in text
    assert "Person B:" in text
    assert not re.search(r"\b(?:Keith|Bibi):", text)


def test_private_data_exposure_audit_note_exists_with_required_boundaries() -> None:
    text = _read(AUDIT_NOTE)
    lowered = text.lower()

    assert "audit found no exposure in checked surfaces" in lowered
    assert "private data must remain local-only" in lowered
    assert "n8n must not receive raw private chat content unless future rights review allows it" in lowered
    assert "remaining uncertainty" in lowered
    assert "do not paste private message content" in lowered


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
