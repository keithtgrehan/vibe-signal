from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_synthetic_vibe_match_pairs.py"
VALIDATOR = ROOT / "scripts" / "validate_vibe_match_pairs.py"
CORPUS = ROOT / "data" / "vibe_matching" / "synthetic" / "synthetic_match_pairs.jsonl"


REQUIRED_FEATURES = {
    "clarity_fit",
    "boundary_fit",
    "repair_fit",
    "communication_fit",
    "pressure_risk",
    "cognitive_load_fit",
    "inconsistency_cues",
    "unsupported_claim_shift",
    "specificity_drop",
    "answer_evasion_pattern",
    "contradiction_against_prior_message",
}
REQUIRED_CATEGORIES = {
    "strong_fit",
    "moderate_fit",
    "mixed_fit",
    "low_fit",
    "high_pressure",
    "low_pressure",
    "specificity",
    "vague_reply",
    "specificity_drop",
    "contradiction",
    "unsupported_claim_shift",
    "answer_evasion",
    "overload",
    "repair",
    "consent_clarity",
    "boundary_respect",
    "boundary_pressure",
}


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def test_committed_synthetic_match_corpus_validates_and_covers_required_categories() -> None:
    result = run_script(VALIDATOR, "--input", str(CORPUS))

    assert result.returncode == 0, result.stdout + result.stderr
    rows = load_jsonl(CORPUS)
    assert len(rows) >= 150
    assert REQUIRED_CATEGORIES <= {category for row in rows for category in row["categories"]}
    for row in rows:
        assert row["source_type"] == "synthetic_fixture"
        assert REQUIRED_FEATURES == set(row["features"])
        assert row["provenance"]["synthetic"] is True
        assert row["provenance"]["not_copied_from_real_chat"] is True
        assert row["blocked_interpretations"] == ["deception", "attraction", "diagnosis", "hidden_intent"]


def test_generator_writes_deterministic_valid_corpus(tmp_path: Path) -> None:
    out = tmp_path / "synthetic_match_pairs.jsonl"
    generate = run_script(GENERATOR, "--out", str(out), "--count", "150")
    validate = run_script(VALIDATOR, "--input", str(out))

    assert generate.returncode == 0, generate.stdout + generate.stderr
    assert validate.returncode == 0, validate.stdout + validate.stderr
    rows = load_jsonl(out)
    assert len(rows) == 150
    assert rows[0]["pair_id"] == "synthetic_001"


def test_validator_rejects_missing_provenance_and_unsafe_labels(tmp_path: Path) -> None:
    bad = {
        "pair_id": "bad_001",
        "source_type": "synthetic_fixture",
        "text_a": "Can you confirm Friday?",
        "text_b": "They lied.",
        "label": "deception",
        "label_value": 1,
        "evidence": ["They lied."],
        "features": {feature: 0 for feature in REQUIRED_FEATURES},
        "blocked_interpretations": ["deception", "attraction", "diagnosis", "hidden_intent"],
    }
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps(bad) + "\n", encoding="utf-8")

    result = run_script(VALIDATOR, "--input", str(path))

    assert result.returncode == 1
    assert "missing provenance" in result.stderr
    assert "unsafe label" in result.stderr


def test_validator_rejects_private_or_copied_dataset_markers_and_non_binary_features(tmp_path: Path) -> None:
    bad = {
        "pair_id": "bad_002",
        "source_type": "synthetic_fixture",
        "text_a": "WhatsApp export from my real ex",
        "text_b": "Copied from DailyDialog row 7",
        "label": "communication_fit",
        "label_value": 1,
        "evidence": ["specific evidence"],
        "features": {feature: 0 for feature in REQUIRED_FEATURES},
        "blocked_interpretations": ["deception", "attraction", "diagnosis", "hidden_intent"],
        "provenance": {"created_by": "codex", "not_copied_from_real_chat": True, "synthetic": True},
    }
    bad["features"]["communication_fit"] = 2
    path = tmp_path / "bad_markers.jsonl"
    path.write_text(json.dumps(bad) + "\n", encoding="utf-8")

    result = run_script(VALIDATOR, "--input", str(path))

    assert result.returncode == 1
    assert "private chat marker" in result.stderr
    assert "copied dataset marker" in result.stderr
    assert "feature communication_fit must be binary" in result.stderr
