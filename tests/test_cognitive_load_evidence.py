from __future__ import annotations

from vibesignal_ai.features.cue_taxonomy import detect_cues


def test_dense_multi_part_message_gets_cognitive_load_evidence() -> None:
    cues = detect_cues(
        [
            {
                "id": "m1",
                "author": "self",
                "text": "I need to check the plan, the calendar, the document, the room, the food, and the backup option before tomorrow.",
            }
        ],
        conversation_id="synthetic_cognitive_load_evidence",
    )

    by_family = {str(row["cue_family"]): row for row in cues}
    assert "cognitive_load" in by_family
    assert "overloaded_message" in by_family
    assert by_family["cognitive_load"]["evidence_text"]
    assert by_family["cognitive_load"]["span_end"] > by_family["cognitive_load"]["span_start"]

