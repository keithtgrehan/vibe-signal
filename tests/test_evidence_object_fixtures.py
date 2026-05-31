from __future__ import annotations

from pathlib import Path

from vibesignal_ai.evidence.export import load_evidence_jsonl
from vibesignal_ai.evidence.objects import validate_evidence_object


ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "evidence_objects" / "valid_evidence_objects.jsonl"
INVALID = ROOT / "tests" / "fixtures" / "evidence_objects" / "invalid_evidence_objects.jsonl"


def test_valid_evidence_fixture_rows_pass() -> None:
    rows = load_evidence_jsonl(VALID)

    assert rows
    assert len({row["evidence_id"] for row in rows}) == len(rows)
    for row in rows:
        assert row["conversation_id"].startswith("synthetic_fixture_")
        assert "Synthetic fixture only." in row["provenance"]["note"]
        assert validate_evidence_object(row) == []


def test_invalid_evidence_fixture_rows_fail() -> None:
    rows = load_evidence_jsonl(INVALID)

    assert len(rows) >= 5
    failures = [validate_evidence_object(row) for row in rows]
    assert all(errors for errors in failures)
    assert any(any("missing required field" in error for error in errors) for errors in failures)
    assert any(any("unsafe field emotion_label" in error for error in errors) for errors in failures)
    assert any(any("unsafe field deception_score" in error for error in errors) for errors in failures)
    assert any(any("missing interpretation limit" in error for error in errors) for errors in failures)
    assert any(any("restricted or unknown rights cannot allow raw text commit" in error for error in errors) for errors in failures)
