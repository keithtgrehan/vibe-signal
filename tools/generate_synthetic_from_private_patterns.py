#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATS = REPO_ROOT / "data" / "restricted" / "private_whatsapp" / "processed" / "private_label_review_100_stats.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "synthetic" / "private_inspired" / "cue_fixtures.jsonl"
DEFAULT_REPORT = REPO_ROOT / "reports" / "engine_eval" / "private_inspired_synthetic_fixture_summary.md"
CUE_TYPES = (
    "ambiguity",
    "unclear_timing",
    "direct_ask",
    "unanswered_ask_candidate",
    "pressure_urgency",
    "boundary",
    "reassurance",
    "repair_attempt",
    "escalation_risk",
    "cognitive_load",
    "soft_commitment",
    "specificity_drop",
)
BLOCKED_RE = re.compile(
    r"\b(?:secretly|hidden intent|cheating|lying|deception|diagnos|neurotype|attachment style|manipulat|attraction|dating score)\b",
    re.IGNORECASE,
)


def read_stats(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _messages(cue_type: str, index: int) -> list[dict[str, str]]:
    variants: dict[str, list[list[dict[str, str]]]] = {
        "ambiguity": [
            [{"role": "self", "text": "Should we choose the plan today?"}, {"role": "other", "text": "Maybe, I am not fully sure yet."}],
            [{"role": "self", "text": "Can we decide the next step?"}, {"role": "other", "text": "Let's see, it depends on a few things."}],
        ],
        "unclear_timing": [
            [{"role": "self", "text": "When should we check in?"}, {"role": "other", "text": "Sometime later, not sure yet."}],
            [{"role": "self", "text": "Are we still planning to talk?"}, {"role": "other", "text": "At some point today maybe."}],
        ],
        "direct_ask": [
            [{"role": "self", "text": "Can you confirm the next step?"}, {"role": "other", "text": "Yes, I can confirm it after lunch."}],
            [{"role": "self", "text": "Could we pick one option now?"}, {"role": "other", "text": "Yes, let's pick the simpler option."}],
        ],
        "unanswered_ask_candidate": [
            [{"role": "self", "text": "Can you answer the schedule question?"}, {"role": "other", "text": "Anyway, the other task changed."}],
            [{"role": "self", "text": "Could you confirm the plan by noon?"}, {"role": "other", "text": "Maybe later, I need to check something else."}],
        ],
        "pressure_urgency": [
            [{"role": "self", "text": "I need the answer right now."}, {"role": "other", "text": "I need a moment to think."}],
            [{"role": "self", "text": "You have to reply immediately."}, {"role": "other", "text": "Please leave room for a later answer."}],
        ],
        "boundary": [
            [{"role": "self", "text": "I cannot do that tonight."}, {"role": "other", "text": "Okay, tomorrow is fine."}],
            [{"role": "self", "text": "I am not comfortable sharing that."}, {"role": "other", "text": "Understood, we can choose another option."}],
        ],
        "reassurance": [
            [{"role": "self", "text": "Can you review it when you can? No rush."}, {"role": "other", "text": "Yes, I can look later."}],
            [{"role": "self", "text": "No pressure if today is too full."}, {"role": "other", "text": "Thanks, I can respond tomorrow."}],
        ],
        "repair_attempt": [
            [{"role": "self", "text": "My bad, I should have said that more clearly."}, {"role": "other", "text": "Thanks for clarifying."}],
            [{"role": "self", "text": "Can we reset and start again?"}, {"role": "other", "text": "Yes, please restate the ask."}],
        ],
        "escalation_risk": [
            [{"role": "self", "text": "You have to answer right now!!"}, {"role": "other", "text": "Let's pause before this gets louder."}],
            [{"role": "self", "text": "This keeps happening and it is ridiculous!!"}, {"role": "other", "text": "I want to slow down and clarify one point."}],
        ],
        "cognitive_load": [
            [{"role": "self", "text": "Can you check the plan, the note, the time, the task list, and whether the next step still works?"}, {"role": "other", "text": "Please send one request first."}],
            [{"role": "self", "text": "I need to compare the file, schedule, reminder, context, and backup option before deciding."}, {"role": "other", "text": "Let's split that into two items."}],
        ],
        "soft_commitment": [
            [{"role": "self", "text": "Can you make it today?"}, {"role": "other", "text": "I think I can, but I will confirm later."}],
            [{"role": "self", "text": "Are we set for the check-in?"}, {"role": "other", "text": "Probably, I just need to verify one thing."}],
        ],
        "specificity_drop": [
            [{"role": "other", "text": "I can send it by 4pm."}, {"role": "other", "text": "Actually, maybe later sometime."}],
            [{"role": "self", "text": "Could you confirm the plan by noon?"}, {"role": "other", "text": "Maybe later, not sure yet."}],
        ],
    }
    return variants[cue_type][index % len(variants[cue_type])]


def safe_next_step(cue_type: str) -> str:
    return {
        "ambiguity": "Ask for the missing detail in one direct sentence.",
        "unclear_timing": "Ask for a specific confirmation window.",
        "direct_ask": "Keep the request concrete and leave room for a clear yes or no.",
        "unanswered_ask_candidate": "Restate the original question once without adding pressure.",
        "pressure_urgency": "Slow down the timing request and add room to decline or delay.",
        "boundary": "Acknowledge the stated limit before suggesting another option.",
        "reassurance": "Keep the low-pressure wording and name the next step.",
        "repair_attempt": "Use the reset opening to restate the ask clearly.",
        "escalation_risk": "Pause and move to one calmer clarification.",
        "cognitive_load": "Split the message into one next action.",
        "soft_commitment": "Ask what would make the commitment specific.",
        "specificity_drop": "Ask for the missing time, plan, or constraint.",
    }[cue_type]


def build_fixtures() -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    for cue_type in CUE_TYPES:
        for index in range(10):
            fixtures.append(
                {
                    "fixture_id": f"private_inspired_{cue_type}_{index + 1:02d}",
                    "source": "private_inspired_synthetic",
                    "cue_type": cue_type,
                    "messages": _messages(cue_type, index),
                    "expected": {
                        "cue_type": cue_type,
                        "evidence_hint": cue_type.replace("_", " "),
                        "safe_next_step": safe_next_step(cue_type),
                    },
                    "blocked_claim_check": True,
                }
            )
    hard_negatives = [
        ("clear_yes", [{"role": "self", "text": "Can you confirm the plan?"}, {"role": "other", "text": "Yes, that works."}]),
        ("clear_no", [{"role": "self", "text": "Can you take this on?"}, {"role": "other", "text": "No, I cannot take it on today."}]),
        ("clear_timing", [{"role": "self", "text": "When can you reply?"}, {"role": "other", "text": "I can reply by 4pm."}]),
        ("warm_not_committed", [{"role": "self", "text": "Can you join?"}, {"role": "other", "text": "Thanks for asking, I need to check first."}]),
        ("delayed_respectful", [{"role": "self", "text": "Can you answer now?"}, {"role": "other", "text": "I cannot answer now, but I can reply after lunch."}]),
        ("short_clear", [{"role": "self", "text": "Does this work?"}, {"role": "other", "text": "Yes."}]),
    ]
    for name, messages in hard_negatives:
        fixtures.append(
            {
                "fixture_id": f"private_inspired_hard_negative_{name}",
                "source": "private_inspired_synthetic",
                "cue_type": "hard_negative",
                "messages": messages,
                "expected": {
                    "cue_type": "hard_negative",
                    "evidence_hint": "clear wording",
                    "safe_next_step": "No cue action needed beyond normal clarification if desired.",
                },
                "blocked_claim_check": True,
            }
        )
    return fixtures


def validate_fixture_text(fixtures: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for fixture in fixtures:
        for message in fixture["messages"]:
            text = str(message["text"])
            if BLOCKED_RE.search(text):
                errors.append(f"{fixture['fixture_id']}: blocked wording")
            if re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text):
                errors.append(f"{fixture['fixture_id']}: possible real name")
    return errors


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def build_report(fixtures: list[dict[str, Any]], stats: dict[str, Any]) -> str:
    counts: dict[str, int] = {}
    for fixture in fixtures:
        counts[str(fixture["cue_type"])] = counts.get(str(fixture["cue_type"]), 0) + 1
    lines = [f"- `{cue}`: `{count}`" for cue, count in sorted(counts.items())]
    source_counts = stats.get("candidate_label_counts", {})
    source_lines = [f"- `{cue}`: `{count}`" for cue, count in sorted(source_counts.items())] or ["- No aggregate stats provided."]
    return "\n".join(
        [
            "# Private-Inspired Synthetic Fixture Summary",
            "",
            "Synthetic fixtures are hand-authored from aggregate cue patterns only. They do not copy private text, names, dates, or locations.",
            "",
            f"- Fixture count: `{len(fixtures)}`",
            f"- Cue types: `{len(counts)}`",
            "",
            "## Fixture Counts",
            "",
            *lines,
            "",
            "## Aggregate Source Pattern Counts",
            "",
            *source_lines,
            "",
            "These fixtures are not validation data, model-quality proof, or production-readiness evidence.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic cue fixtures from aggregate private-label patterns.")
    parser.add_argument("--stats", default=str(DEFAULT_STATS), help="Aggregate restricted stats JSON. Raw private text is not read.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--report-out", default=str(DEFAULT_REPORT))
    args = parser.parse_args(argv)

    stats = read_stats(Path(args.stats))
    fixtures = build_fixtures()
    errors = validate_fixture_text(fixtures)
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 2
    write_jsonl(Path(args.output), fixtures)
    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(fixtures, stats), encoding="utf-8")
    print(json.dumps({"status": "complete", "fixture_count": len(fixtures)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
