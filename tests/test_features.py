from __future__ import annotations

from vibesignal_ai.features.confidence_clarity import analyze_confidence_clarity
from vibesignal_ai.features.consistency import analyze_consistency
from vibesignal_ai.features.shift_radar import analyze_shift_radar
from vibesignal_ai.features.what_changed import analyze_what_changed
from vibesignal_ai.ingest.segmentation import group_turns, link_response_pairs


MESSAGES = [
    {"message_id": 1, "speaker": "Alex", "speaker_key": "alex", "text": "Are you still coming tonight?", "analysis_text": "Are you still coming tonight?", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:00:00"},
    {"message_id": 2, "speaker": "Sam", "speaker_key": "sam", "text": "Yes, I can be there by 7 because I leave work at 6.", "analysis_text": "Yes, I can be there by 7 because I leave work at 6.", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:01:00"},
    {"message_id": 3, "speaker": "Alex", "speaker_key": "alex", "text": "Can you confirm once you leave?", "analysis_text": "Can you confirm once you leave?", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:03:00"},
    {"message_id": 4, "speaker": "Sam", "speaker_key": "sam", "text": "Maybe later... not sure yet.", "analysis_text": "Maybe later... not sure yet.", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T09:25:00"},
    {"message_id": 5, "speaker": "Alex", "speaker_key": "alex", "text": "Okay, just let me know once you leave work.", "analysis_text": "Okay, just let me know once you leave work.", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T10:00:00"},
    {"message_id": 6, "speaker": "Sam", "speaker_key": "sam", "text": "Actually, change of plans, I probably cannot make dinner tonight.", "analysis_text": "Actually, change of plans, I probably cannot make dinner tonight.", "is_system": False, "analysis_included": True, "message_type": "text", "timestamp": "2026-04-07T10:45:00"},
]

SEGMENTS = [
    {"segment_id": 1, "speaker": "candidate", "start": 0.0, "end": 4.0, "text": "I led the migration in two phases because the team needed a safer rollout."},
    {"segment_id": 2, "speaker": "candidate", "start": 4.5, "end": 8.0, "text": "Um, I mean, the second phase focused on API cleanup and test coverage."},
    {"segment_id": 3, "speaker": "candidate", "start": 8.5, "end": 12.0, "text": "Well, well, the main point is that we reduced deploy risk and documented the handoff."},
]


def test_feature_modules_return_hardened_structured_outputs() -> None:
    turns = group_turns(MESSAGES)
    pairs = link_response_pairs(turns)
    shift = analyze_shift_radar(MESSAGES, turns=turns)
    consistency = analyze_consistency(MESSAGES, turns=turns, response_pairs=pairs)
    clarity = analyze_confidence_clarity(SEGMENTS)
    changed = analyze_what_changed(MESSAGES, turns=turns)

    assert shift["shift_events"]
    assert consistency["consistency_events"]
    assert "clarity_score" in clarity
    assert clarity["segment_metrics"][0]["sentence_count"] >= 1
    assert clarity["segment_metrics"][1]["self_corrections"] >= 1
    assert changed["earliest_significant_shift_point"] is not None
    assert any("less detailed" in item["summary"].lower() or "more softening" in item["summary"].lower() for item in changed["ranked_deltas"][:5])
