from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from vibesignal_ai.evidence.objects import build_evidence_object
from vibesignal_ai.evidence.export import write_evidence_jsonl


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_vibe_review_packet.py"
FIXTURE_EVIDENCE = ROOT / "tests" / "fixtures" / "evidence_objects" / "valid_evidence_objects.jsonl"


def fixture_evidence(path: Path) -> None:
    row = build_evidence_object(
        evidence_id="ev_1",
        conversation_id="conv_1",
        source_type="whatsapp_export",
        message_id="msg_1",
        turn_id="turn_1",
        speaker_role="self",
        cue_name="pressure_language",
        evidence_text="Please reply before tonight.",
        start_offset=0,
        end_offset=28,
        provenance={"source": "unit_test"},
    )
    write_evidence_jsonl(path, [row])


def run_builder(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_builds_markdown_and_csv_from_fixture_evidence(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.jsonl"
    md_out = tmp_path / "packet.md"
    csv_out = tmp_path / "packet.csv"
    fixture_evidence(evidence)

    result = run_builder("--evidence", str(evidence), "--md-out", str(md_out), "--csv-out", str(csv_out))

    assert result.returncode == 0, result.stdout + result.stderr
    markdown = md_out.read_text(encoding="utf-8")
    with csv_out.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert rows[0]["reviewer_label_type"] == ""
    assert rows[0]["reviewer_confidence"] == ""
    assert rows[0]["reviewer_notes"] == ""
    assert rows[0]["accept/reject"] == ""
    assert "machine cues are suggestions" in markdown.lower()
    assert "no emotion/deception/intent/diagnosis claims" in markdown.lower()


def test_refuses_invalid_evidence_unless_allow_invalid(tmp_path: Path) -> None:
    evidence = tmp_path / "bad_evidence.jsonl"
    md_out = tmp_path / "packet.md"
    csv_out = tmp_path / "packet.csv"
    evidence.write_text('{"evidence_id":"bad","conversation_id":"conv","source_type":"whatsapp_export"}\n', encoding="utf-8")

    result = run_builder("--evidence", str(evidence), "--md-out", str(md_out), "--csv-out", str(csv_out))

    assert result.returncode == 1
    assert "invalid evidence" in result.stderr.lower()

    allowed = run_builder(
        "--evidence",
        str(evidence),
        "--md-out",
        str(md_out),
        "--csv-out",
        str(csv_out),
        "--allow-invalid",
    )
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr
    assert csv_out.exists()


def test_builds_review_packet_from_committed_fixture(tmp_path: Path) -> None:
    md_out = tmp_path / "fixture_packet.md"
    csv_out = tmp_path / "fixture_packet.csv"

    result = run_builder("--evidence", str(FIXTURE_EVIDENCE), "--md-out", str(md_out), "--csv-out", str(csv_out))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "machine cues are suggestions" in md_out.read_text(encoding="utf-8").lower()
    with csv_out.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert {"reviewer_label_type", "reviewer_confidence", "reviewer_notes", "accept/reject"} <= set(rows[0])
