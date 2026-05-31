from __future__ import annotations

import json
from pathlib import Path

from vibesignal_ai.safety.redline_output_blocker import check_output_text
from vibesignal_ai.safety.validator import validate_text


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "redline_outputs" / "redline_output_cases.json"
REQUIRED_KEYS = {"id", "candidate_output", "expected_action", "reason"}


def load_cases() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_redline_fixture_schema() -> None:
    rows = load_cases()

    assert rows
    assert len({row["id"] for row in rows}) == len(rows)
    assert {row["expected_action"] for row in rows} == {"allow", "block"}
    for row in rows:
        assert REQUIRED_KEYS <= set(row)
        assert row["id"].startswith("R")
        if row["expected_action"] == "block":
            assert row.get("safe_replacement")


def test_redline_fixture_expected_actions() -> None:
    for row in load_cases():
        result = check_output_text(row["candidate_output"])
        if row["expected_action"] == "block":
            assert result["status"] == "block", row
            assert result["categories"], row
            assert validate_text(row["candidate_output"])
        else:
            assert result["status"] == "allow", row
            assert validate_text(row["candidate_output"]) == []
