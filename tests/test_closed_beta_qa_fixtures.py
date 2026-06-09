from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "synthetic" / "closed_beta_qa" / "closed_beta_qa_fixtures.json"
SCHEMA = ROOT / "schemas" / "closed_beta_qa_fixture.schema.json"

REQUIRED_FIELDS = {
    "id",
    "synthetic",
    "not_copied_from_real_chat",
    "input",
    "expected_cue",
    "expected_span",
    "required_safe_phrases",
    "forbidden_outputs",
    "safe_output",
    "screenshot_allowed",
}

REQUIRED_CUES = {
    "ambiguity",
    "unanswered_ask",
    "pressure",
    "boundary_pressure",
    "escalation",
    "cognitive_overload",
    "specificity_drop",
    "reassurance_directness",
    "backend_unreachable",
    "safety_fallback",
    "low_evidence",
}


def test_closed_beta_fixture_schema_and_data_are_synthetic_only() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))

    assert schema["title"] == "Closed Beta QA Fixture"
    assert isinstance(payload, list)
    assert len(payload) >= 10
    assert REQUIRED_CUES <= {row["expected_cue"] for row in payload}

    ids = set()
    for row in payload:
      assert REQUIRED_FIELDS <= set(row)
      assert row["id"] not in ids
      ids.add(row["id"])
      assert row["synthetic"] is True
      assert row["not_copied_from_real_chat"] is True
      assert row["screenshot_allowed"] is True
      assert isinstance(row["required_safe_phrases"], list) and row["required_safe_phrases"]
      assert isinstance(row["forbidden_outputs"], list) and row["forbidden_outputs"]
      assert "private" not in row["id"].lower()
      assert "tester" not in row["id"].lower()
