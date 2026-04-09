from __future__ import annotations

import json
from pathlib import Path

from vibesignal_ai.pipeline.run import analyze_conversation
from vibesignal_ai.summaries.summary_rewriter import rewrite_summary


def test_pipeline_happy_path_chat_with_hardened_artifacts(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "relationship_chat_hardened.txt"
    result = analyze_conversation(
        input_path=fixture,
        input_type="whatsapp",
        mode="relationship_chat",
        out_dir=tmp_path,
        rights_asserted=True,
    )

    root = Path(result["conversation_root"])
    required = [
        root / "raw" / "messages.json",
        root / "processed" / "segments.json",
        root / "processed" / "turns.json",
        root / "derived" / "shift_radar.json",
        root / "derived" / "consistency.json",
        root / "derived" / "confidence_clarity.json",
        root / "derived" / "what_changed.json",
        root / "exports" / "shift_events.csv",
        root / "exports" / "consistency_events.csv",
        root / "exports" / "ui_payloads.json",
        root / "exports" / "pattern_summary.json",
        root / "exports" / "ui_summary.json",
    ]
    for path in required:
        assert path.exists()
        assert path.stat().st_size > 0

    payloads = json.loads(Path(result["ui_payloads_path"]).read_text(encoding="utf-8"))
    assert "ui_summary" in payloads
    assert payloads["pattern_summary"]["headline"]


def test_pipeline_happy_path_interview_segments(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "interview_segments.json"
    result = analyze_conversation(
        input_path=fixture,
        input_type="interview_audio",
        mode="interview",
        out_dir=tmp_path,
        processing_mode="local_plus_summary",
        rights_asserted=True,
    )

    assert Path(result["summary_path"]).exists()
    summary = json.loads(Path(result["summary_path"]).read_text(encoding="utf-8"))
    assert "summary" in summary
    assert "limitations" in summary


def test_optional_summary_falls_back_safely() -> None:
    payload = rewrite_summary(
        {
            "shift_radar": {"shift_start_window": {"summary": "Later replies use more softening language."}},
            "consistency": {"top_reasons": ["Direct answer style weakens after the midpoint."]},
            "confidence_clarity": {},
            "what_changed": {"comparison_summary": "Later replies look shorter and less detailed than earlier ones.", "top_changes": ["Later replies look shorter and less detailed than earlier ones."]},
        },
        rewriter=lambda _: '{"summary":"This suggests hidden intent.","observations":["This means they are secretive."],"limitations":[]}',
    )
    assert "hidden intent" not in payload["summary"].lower()
    assert payload["summary"]
