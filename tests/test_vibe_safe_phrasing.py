from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from vibesignal_ai.features.cue_taxonomy import detect_cues


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_vibe_text.py"
FORBIDDEN_OUTPUT_PATTERNS = (
    r"\bthey feel\b",
    r"\bthe person feels\b",
    r"\bthe person is\b",
    r"\bdiagnos",
    r"\battachment style\b",
    r"\bmake them like you\b",
    r"\bpersuasion optimization\b",
    r"\btrue emotion\b",
    r"\bmanipulation\b",
)


def generated_strings(row: dict) -> list[str]:
    return [str(row.get(field, "")) for field in ("safe_phrase", "explanation")]


def assert_safe_generated_language(rows: list[dict]) -> None:
    hits: list[str] = []
    for row in rows:
        for text in generated_strings(row):
            lowered = text.lower()
            for pattern in FORBIDDEN_OUTPUT_PATTERNS:
                if re.search(pattern, lowered):
                    hits.append(f"{row.get('cue_id')}: {pattern}: {text}")
    assert hits == []


def test_detected_cue_output_uses_safe_non_emotional_truth_phrasing() -> None:
    cues = detect_cues(
        [
            {
                "id": "m1",
                "author": "self",
                "created_at": "2026-05-31T10:00:00Z",
                "text": "Please confirm by Friday. You have to reply right now.",
            }
        ],
        conversation_id="synthetic_safe_language",
    )

    assert cues
    assert_safe_generated_language(cues)
    assert all(cue["safe_phrase"].startswith(("message contains", "text cues suggest")) for cue in cues)


def test_analyze_vibe_text_cli_outputs_structured_safe_evidence() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--text", "Maybe confirm Friday? No pressure, when you can."],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    rows = payload["evidence_objects"]
    assert rows
    assert {row["cue_family"] for row in rows} >= {"hedging", "specificity", "reassurance"}
    assert all({"cue_id", "cue_family", "span_start", "span_end", "confidence", "explanation", "safe_phrase"} <= set(row) for row in rows)
    assert_safe_generated_language(rows)
