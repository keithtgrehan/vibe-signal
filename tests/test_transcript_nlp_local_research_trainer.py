from __future__ import annotations

import json
from pathlib import Path

from scripts.train_transcript_nlp_local_research_baseline import main as train_main
from tools.transcript_nlp_local_research_common import GOEMOTIONS_SOURCE_TIER, build_local_research_row


def _synthetic_row(index: int, split: str, cues: list[str], text: str) -> dict[str, object]:
    evidence = []
    for cue in cues:
        if cue not in {"low_signal", "neutral"}:
            evidence.append({"cue_type": cue, "span": text[:40], "explanation": "Synthetic cue span."})
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


def _synthetic_rows() -> list[dict[str, object]]:
    return [
        _synthetic_row(1, "dev", ["directness", "specificity"], "Can you confirm Friday at 3pm?"),
        _synthetic_row(2, "dev", ["ambiguity"], "Maybe later, not sure yet."),
        _synthetic_row(3, "dev", ["pressure", "urgency"], "You have to answer right now."),
        _synthetic_row(4, "dev", ["reassurance"], "No pressure if you need more time."),
        _synthetic_row(5, "hard_negative", ["directness", "specificity"], "Can you send it by 5pm? No stress if not."),
        _synthetic_row(6, "heldout", ["ambiguity"], "Maybe sometime later."),
        _synthetic_row(7, "red_team", ["low_signal"], "Do they mean something secret?"),
        _synthetic_row(8, "red_team", ["neutral"], "Good morning."),
    ]


def _augmentation_rows() -> list[dict[str, object]]:
    return [
        build_local_research_row(
            source_tier=GOEMOTIONS_SOURCE_TIER,
            row_number=1,
            source_row_id="a",
            split="train",
            text="Can you explain why this happened?",
            labels=["confusion"],
            expected_cues=["directness"],
            evidence_spans=[
                {"cue_type": "directness", "span": "Can you explain", "explanation": "Observable direct request."}
            ],
        ),
        build_local_research_row(
            source_tier=GOEMOTIONS_SOURCE_TIER,
            row_number=2,
            source_row_id="b",
            split="validation",
            text="Thank you, that makes sense.",
            labels=["gratitude"],
            expected_cues=["reassurance", "alignment"],
            evidence_spans=[
                {"cue_type": "reassurance", "span": "Thank you", "explanation": "Observable reassurance-like wording."},
                {"cue_type": "alignment", "span": "makes sense", "explanation": "Observable alignment wording."},
            ],
        ),
    ]


def test_combined_trainer_fails_in_commercial_mode(tmp_path: Path) -> None:
    synthetic = tmp_path / "synthetic.jsonl"
    _write_rows(synthetic, _synthetic_rows())

    assert train_main(["--synthetic-input", str(synthetic), "--project-mode", "commercial"]) == 1


def test_combined_trainer_writes_reports_without_artifact_by_default(tmp_path: Path) -> None:
    synthetic = tmp_path / "synthetic.jsonl"
    augmentation = tmp_path / "goemotions.jsonl"
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"
    _write_rows(synthetic, _synthetic_rows())
    _write_rows(augmentation, _augmentation_rows())

    exit_code = train_main(
        [
            "--synthetic-input",
            str(synthetic),
            "--augmentation-input",
            f"goemotions:{augmentation}",
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
    assert payload["provider_calls_made"] is False
    assert payload["external_embeddings_used"] is False
    assert payload["public_dataset_rows_committed"] is False
    assert payload["deterministic_engine_remains_primary"] is True
    assert "bronze_synthetic_whatsapp_10k" in payload["metrics"]["sources"]
    assert GOEMOTIONS_SOURCE_TIER in payload["metrics"]["sources"]
    assert "dev" in payload["metrics"]["splits"]
    assert "hard_negative_overfire_rate" in payload["metrics"]
    assert "red_team_unsafe_output_pass_rate" in payload["metrics"]

    markdown = report_md.read_text(encoding="utf-8")
    assert "development signals only" in markdown
    assert "deterministic cue engine remains primary" in markdown.lower()
    assert "Can you explain why this happened" not in markdown
    for blocked_phrase in (
        "production-grade",
        "hidden intent detection",
        "attraction prediction",
        "deception detection",
        "diagnosis detection",
        "manipulation detection",
        "relationship outcome prediction",
    ):
        assert blocked_phrase not in markdown.lower()
    assert not list(tmp_path.glob("*.joblib"))


def test_combined_trainer_restricts_optional_artifact_path(tmp_path: Path) -> None:
    synthetic = tmp_path / "synthetic.jsonl"
    _write_rows(synthetic, _synthetic_rows())

    assert (
        train_main(
            [
                "--synthetic-input",
                str(synthetic),
                "--project-mode",
                "research_only",
                "--local-artifact-out",
                str(tmp_path / "model.joblib"),
            ]
        )
        == 1
    )


def test_combined_trainer_can_write_local_only_artifact_under_local_artifacts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    synthetic = tmp_path / "synthetic.jsonl"
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"
    artifact = tmp_path / ".local_artifacts" / "transcript_nlp" / "model.joblib"
    _write_rows(synthetic, _synthetic_rows())

    exit_code = train_main(
        [
            "--synthetic-input",
            str(synthetic),
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
