from __future__ import annotations

from pathlib import Path

from vibesignal_ai.ingest.segmentation import group_turns
from vibesignal_ai.ingest.whatsapp_parser import parse_whatsapp_file


def test_whatsapp_parser_hardening_features() -> None:
    fixture = Path(__file__).parent / "fixtures" / "relationship_chat_hardened.txt"
    messages = parse_whatsapp_file(fixture)

    assert len(messages) == 8
    assert messages[0]["emoji_text"].count("smiling_face_with_smiling_eyes") == 1
    assert messages[2]["normalized_text"] == "i do not know yet"
    assert messages[3]["message_type"] == "image_omitted"
    assert messages[4]["message_type"] == "system_notice"
    assert messages[0]["speaker"] == messages[1]["speaker"]
    assert all(item["conversation_detected_language"] == "en" for item in messages)

    turns = group_turns(messages)
    assert len(turns) == 5
    assert turns[0]["message_count"] == 2
