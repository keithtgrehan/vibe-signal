from __future__ import annotations

import json
from pathlib import Path

from tools.create_human_review_packet import build_bootstrap_labels, read_jsonl, select_balanced


ROOT = Path(__file__).resolve().parents[1]


def test_human_reviewed_cue_label_schema_requires_safety_fields() -> None:
    schema = json.loads((ROOT / "schemas" / "human_reviewed_cue_label.schema.json").read_text(encoding="utf-8"))

    required = set(schema["required"])
    assert {
        "label_id",
        "fixture_id",
        "reviewer",
        "not_human_validated",
        "cue_id",
        "cue_present",
        "evidence_supports_cue",
        "blocked_inference_guard",
    } <= required
    guard_required = set(schema["properties"]["blocked_inference_guard"]["required"])
    assert {
        "no_hidden_intent",
        "no_cheating",
        "no_attraction",
        "no_diagnosis",
        "no_true_emotion",
        "no_attachment_style_or_neurotype",
    } == guard_required


def test_bootstrap_label_rows_match_schema_required_fields() -> None:
    conversations = select_balanced(read_jsonl(Path("data/synthetic/whatsapp/conversations.jsonl")), limit=2, seed=1)
    labels = build_bootstrap_labels(conversations)
    schema = json.loads((ROOT / "schemas" / "human_reviewed_cue_label.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])

    assert labels
    for row in labels:
        assert required <= set(row)
        assert row["reviewer"] == "synthetic_bootstrap"
        assert row["not_human_validated"] is True
        assert all(row["blocked_inference_guard"].values())
