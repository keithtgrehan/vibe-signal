from __future__ import annotations

import json
from pathlib import Path


CONVERSATIONS_PATH = Path("data/synthetic/whatsapp/conversations.jsonl")
EVALUATIONS_PATH = Path("data/synthetic/whatsapp/evaluations.jsonl")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_committed_synthetic_whatsapp_fixture_set_has_expected_counts() -> None:
    conversations = _read_jsonl(CONVERSATIONS_PATH)
    evaluations = _read_jsonl(EVALUATIONS_PATH)

    assert sum(len(row["messages"]) for row in conversations) == 1000
    assert len(conversations) == 455
    assert len(evaluations) == len(conversations)
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


def test_synthetic_whatsapp_evaluations_all_pass_contract_checks() -> None:
    evaluations = _read_jsonl(EVALUATIONS_PATH)

    assert evaluations
    assert all(row["passed"] is True for row in evaluations)
    assert all(row["evidence_complete"] is True for row in evaluations if row["expected_result_type"] != "low_signal")
    assert all(row["unsafe_output_absent"] is True for row in evaluations)
    assert all(row["numeric_confidence_absent"] is True for row in evaluations)
    assert all(row["cannot_infer_present"] is True for row in evaluations)
    assert all(row["signal_strength_valid"] is True for row in evaluations)
    assert all(row["repair_suggestion_safe"] is True for row in evaluations)


def test_cheating_ambiguous_is_private_synthetic_metadata_not_product_claim() -> None:
    conversations = _read_jsonl(CONVERSATIONS_PATH)
    evaluations = _read_jsonl(EVALUATIONS_PATH)
    category_rows = [row for row in conversations if row["category"] == "cheating_ambiguous"]
    evaluation_rows = [row for row in evaluations if row["category"] == "cheating_ambiguous"]

    assert category_rows
    assert evaluation_rows
    assert all(row["category_scope"] == "private synthetic evaluation metadata only" for row in category_rows)
    assert all("cheating detection" not in " ".join(row["forbidden_outputs"]).lower() for row in category_rows)
    assert all("cheating" not in json.dumps(row["result_excerpt"]).lower() for row in evaluation_rows)
