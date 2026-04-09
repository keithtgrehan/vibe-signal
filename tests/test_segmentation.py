from __future__ import annotations

from pathlib import Path

from vibesignal_ai.ingest.segmentation import detect_topical_blocks, group_turns, link_response_pairs
from vibesignal_ai.ingest.whatsapp_parser import parse_whatsapp_file


def test_speaker_normalization_language_and_turn_grouping() -> None:
    fixture = Path(__file__).parent / "fixtures" / "relationship_chat_hardened.txt"
    messages = parse_whatsapp_file(fixture)
    turns = group_turns(messages)
    pairs = link_response_pairs(turns)
    blocks = detect_topical_blocks(turns)

    assert messages[0]["speaker"] == messages[1]["speaker"]
    assert messages[0]["conversation_detected_language"] == "en"
    assert any(pair["link_score"] > 0 for pair in pairs)
    assert blocks
    assert blocks[0]["turn_ids"]
