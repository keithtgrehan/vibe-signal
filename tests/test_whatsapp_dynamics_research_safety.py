from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from tools import analyze_whatsapp_dynamics
from tools import export_synthetic_dynamics_fixtures
from tools import train_private_dynamics_baseline


ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_TEST_ROOT = ROOT / "data" / "restricted" / "private_whatsapp" / "test_whatsapp_dynamics"
RAW_SAMPLE_TEXT = "Can you confirm the plan by tonight?"
BLOCKED_REPORT_CLAIMS = (
    "clinical",
    "relationship score",
    "true emotion",
    "secret intent",
    "hidden intent",
    "hiding anger",
    "suppressed emotion",
    "they are lying",
    "they are manipulating",
    "attachment style",
)
REQUIRED_HEADINGS = [
    "# EMOTIONAL TRAJECTORY MAP",
    "# CONVERSATIONAL ASYMMETRY METRICS",
    "# MULTI-MODAL SYNCHRONICITY (TEXT VS. AUDIO)",
    "# RELATIONSHIP HEALTH SYNTHESIS",
]


def _reset_restricted_test_root() -> None:
    if RESTRICTED_TEST_ROOT.exists():
        shutil.rmtree(RESTRICTED_TEST_ROOT)
    RESTRICTED_TEST_ROOT.mkdir(parents=True, exist_ok=True)


