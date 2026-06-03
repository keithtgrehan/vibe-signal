from __future__ import annotations

import json
from pathlib import Path


CONVERSATIONS_PATH = Path("data/synthetic/whatsapp/conversations.jsonl")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_committed_synthetic_whatsapp_fixture_set_has_expected_counts() -> None:
    conversations = _read_jsonl(CONVERSATIONS_PATH)

    assert sum(len(row["messages"]) for row in conversations) == 1000
    assert len(conversations) == 455
    assert {row["category"] for row in conversations} >= {
        "happy",
        "new_in_love",
        "in_love",
        "unhappy",
        "scared",
        "cheating_ambiguous",
        "low_signal",
        "boundary_pressure",
        "conflict_repair",
        "overloaded_message",
    }


def test_cheating_ambiguous_is_private_synthetic_metadata_not_product_claim() -> None:
    conversations = _read_jsonl(CONVERSATIONS_PATH)
    category_rows = [row for row in conversations if row["category"] == "cheating_ambiguous"]

    assert category_rows
    assert all(row["category_scope"] == "private synthetic evaluation metadata only" for row in category_rows)
    assert all("cheating detection" not in " ".join(row["forbidden_outputs"]).lower() for row in category_rows)
    assert all("cheating detection" not in row["input_text"].lower() for row in category_rows)
