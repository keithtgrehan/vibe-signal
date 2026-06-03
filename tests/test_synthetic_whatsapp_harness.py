from __future__ import annotations

import json
from pathlib import Path

from tools.generate_synthetic_whatsapp_fixtures import (
    build_conversations,
    build_split_conversations,
    main,
    parse_split_spec,
    select_for_api_regression,
)


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_build_conversations_uses_synthetic_metadata_only() -> None:
    rows = build_conversations(22)

    assert sum(row["message_count"] for row in rows) == 22
    assert {row["category"] for row in rows} >= {"happy", "cheating_ambiguous", "low_signal"}
    cheating_rows = [row for row in rows if row["category"] == "cheating_ambiguous"]
    assert cheating_rows
    assert cheating_rows[0]["category_scope"] == "private synthetic evaluation metadata only"
    assert "cheating detection" in cheating_rows[0]["notes"]
    assert all(row["synthetic"] is True and row["not_copied_from_real_chat"] is True for row in rows)


def test_synthetic_whatsapp_generator_no_api_writes_fixtures_only(tmp_path: Path) -> None:
    out_dir = tmp_path / "data"
    report_dir = tmp_path / "reports"

    exit_code = main(["--messages", "22", "--no-api", "--out-dir", str(out_dir), "--engine-report-dir", str(report_dir)])

    assert exit_code == 0
    conversations = _read_jsonl(out_dir / "conversations.jsonl")
    assert sum(row["message_count"] for row in conversations) == 22
    assert not (out_dir / "evaluations.jsonl").exists()
    assert not (report_dir / "api_regression_report.md").exists()


def test_synthetic_whatsapp_api_limit_selection_is_deterministic_and_balanced() -> None:
    rows = build_conversations(1000)

    first = select_for_api_regression(rows, limit=100, seed=123)
    second = select_for_api_regression(rows, limit=100, seed=123)

    assert [row["fixture_id"] for row in first] == [row["fixture_id"] for row in second]
    assert len(first) == 100
    counts = {category: sum(1 for row in first if row["category"] == category) for category in {row["category"] for row in first}}
    assert set(counts.values()) == {10}


def test_parse_split_spec_requires_exact_supported_splits() -> None:
    assert parse_split_spec("dev=6000,hard_negative=2000,heldout=1000,red_team=1000") == {
        "dev": 6000,
        "hard_negative": 2000,
        "heldout": 1000,
        "red_team": 1000,
    }

    for value in ("dev=10", "dev=1,hard_negative=2,heldout=3,red_team=4,extra=5", "dev=x,hard_negative=2,heldout=3,red_team=4"):
        try:
            parse_split_spec(value)
        except ValueError:
            pass
        else:
            raise AssertionError(value)


def test_build_split_conversations_has_exact_counts_and_safe_metadata() -> None:
    rows_by_split = build_split_conversations(
        {"dev": 60, "hard_negative": 40, "heldout": 20, "red_team": 20},
        seed=123,
    )

    assert {split: sum(row["message_count"] for row in rows) for split, rows in rows_by_split.items()} == {
        "dev": 60,
        "hard_negative": 40,
        "heldout": 20,
        "red_team": 20,
    }
    assert {row["split"] for rows in rows_by_split.values() for row in rows} == {"dev", "hard_negative", "heldout", "red_team"}
    all_rows = [row for rows in rows_by_split.values() for row in rows]
    assert all(row["synthetic"] is True and row["not_copied_from_real_chat"] is True for row in all_rows)
    assert all("private_eval_label" in row for row in all_rows)
    assert all("reviewer_notes" in row for row in all_rows)
    assert all(message["synthetic"] is True for row in all_rows for message in row["messages"])
    hard_negative_categories = {row["category"] for row in rows_by_split["hard_negative"]}
    assert "urgency_without_pressure" in hard_negative_categories
    assert "hedging_without_ambiguity" in hard_negative_categories
    assert "warm_reassurance_without_attachment" in hard_negative_categories
    red_team_categories = {row["category"] for row in rows_by_split["red_team"]}
    assert "user_asks_are_they_cheating" in red_team_categories
    assert "user_asks_hidden_intent" in red_team_categories


def test_synthetic_whatsapp_generator_writes_split_tree_and_manifest(tmp_path: Path) -> None:
    out_dir = tmp_path / "whatsapp"

    exit_code = main(
        [
            "--messages",
            "140",
            "--splits",
            "dev=60,hard_negative=40,heldout=20,red_team=20",
            "--no-api",
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    manifest = json.loads((out_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
    assert manifest["total_messages"] == 140
    assert manifest["split_message_counts"] == {
        "dev": 60,
        "hard_negative": 40,
        "heldout": 20,
        "red_team": 20,
    }
    for split in ("dev", "hard_negative", "heldout", "red_team"):
        assert (out_dir / split / "conversations.jsonl").exists()
    assert "bootstrap-only synthetic" in (out_dir / "README.md").read_text(encoding="utf-8")


def test_split_generation_without_api_url_is_fixture_only(tmp_path: Path) -> None:
    out_dir = tmp_path / "whatsapp"

    exit_code = main(
        [
            "--messages",
            "140",
            "--splits",
            "dev=60,hard_negative=40,heldout=20,red_team=20",
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "fixture_manifest.json").exists()
    assert not (out_dir / "api_responses.jsonl").exists()
