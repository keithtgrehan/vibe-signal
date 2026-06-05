from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from scripts.check_vibe_restricted_artifacts import find_restricted
from tools import ingest_private_whatsapp as ingest
from tools import prepare_private_label_review as prepare_review
from tools import redact_private_whatsapp as redact


ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_TEST_DIR = ROOT / "data" / "restricted" / "private_whatsapp" / "pytest_private_pipeline"
EXPECTED_REVIEW_COLUMNS = [
    "example_id",
    "split",
    "speaker_roles",
    "text_window_redacted",
    "candidate_labels",
    "evidence_hint",
    "review_label",
    "severity",
    "safe_next_step",
    "reviewer_notes",
]


def test_private_whatsapp_tree_is_gitignored() -> None:
    result = subprocess.run(
        ["git", "check-ignore", "-q", "data/restricted/private_whatsapp/processed/private_messages_redacted.jsonl"],
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0


def test_restricted_scanner_blocks_private_whatsapp_artifacts_by_path() -> None:
    flagged = find_restricted(
        [
            "data/restricted/private_whatsapp/raw/export.txt",
            "data/restricted/private_whatsapp/processed/private_messages.jsonl",
            "data/restricted/private_whatsapp/reports/whatsapp_dynamics_report.json",
            "data/restricted/private_whatsapp/models/private_dynamics_baseline.pkl",
        ]
    )

    assert flagged == [
        "data/restricted/private_whatsapp/raw/export.txt",
        "data/restricted/private_whatsapp/processed/private_messages.jsonl",
        "data/restricted/private_whatsapp/reports/whatsapp_dynamics_report.json",
        "data/restricted/private_whatsapp/models/private_dynamics_baseline.pkl",
    ]


def test_synthetic_private_inspired_fixture_path_is_allowed() -> None:
    assert find_restricted(["data/synthetic/private_inspired/dynamics_fixtures.jsonl"]) == []


def _cleanup_restricted_test_dir() -> None:
    shutil.rmtree(RESTRICTED_TEST_DIR, ignore_errors=True)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_parser_handles_whatsapp_sample_text() -> None:
    sample = "[01.06.26, 09:00:00] Keith: Can you confirm Friday?\n[01.06.26, 09:01:00] Bibi: Yes, Friday works."

    rows = ingest.parse_chat_text(sample)

    assert len(rows) == 2
    assert rows[0].speaker_role == "self"
    assert rows[0].text == "Can you confirm Friday?"
    assert rows[1].speaker_role == "other"
    assert rows[1].text == "Yes, Friday works."


def test_parser_handles_multiline_messages() -> None:
    sample = "\n".join(
        [
            "[01.06.26, 09:00:00] self: Can you confirm Friday?",
            "This is the second line.",
            "[01.06.26, 09:01:00] Other: Maybe later.",
        ]
    )

    rows = ingest.parse_chat_text(sample)

    assert len(rows) == 2
    assert rows[0].multiline is True
    assert rows[0].text == "Can you confirm Friday?\nThis is the second line."


def test_ingest_refuses_non_restricted_output_directory(tmp_path: Path) -> None:
    zip_path = tmp_path / "sample.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("_chat.txt", "[01.06.26, 09:00:00] Keith: Can you confirm Friday?")

    exit_code = ingest.main(["--zip-path", str(zip_path), "--output-dir", str(tmp_path / "out")])

    assert exit_code == 2


def test_scripts_do_not_print_raw_message_text(tmp_path: Path, capsys) -> None:
    _cleanup_restricted_test_dir()
    try:
        zip_path = tmp_path / "sample.zip"
        raw_text = "Can you confirm Friday?"
        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("_chat.txt", f"[01.06.26, 09:00:00] Keith: {raw_text}")

        ingest_exit = ingest.main(["--zip-path", str(zip_path), "--output-dir", str(RESTRICTED_TEST_DIR)])
        ingest_output = capsys.readouterr()

        redacted_path = RESTRICTED_TEST_DIR / "private_messages_redacted.jsonl"
        redact_exit = redact.main(
            [
                "--input",
                str(RESTRICTED_TEST_DIR / "private_messages.jsonl"),
                "--output",
                str(redacted_path),
                "--stats-out",
                str(RESTRICTED_TEST_DIR / "private_redaction_stats.json"),
            ]
        )
        redact_output = capsys.readouterr()

        assert ingest_exit == 0
        assert redact_exit == 0
        assert raw_text not in ingest_output.out
        assert raw_text not in ingest_output.err
        assert raw_text not in redact_output.out
        assert raw_text not in redact_output.err
    finally:
        _cleanup_restricted_test_dir()


def test_blocked_raw_files_are_ignored_by_git_patterns() -> None:
    ignored_paths = [
        "data/restricted/private_whatsapp/local_export.zip",
        "data/restricted/private_whatsapp/private_messages.jsonl",
        "example_chat.txt",
        "example_redacted.jsonl",
        "example_labels_private.csv",
        "example_private_review.csv",
    ]
    result = subprocess.run(
        ["git", "check-ignore", *ignored_paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    ignored = set(result.stdout.splitlines())
    assert set(ignored_paths) <= ignored


def test_review_csv_has_expected_columns() -> None:
    _cleanup_restricted_test_dir()
    try:
        redacted_jsonl = RESTRICTED_TEST_DIR / "private_messages_redacted.jsonl"
        review_csv = RESTRICTED_TEST_DIR / "private_label_review.csv"
        _write_jsonl(
            redacted_jsonl,
            [
                {"message_id": "m1", "speaker_role": "self", "text_redacted": "Can you confirm [DATE]?"},
                {"message_id": "m2", "speaker_role": "other", "text_redacted": "Maybe later."},
            ],
        )

        exit_code = prepare_review.main(["--input", str(redacted_jsonl), "--output", str(review_csv)])

        assert exit_code == 0
        with review_csv.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            assert reader.fieldnames == EXPECTED_REVIEW_COLUMNS
            rows = list(reader)
        assert rows
        assert "direct_ask" in rows[0]["candidate_labels"]
    finally:
        _cleanup_restricted_test_dir()