def _write_messages(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "message_id": "m1",
            "speaker_role": "self",
            "timestamp": "2026-01-01T10:00:00Z",
            "text": RAW_SAMPLE_TEXT,
        },
        {
            "message_id": "m2",
            "speaker_role": "other",
            "timestamp": "2026-01-01T10:05:00Z",
            "text": "Maybe later, no pressure if timing shifts.",
        },
        {
            "message_id": "m3",
            "speaker_role": "self",
            "timestamp": "2026-01-02T10:00:00Z",
            "text": "I cannot share that.",
        },
        {
            "message_id": "m4",
            "speaker_role": "other",
            "timestamp": "2026-01-02T10:01:00Z",
            "text": "You have to answer right now.",
        },
        {
            "message_id": "m5",
            "speaker_role": "self",
            "timestamp": "2026-01-09T09:00:00Z",
            "text": "Sorry, let me rephrase the ask.",
        },
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    return path


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_parser_refuses_non_restricted_private_output(tmp_path: Path, capsys) -> None:
    _reset_restricted_test_root()
    messages = _write_messages(RESTRICTED_TEST_ROOT / "processed" / "private_messages_redacted.jsonl")

    exit_code = analyze_whatsapp_dynamics.main(
        [
            "--messages-jsonl",
            str(messages),
            "--output-dir",
            str(tmp_path / "public_reports"),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert RAW_SAMPLE_TEXT not in captured.out
    assert RAW_SAMPLE_TEXT not in captured.err


def test_report_contains_four_required_headings_and_no_raw_text_or_blocked_claims(capsys) -> None:
    _reset_restricted_test_root()
    messages = _write_messages(RESTRICTED_TEST_ROOT / "processed" / "private_messages_redacted.jsonl")
    output_dir = RESTRICTED_TEST_ROOT / "reports"

    exit_code = analyze_whatsapp_dynamics.main(["--messages-jsonl", str(messages), "--output-dir", str(output_dir)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert RAW_SAMPLE_TEXT not in captured.out
    assert RAW_SAMPLE_TEXT not in captured.err
    report_text = (output_dir / "whatsapp_dynamics_report.md").read_text(encoding="utf-8")
    assert [line for line in report_text.splitlines() if line.startswith("# ")] == REQUIRED_HEADINGS
    assert RAW_SAMPLE_TEXT not in report_text
    assert "No audio telemetry provided." in report_text
    lowered = report_text.lower()
    assert not any(claim in lowered for claim in BLOCKED_REPORT_CLAIMS)


def test_audio_matrix_schema_validation_works() -> None:
    _reset_restricted_test_root()
    messages = _write_messages(RESTRICTED_TEST_ROOT / "processed" / "private_messages_redacted.jsonl")
    audio = RESTRICTED_TEST_ROOT / "audio" / "bad_audio.csv"
    audio.parent.mkdir(parents=True, exist_ok=True)
    with audio.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["audio_id", "message_id", "speaker_role"])
        writer.writeheader()
        writer.writerow({"audio_id": "a1", "message_id": "m1", "speaker_role": "self"})

    exit_code = analyze_whatsapp_dynamics.main(
        [
            "--messages-jsonl",
            str(messages),
            "--audio-matrix",
            str(audio),
            "--output-dir",
            str(RESTRICTED_TEST_ROOT / "reports"),
        ]
    )

    assert exit_code == 1


def test_audio_matrix_must_be_restricted(tmp_path: Path) -> None:
    _reset_restricted_test_root()
    messages = _write_messages(RESTRICTED_TEST_ROOT / "processed" / "private_messages_redacted.jsonl")
    audio = tmp_path / "audio.csv"
    with audio.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(analyze_whatsapp_dynamics.AUDIO_COLUMNS))
        writer.writeheader()
        writer.writerow(
            {
                "audio_id": "a1",
                "message_id": "m1",
                "speaker_role": "self",
                "timestamp": "2026-01-01T10:00:00Z",
                "pitch_mean": "100",
                "pitch_std": "5",
                "energy_mean": "0.5",
                "voice_break_rate": "0.1",
                "pause_rate": "0.2",
                "wav2vec_cluster": "1",
                "valence_proxy": "0.5",
                "arousal_proxy": "0.8",
                "dominance_proxy": "0.4",
            }
        )

    exit_code = analyze_whatsapp_dynamics.main(
        [
            "--messages-jsonl",
            str(messages),
            "--audio-matrix",
            str(audio),
            "--output-dir",
            str(RESTRICTED_TEST_ROOT / "reports"),
        ]
    )

    assert exit_code == 1


def test_audio_success_reports_feature_divergence_without_feature_means() -> None:
    _reset_restricted_test_root()
    messages = _write_messages(RESTRICTED_TEST_ROOT / "processed" / "private_messages_redacted.jsonl")
    audio = RESTRICTED_TEST_ROOT / "audio" / "audio.csv"
    audio.parent.mkdir(parents=True, exist_ok=True)
    with audio.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(analyze_whatsapp_dynamics.AUDIO_COLUMNS))
        writer.writeheader()
        writer.writerow(
            {
                "audio_id": "a1",
                "message_id": "m4",
                "speaker_role": "other",
                "timestamp": "2026-01-02T10:01:00Z",
                "pitch_mean": "100",
                "pitch_std": "5",
                "energy_mean": "0.5",
                "voice_break_rate": "0.1",
                "pause_rate": "0.2",
                "wav2vec_cluster": "1",
                "valence_proxy": "0.5",
                "arousal_proxy": "0.2",
                "dominance_proxy": "0.4",
            }
        )
    output_dir = RESTRICTED_TEST_ROOT / "reports"

    exit_code = analyze_whatsapp_dynamics.main(
        ["--messages-jsonl", str(messages), "--audio-matrix", str(audio), "--output-dir", str(output_dir)]
    )

    assert exit_code == 0
    payload = json.loads((output_dir / "whatsapp_dynamics_report.json").read_text(encoding="utf-8"))
    rendered = json.dumps(payload)
    assert "feature_divergence" in rendered
    assert "text and audio features point in different directions" in rendered
    assert "pitch_mean_mean" not in rendered
    assert "valence_proxy_mean" not in rendered
    assert "arousal_proxy_mean" not in rendered
    assert "dominance_proxy_mean" not in rendered


def test_synthetic_fixture_export_does_not_copy_raw_text(tmp_path: Path) -> None:
    aggregate_report = tmp_path / "whatsapp_dynamics_report.json"
    aggregate_report.write_text(
        json.dumps(
            {
                "report_type": "whatsapp_dynamics_research",
                "top_aggregate_cue_categories": {"pressure_urgency": 2, "repair_reassurance": 1},
                "raw_private_phrase": RAW_SAMPLE_TEXT,
            }
        ),
        encoding="utf-8",
    )
    output_dir = ROOT / "data" / "synthetic" / "private_inspired" / "test_whatsapp_dynamics"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output = output_dir / "dynamics_fixtures.jsonl"

    try:
        exit_code = export_synthetic_dynamics_fixtures.main(["--input", str(aggregate_report), "--output", str(output)])

        assert exit_code == 0
        rows = _read_jsonl(output)
        assert len(rows) >= 60
        payload = output.read_text(encoding="utf-8")
        assert RAW_SAMPLE_TEXT not in payload
        assert all(row["synthetic"] is True and row["not_copied_from_real_chat"] is True for row in rows)
    finally:
        if output_dir.exists():
            shutil.rmtree(output_dir)


def test_synthetic_fixture_export_refuses_non_synthetic_output(tmp_path: Path) -> None:
    aggregate_report = tmp_path / "whatsapp_dynamics_report.json"
    aggregate_report.write_text(json.dumps({"top_aggregate_cue_categories": {}}), encoding="utf-8")

    exit_code = export_synthetic_dynamics_fixtures.main(["--input", str(aggregate_report), "--output", str(tmp_path / "out.jsonl")])

    assert exit_code == 1


def test_baseline_trainer_refuses_non_restricted_private_input(tmp_path: Path) -> None:
    private_review = tmp_path / "private_review.csv"
    private_review.write_text("text,label\nhello,boundary\n", encoding="utf-8")

    exit_code = train_private_dynamics_baseline.main(["--input", str(private_review)])

    assert exit_code == 1


def test_baseline_trainer_refuses_public_report_for_restricted_review_csv(tmp_path: Path) -> None:
    _reset_restricted_test_root()
    review_csv = RESTRICTED_TEST_ROOT / "processed" / "private_label_review.csv"
    review_csv.parent.mkdir(parents=True, exist_ok=True)
    review_csv.write_text("text,cue_id\nsynthetic review text,boundary\n", encoding="utf-8")

    exit_code = train_private_dynamics_baseline.main(["--input", str(review_csv), "--report-out", str(tmp_path / "report.md")])

    assert exit_code == 1
