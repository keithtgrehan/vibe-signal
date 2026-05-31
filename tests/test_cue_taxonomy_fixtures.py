from __future__ import annotations

import json
from pathlib import Path

from vibesignal_ai.features.cue_taxonomy import CUE_IDS, detect_cues


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "cue_taxonomy" / "cue_taxonomy_cases.json"
REQUIRED_KEYS = {"id", "name", "messages", "expected_present", "expected_absent", "notes"}


def load_cases() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_cue_taxonomy_fixture_schema() -> None:
    rows = load_cases()

    assert len(rows) >= 16
    assert len({row["id"] for row in rows}) == len(rows)
    for row in rows:
        assert REQUIRED_KEYS <= set(row)
        assert row["id"].startswith("T")
        assert row["notes"] == "Synthetic fixture only."
        assert isinstance(row["messages"], list) and row["messages"]
        for message in row["messages"]:
            assert {"id", "author", "created_at", "text"} <= set(message)
        for expected in row["expected_present"]:
            assert expected["cue_id"] in CUE_IDS
            assert int(expected["min_strength"]) >= 1
        for absent in row["expected_absent"]:
            assert absent in CUE_IDS


def test_cue_taxonomy_runtime_matches_synthetic_fixtures() -> None:
    for row in load_cases():
        cues = detect_cues(row["messages"], conversation_id=f"synthetic_{row['id'].lower()}")
        by_cue: dict[str, list[dict]] = {}
        for cue in cues:
            by_cue.setdefault(cue["cue_id"], []).append(cue)

        for expected in row["expected_present"]:
            cue_id = expected["cue_id"]
            assert cue_id in by_cue, f"{row['id']} expected {cue_id}; got {sorted(by_cue)}"
            assert max(int(cue.get("strength", 0)) for cue in by_cue[cue_id]) >= int(expected["min_strength"])

        for cue_id in row["expected_absent"]:
            assert cue_id not in by_cue, f"{row['id']} did not expect {cue_id}; got {sorted(by_cue)}"
