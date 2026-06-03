from __future__ import annotations

import json
from pathlib import Path

from tools import create_human_review_packet as packet


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_create_human_review_packet_writes_balanced_seed_and_bootstrap_labels(tmp_path: Path) -> None:
    output = tmp_path / "seed_review_packet.jsonl"
    labels = tmp_path / "seed_reviewed_labels.jsonl"

    exit_code = packet.main(
        [
            "--input",
            "data/synthetic/whatsapp/conversations.jsonl",
            "--output",
            str(output),
            "--bootstrap-labels-output",
            str(labels),
            "--limit",
            "50",
        ]
    )

    assert exit_code == 0
    rows = _read_jsonl(output)
    label_rows = _read_jsonl(labels)
    assert len(rows) == 50
    assert len(label_rows) == 50 * len(packet.CUE_UNIVERSE)
    assert {row["category"] for row in rows} >= {
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
    assert all(row["synthetic"] is True and row["not_copied_from_real_chat"] is True for row in rows)
    assert all(row["reviewer"] == "synthetic_bootstrap" for row in label_rows)
    assert all(row["not_human_validated"] is True for row in label_rows)


def test_review_packet_instructions_block_hidden_inferences() -> None:
    rows = packet.build_packet_rows(packet.select_balanced(packet.read_jsonl(Path("data/synthetic/whatsapp/conversations.jsonl")), limit=1, seed=1))
    text = " ".join(rows[0]["review_instructions"]).lower()
    assert "observable wording only" in text
    assert "do not label hidden intent" in text
    assert "cheating" in text
    assert "attraction" in text
    assert "diagnosis" in text
