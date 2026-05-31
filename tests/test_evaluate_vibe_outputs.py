from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.evaluate_vibe_outputs import evaluate
from vibesignal_ai.evidence.export import load_evidence_jsonl


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_vibe_outputs.py"
EVIDENCE = ROOT / "tests" / "fixtures" / "evidence_objects" / "valid_evidence_objects.jsonl"


def test_evaluate_outputs_passes_safe_fixture_evidence() -> None:
    evidence_rows = load_evidence_jsonl(EVIDENCE)
    gold = [
        {
            "conversation_id": "synthetic_fixture_conv_1",
            "label_id": "gold_1",
            "label_type": "directness_shift",
            "evidence_text": "Can you confirm Friday at 3pm?",
        }
    ]

    report = evaluate(gold_labels=gold, evidence_rows=evidence_rows, output_payloads=[])

    assert report["status"] == "pass"
    assert report["metrics"]["reviewed_label_count"] == 1
    assert report["metrics"]["matched_labels"] == 1


def test_low_reviewed_label_count_blocks_benchmark_claims() -> None:
    report = evaluate(
        gold_labels=[],
        evidence_rows=[],
        output_payloads=[{"summary": "This is a benchmark-quality result."}],
    )

    assert report["status"] == "fail"
    assert "below 50 reviewed labels: no ML/benchmark claims" in report["blockers"]


def test_unsafe_claim_and_provider_canonical_fail() -> None:
    report = evaluate(
        gold_labels=[],
        evidence_rows=[],
        output_payloads=[
            {"summary": "They are lying."},
            {"source_type": "provider_summary", "is_canonical": True, "summary": "Pattern summary only."},
        ],
    )

    assert report["status"] == "fail"
    assert "unsafe output claim detected" in report["blockers"]
    assert "provider outputs cannot be canonical" in report["blockers"]


def test_evaluate_script_help_runs() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Evaluate Vibe" in result.stdout


def test_evaluate_script_writes_json_report(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--evidence", str(EVIDENCE), "--json-out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["metrics"]["potential_false_positives"] == 2
