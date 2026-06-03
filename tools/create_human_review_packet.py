#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

try:
    from tools import generate_synthetic_whatsapp_fixtures as generator
except ImportError:  # pragma: no cover - exercised when run as a script.
    import generate_synthetic_whatsapp_fixtures as generator


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "synthetic" / "whatsapp" / "conversations.jsonl"
DEFAULT_INPUT_ROOT = REPO_ROOT / "data" / "synthetic" / "whatsapp"
DEFAULT_PACKET = REPO_ROOT / "data" / "review" / "seed_review_packet.jsonl"
DEFAULT_BOOTSTRAP_LABELS = REPO_ROOT / "data" / "review" / "seed_reviewed_labels.jsonl"
DEFAULT_V2_PACKET = REPO_ROOT / "data" / "review" / "human_review_packet_v2.jsonl"
DEFAULT_V2_BOOTSTRAP_LABELS = REPO_ROOT / "data" / "review" / "human_review_packet_v2_bootstrap_labels.jsonl"
DEFAULT_LIMIT = 50
DEFAULT_SEED = 20260603
V2_SPLIT_TARGETS = {"dev": 40, "hard_negative": 25, "heldout": 20, "red_team": 15}
CUE_UNIVERSE = (
    "alignment",
    "ambiguity",
    "answer_evasion_pattern",
    "boundary_pressure",
    "cognitive_load",
    "conflict",
    "contradiction_against_prior_message",
    "directness",
    "escalation_risk",
    "hedging",
    "overloaded_message",
    "pressure",
    "reassurance",
    "repair_opportunity",
    "specificity",
    "specificity_drop",
    "topic_shift",
    "unclear_ask",
    "urgency",
    "unsupported_claim_shift",
)
REVIEWER_INSTRUCTIONS_V2 = [
    "Review observable wording only.",
    "Do not label hidden intent.",
    "Do not label cheating.",
    "Do not label attraction.",
    "Do not diagnose.",
    "Do not infer true emotion.",
    "Do not infer attachment style or neurotype.",
    "Mark bootstrap labels as suggestions only, not human-reviewed labels.",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def select_balanced(rows: list[dict[str, Any]], *, limit: int, seed: int) -> list[dict[str, Any]]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    rng = random.Random(int(seed))
    by_category: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_category.setdefault(str(row["category"]), []).append(row)
    for bucket in by_category.values():
        rng.shuffle(bucket)
    categories = sorted(by_category)
    selected: list[dict[str, Any]] = []
    while len(selected) < limit:
        made_progress = False
        for category in categories:
            bucket = by_category.get(category) or []
            if bucket:
                selected.append(bucket.pop(0))
                made_progress = True
                if len(selected) == limit:
                    break
        if not made_progress:
            break
    return sorted(selected, key=lambda row: str(row["fixture_id"]))


def build_packet_rows(conversations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, conversation in enumerate(conversations, start=1):
        rows.append(
            {
                "review_packet_id": f"seed_review_{index:04d}",
                "fixture_id": conversation["fixture_id"],
                "source_type": "synthetic_fixture",
                "synthetic": True,
                "not_copied_from_real_chat": True,
                "category": conversation["category"],
                "category_scope": conversation["category_scope"],
                "messages": conversation["messages"],
                "candidate_cues": list(CUE_UNIVERSE),
                "fixture_expected_cues": conversation["expected_cues"],
                "review_instructions": [
                    "Review observable wording only.",
                    "Do not label hidden intent, cheating, attraction, diagnosis, true emotion, attachment style, or neurotype.",
                    "Mark evidence only when the visible text supports the cue.",
                ],
            }
        )
    return rows


def build_bootstrap_labels(conversations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels: list[dict[str, Any]] = []
    for conversation in conversations:
        expected = set(str(cue) for cue in conversation["expected_cues"])
        evidence_text_by_cue = {
            cue: " | ".join(message["text"] for message in conversation["messages"])
            for cue in expected
        }
        for cue in CUE_UNIVERSE:
            present = cue in expected
            labels.append(
                {
                    "label_id": f"{conversation['fixture_id']}_{cue}",
                    "fixture_id": conversation["fixture_id"],
                    "source_type": "synthetic_fixture",
                    "reviewer": "synthetic_bootstrap",
                    "not_human_validated": True,
                    "cue_id": cue,
                    "cue_present": present,
                    "evidence_supports_cue": present,
                    "evidence_text": evidence_text_by_cue.get(cue, ""),
                    "unsafe_wording_flag": False,
                    "low_signal_flag": conversation["expected_result_type"] == "low_signal",
                    "notes": "Bootstrap label derived from synthetic fixture expectations; not human reviewed.",
                    "blocked_inference_guard": {
                        "no_hidden_intent": True,
                        "no_cheating": True,
                        "no_attraction": True,
                        "no_diagnosis": True,
                        "no_true_emotion": True,
                        "no_attachment_style_or_neurotype": True,
                    },
                }
            )
    return labels


def read_split_conversations(input_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in ("dev", "hard_negative", "heldout", "red_team"):
        rows.extend(read_jsonl(input_root / split / "conversations.jsonl"))
    return rows


def select_v2_balanced(rows: list[dict[str, Any]], *, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(int(seed))
    by_split: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_split.setdefault(str(row.get("split", "legacy")), []).append(row)
    selected: list[dict[str, Any]] = []
    for split, target in V2_SPLIT_TARGETS.items():
        bucket = list(by_split.get(split, []))
        if len(bucket) < target:
            raise ValueError(f"not enough rows for split {split}: {len(bucket)} < {target}")
        by_scenario: dict[str, list[dict[str, Any]]] = {}
        for row in bucket:
            by_scenario.setdefault(str(row.get("scenario", row.get("category", ""))), []).append(row)
        for scenario_rows in by_scenario.values():
            rng.shuffle(scenario_rows)
        scenarios = sorted(by_scenario)
        split_rows: list[dict[str, Any]] = []
        while len(split_rows) < target:
            made_progress = False
            for scenario in scenarios:
                scenario_rows = by_scenario.get(scenario) or []
                if scenario_rows:
                    split_rows.append(scenario_rows.pop(0))
                    made_progress = True
                    if len(split_rows) == target:
                        break
            if not made_progress:
                break
        selected.extend(split_rows)
    return sorted(selected, key=lambda row: (str(row.get("split", "")), str(row.get("fixture_id", ""))))


def build_packet_rows_v2(conversations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, conversation in enumerate(conversations, start=1):
        rows.append(
            {
                "review_id": f"human_review_v2_{index:04d}",
                "conversation_id": conversation["fixture_id"],
                "fixture_id": conversation["fixture_id"],
                "source_type": "synthetic_fixture",
                "synthetic": True,
                "not_copied_from_real_chat": True,
                "split": conversation.get("split", "legacy"),
                "scenario": conversation.get("scenario", conversation.get("category", "")),
                "private_eval_label": conversation.get("private_eval_label", conversation.get("category", "")),
                "messages": conversation["messages"],
                "candidate_cues": list(CUE_UNIVERSE),
                "bootstrap_expected_cues": conversation["expected_cues"],
                "bootstrap_labels_are_suggestions_only": True,
                "not_human_validated": True,
                "review_instructions": REVIEWER_INSTRUCTIONS_V2,
                "human_label_fields": {
                    "message_id_or_span_id": "",
                    "cue_id": "",
                    "cue_present": None,
                    "evidence_text": "",
                    "evidence_start": None,
                    "evidence_end": None,
                    "evidence_supports_cue": None,
                    "false_positive_reason": "",
                    "false_negative_reason": "",
                    "unsafe_wording_flag": None,
                    "low_signal_flag": None,
                    "reviewer_confidence": "low",
                    "reviewer": "",
                    "reviewed_at": "",
                    "notes": "",
                },
            }
        )
    return rows


def build_bootstrap_labels_v2(conversations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels: list[dict[str, Any]] = []
    for conversation in conversations:
        expected = {str(cue) for cue in conversation["expected_cues"]}
        evidence_text = " | ".join(message["text"] for message in conversation["messages"])
        for cue in CUE_UNIVERSE:
            present = cue in expected
            labels.append(
                {
                    "label_id": f"{conversation['fixture_id']}_{cue}",
                    "review_id": f"bootstrap_suggestion_{conversation['fixture_id']}_{cue}",
                    "fixture_id": conversation["fixture_id"],
                    "conversation_id": conversation["fixture_id"],
                    "split": conversation.get("split", "legacy"),
                    "scenario": conversation.get("scenario", conversation.get("category", "")),
                    "message_id": "",
                    "span_id": "",
                    "source_type": "synthetic_fixture",
                    "reviewer": "synthetic_bootstrap",
                    "not_human_validated": True,
                    "bootstrap_suggestion_only": True,
                    "cue_id": cue,
                    "cue_present": present,
                    "evidence_supports_cue": present,
                    "evidence_text": evidence_text if present else "",
                    "evidence_start": 0 if present else None,
                    "evidence_end": len(evidence_text) if present else None,
                    "false_positive_reason": "",
                    "false_negative_reason": "",
                    "unsafe_wording_flag": False,
                    "low_signal_flag": conversation["expected_result_type"] == "low_signal",
                    "reviewer_confidence": "low",
                    "reviewed_at": "",
                    "notes": "Bootstrap suggestion derived from synthetic fixture expectations; not human reviewed.",
                    "blocked_inference_guard": {
                        "no_hidden_intent": True,
                        "no_cheating": True,
                        "no_attraction": True,
                        "no_diagnosis": True,
                        "no_true_emotion": True,
                        "no_attachment_style_or_neurotype": True,
                    },
                }
            )
    return labels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a synthetic seed packet for future human cue-label review.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--input-root", default=str(DEFAULT_INPUT_ROOT))
    parser.add_argument("--output", default=str(DEFAULT_PACKET))
    parser.add_argument("--bootstrap-labels-output", default=str(DEFAULT_BOOTSTRAP_LABELS))
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--v2", action="store_true")
    args = parser.parse_args(argv)

    if args.v2:
        conversations = read_split_conversations(Path(args.input_root))
        selected = select_v2_balanced(conversations, seed=int(args.seed))
        packet_rows = build_packet_rows_v2(selected)
        bootstrap_labels = build_bootstrap_labels_v2(selected)
        if args.output == str(DEFAULT_PACKET):
            args.output = str(DEFAULT_V2_PACKET)
        if args.bootstrap_labels_output == str(DEFAULT_BOOTSTRAP_LABELS):
            args.bootstrap_labels_output = str(DEFAULT_V2_BOOTSTRAP_LABELS)
    else:
        conversations = read_jsonl(Path(args.input))
        selected = select_balanced(conversations, limit=int(args.limit), seed=int(args.seed))
        packet_rows = build_packet_rows(selected)
        bootstrap_labels = build_bootstrap_labels(selected)
    write_jsonl(Path(args.output), packet_rows)
    write_jsonl(Path(args.bootstrap_labels_output), bootstrap_labels)
    print(
        json.dumps(
            {
                "status": "review_packet_created",
                "packet_rows": len(packet_rows),
                "bootstrap_label_rows": len(bootstrap_labels),
                "reviewed_label_status": "bootstrap",
                "not_human_validated": True,
                "output": str(Path(args.output)),
                "bootstrap_labels_output": str(Path(args.bootstrap_labels_output)),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
