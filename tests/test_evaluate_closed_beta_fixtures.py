from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "scripts" / "evaluate_closed_beta_fixtures.py"


def run_evaluator(input_path: Path, output_md: Path, output_json: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--input",
            str(input_path),
            "--output-md",
            str(output_md),
            "--output-json",
            str(output_json),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_closed_beta_fixture_evaluator_reports_cue_span_and_forbidden_output(tmp_path: Path) -> None:
    fixtures = [
        {
            "id": "unanswered_ask_001",
            "synthetic": True,
            "not_copied_from_real_chat": True,
            "input": "self: Can you confirm by tonight?\nother: Things are busy right now.",
            "expected_cue": "unanswered_ask",
            "expected_span": "Things are busy right now.",
            "required_safe_phrases": ["does not directly answer"],
            "forbidden_outputs": ["They are avoiding you", "This proves"],
            "safe_output": "The reply does not directly answer the timing question.",
            "screenshot_allowed": True,
        },
        {
            "id": "low_evidence_001",
            "synthetic": True,
            "not_copied_from_real_chat": True,
            "input": "self: hey\nother: ok",
            "expected_cue": "low_signal",
            "expected_span": "",
            "required_safe_phrases": ["Not enough context"],
            "forbidden_outputs": ["This proves"],
            "safe_output": "This exchange is too short to read safely.",
            "screenshot_allowed": True,
        },
    ]
    input_path = tmp_path / "fixtures.json"
    output_md = tmp_path / "latest.md"
    output_json = tmp_path / "latest.json"
    input_path.write_text(json.dumps(fixtures), encoding="utf-8")

    result = run_evaluator(input_path, output_md, output_json)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["trained"] is False
    assert payload["private_data_read"] is False
    assert payload["summary"]["fixture_count"] == 2
    assert payload["summary"]["forbidden_output_violations"] == 0
    first, second = payload["fixtures"]
    assert first["cue_hit"] is True
    assert first["expected_span_hit"] is True
    assert first["required_safe_phrase_hit"] is True
    assert second["low_evidence_fallback"] is True
    assert "Closed-Beta Synthetic Fixture Evaluation" in output_md.read_text(encoding="utf-8")
