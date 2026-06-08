from __future__ import annotations

import json
from pathlib import Path

from scripts.train_synthetic_whatsapp_pattern_baseline import main as train_main


NON_CLAIMS = (
    "Synthetic-only metrics are development signals only. They are not real-world validation, "
    "model-quality proof, production-readiness proof, legal/compliance approval, or a claim that "
    "Vibe Signal can infer hidden intent, attraction, deception, diagnosis, manipulation, abuse, "
    "or relationship outcomes."
)


def _row(index: int, split: str, cues: list[str], text: str) -> dict[str, object]:
    evidence = []
    for cue in cues:
        if cue not in {"low_signal", "neutral"}:
            evidence.append({"cue_type": cue, "span": text.split(": ", 1)[-1][:40], "explanation": "Synthetic cue span."})
    return {
        "row_id": f"synthetic_whatsapp_{index:06d}",
        "conversation_id": f"fixture_{index:03d}",
        "source_tier": "bronze_synthetic_whatsapp_10k",
        "source_type": "synthetic_fixture",
        "rights_review_status": "synthetic_only",
        "consent_status": "not_required_synthetic",
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_raw_private_text": False,
        "contains_personal_data": False,
        "redaction_status": "synthetic",
        "review_status": "synthetic_expected",
        "split": split,
        "scenario_family": "tiny_fixture",
        "synthetic": True,
        "not_copied_from_real_chat": True,
        "messages": [{"message_id": "m1", "speaker_role": "self", "text": text}],
        "text_for_training": f"self: {text}",
        "expected_cues": cues,
        "evidence_spans": evidence,
        "blocked_interpretations": [
            "hidden_intent",
            "attraction",
            "deception_certainty",
            "diagnosis",
            "therapy",
            "manipulation_claim",
            "relationship_outcome",
        ],
        "forbidden_outputs": [
            "they like you",
            "they are lying",
            "this proves",
            "hidden intent",
            "gaslighting",
            "manipulating you",
            "diagnosis",
            "attachment style",
            "narcissist",
            "abusive person",
            "make them respond",
            "win them back",
        ],
        "safe_summary": "The synthetic exchange contains observable wording cues.",
        "safe_next_step": "Ask one direct question or pause before replying.",
    }


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _training_rows() -> list[dict[str, object]]:
    return [
        _row(1, "dev", ["directness", "specificity"], "Can you confirm Friday at 3pm?"),
        _row(2, "dev", ["ambiguity"], "Maybe later, not sure yet."),
        _row(3, "dev", ["pressure", "urgency"], "You have to answer right now."),
        _row(4, "dev", ["reassurance"], "No pressure if you need more time."),
        _row(5, "hard_negative", ["directness", "specificity"], "Can you send it by 5pm? No stress if not."),
        _row(6, "heldout", ["ambiguity"], "Maybe sometime later."),
        _row(7, "red_team", ["low_signal"], "Do they mean something secret?"),
        _row(8, "red_team", ["neutral"], "Good morning."),
    ]


def test_trainer_fails_in_commercial_mode(tmp_path: Path) -> None:
    input_path = tmp_path / "rows.jsonl"
    _write_rows(input_path, _training_rows())

    assert train_main(["--input", str(input_path), "--project-mode", "commercial"]) == 1


def test_trainer_fails_on_non_synthetic_rows(tmp_path: Path) -> None:
    input_path = tmp_path / "rows.jsonl"
    rows = _training_rows()
    rows[0]["synthetic"] = False
    _write_rows(input_path, rows)

    assert train_main(["--input", str(input_path), "--project-mode", "research_only"]) == 1


def test_trainer_writes_report_but_no_model_artifact_by_default(tmp_path: Path) -> None:
    input_path = tmp_path / "rows.jsonl"
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"
    _write_rows(input_path, _training_rows())

    exit_code = train_main(
        [
            "--input",
            str(input_path),
            "--project-mode",
            "research_only",
            "--report-out",
            str(report_json),
            "--markdown-out",
            str(report_md),
        ]
    )

    assert exit_code == 0
    payload = json.loads(report_json.read_text(encoding="utf-8"))
    assert payload["project_mode"] == "research_only"
    assert payload["model_artifact_saved"] is False
    assert "all_sources_combined" in payload["metrics"]
    assert "bronze_synthetic_whatsapp_10k" in payload["metrics"]
    assert "dev" in payload["metrics"]["splits"]
    assert "hard_negative" in payload["metrics"]["splits"]
    assert "red_team" in payload["metrics"]["splits"]
    assert "hard_negative_overfire_rate" in payload["metrics"]
    assert "red_team_unsafe_output_pass_rate" in payload["metrics"]
    assert payload["deterministic_engine_remains_primary"] is True

    text = report_md.read_text(encoding="utf-8")
    assert NON_CLAIMS in text
    assert "deterministic cue engine remains primary" in text.lower()
    lower = text.lower()
    for blocked_phrase in (
        "production-grade",
        "attraction prediction",
        "deception detection",
        "manipulation detection",
        "relationship outcome prediction",
    ):
        assert blocked_phrase not in lower
    assert not list(tmp_path.glob("*.joblib"))


def test_trainer_local_artifact_path_must_be_under_local_artifacts(tmp_path: Path) -> None:
    input_path = tmp_path / "rows.jsonl"
    _write_rows(input_path, _training_rows())

    assert (
        train_main(
            [
                "--input",
                str(input_path),
                "--project-mode",
                "research_only",
                "--local-artifact-out",
                str(tmp_path / "model.joblib"),
            ]
        )
        == 1
    )


def test_trainer_can_write_optional_local_only_artifact_under_local_artifacts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = tmp_path / "rows.jsonl"
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"
    artifact = tmp_path / ".local_artifacts" / "pattern_baseline" / "model.joblib"
    _write_rows(input_path, _training_rows())

    exit_code = train_main(
        [
            "--input",
            str(input_path),
            "--project-mode",
            "research_only",
            "--report-out",
            str(report_json),
            "--markdown-out",
            str(report_md),
            "--local-artifact-out",
            str(artifact),
        ]
    )

    assert exit_code == 0
    assert artifact.exists()
    assert json.loads(report_json.read_text(encoding="utf-8"))["model_artifact_saved"] is True
