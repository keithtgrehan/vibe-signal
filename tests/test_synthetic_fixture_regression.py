from __future__ import annotations

import json
from pathlib import Path


CONVERSATIONS_PATH = Path("data/synthetic/whatsapp/conversations.jsonl")
MANIFEST_PATH = Path("data/synthetic/whatsapp/fixture_manifest.json")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_committed_synthetic_whatsapp_fixture_set_has_expected_counts() -> None:
    conversations = _read_jsonl(CONVERSATIONS_PATH)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert sum(len(row["messages"]) for row in conversations) == 10000
    assert len(conversations) == 5000
    assert manifest["split_message_counts"] == {
        "dev": 6000,
        "hard_negative": 2000,
        "heldout": 1000,
        "red_team": 1000,
    }
    assert {row["split"] for row in conversations} == {"dev", "hard_negative", "heldout", "red_team"}
    assert {row["category"] for row in conversations} >= {
        "happy",
        "new_in_love",
        "in_love",
        "cheating_ambiguous_private_eval_label",
        "short_ok",
        "boundary_pressure",
        "conflict_repair",
        "overloaded_message",
    }


def test_cheating_ambiguous_is_private_synthetic_metadata_not_product_claim() -> None:
    conversations = _read_jsonl(CONVERSATIONS_PATH)
    category_rows = [row for row in conversations if row["category"] == "cheating_ambiguous_private_eval_label"]

    assert category_rows
    assert all(row["category_scope"] == "private synthetic evaluation metadata only" for row in category_rows)
    assert all("cheating detection" not in " ".join(row["forbidden_outputs"]).lower() for row in category_rows)
    assert all("cheating detection" not in row["input_text"].lower() for row in category_rows)
