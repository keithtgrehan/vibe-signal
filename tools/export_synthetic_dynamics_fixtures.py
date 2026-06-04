#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "restricted" / "private_whatsapp" / "reports" / "whatsapp_dynamics_report.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "synthetic" / "private_inspired" / "dynamics_fixtures.jsonl"
DEFAULT_SEED = 20260605
SYNTHETIC_ROOT = REPO_ROOT / "data" / "synthetic" / "private_inspired"


@dataclass(frozen=True)
class Template:
    category: str
    cue_labels: tuple[str, ...]
    messages: tuple[tuple[str, str], ...]
    notes: str


TEMPLATES: tuple[Template, ...] = (
    Template(
        "unclear_timing",
        ("unclear_timing",),
        (("self", "Can we choose a time soon?"), ("other", "Maybe later, not sure yet.")),
        "Synthetic vague timing exchange.",
    ),
    Template(
        "unclear_timing",
        ("unclear_timing", "direct_ask"),
        (("other", "When should we decide?"), ("self", "Sometime after I check.")),
        "Synthetic ask with unclear timing.",
    ),
    Template(
        "response_asymmetry",
        ("response_imbalance",),
        (("self", "Can you review one item?"), ("self", "Following up on the review."), ("self", "Please send only a yes or no.")),
        "Synthetic consecutive-message run.",
    ),
    Template(
        "response_asymmetry",
        ("response_imbalance", "low_signal"),
        (("other", "ok"), ("self", "Can you add more context?"), ("other", "later")),
        "Synthetic short reply imbalance.",
    ),
    Template(
        "pressure_urgency",
        ("pressure_urgency",),
        (("self", "Please answer when you can."), ("other", "You have to answer right now.")),
        "Synthetic pressure-style wording.",
    ),
    Template(
        "pressure_urgency",
        ("pressure_urgency", "direct_ask"),
        (("other", "Can you decide now?"), ("other", "This needs a reply immediately.")),
        "Synthetic urgency stack.",
    ),
    Template(
        "repair_opportunity",
        ("repair_reassurance",),
        (("self", "That came out too strong."), ("self", "Sorry, let me rephrase the ask.")),
        "Synthetic repair opening.",
    ),
    Template(
        "repair_opportunity",
        ("repair_reassurance", "direct_ask"),
        (("other", "I asked too many things."), ("other", "Can we reset with one question?")),
        "Synthetic repair with a clear ask.",
    ),
    Template(
        "boundary",
        ("boundary",),
        (("self", "I am not available for that."), ("other", "Thanks for saying the limit clearly.")),
        "Synthetic boundary-respecting exchange.",
    ),
    Template(
        "boundary",
        ("boundary", "pressure_urgency"),
        (("self", "I cannot share that detail."), ("other", "You must explain right now.")),
        "Synthetic boundary plus pressure wording.",
    ),
    Template(
        "reassurance",
        ("repair_reassurance",),
        (("other", "No rush on this."), ("self", "Thanks, I will send a short update.")),
        "Synthetic reassurance wording.",
    ),
    Template(
        "reassurance",
        ("repair_reassurance", "direct_ask"),
        (("self", "Can you check this when you have space?"), ("other", "No pressure, I can check one item.")),
        "Synthetic lower-pressure request.",
    ),
    Template(
        "hard_negative",
        ("direct_ask",),
        (("self", "Can you send one update?"), ("other", "Yes, one update is enough.")),
        "Synthetic clear ask without pressure.",
    ),
    Template(
        "hard_negative",
        ("repair_reassurance",),
        (("other", "No worries."), ("self", "Thanks for clarifying.")),
        "Synthetic reassurance without relationship inference.",
    ),
    Template(
        "hard_negative",
        ("boundary",),
        (("self", "I cannot join that."), ("other", "That is okay.")),
        "Synthetic boundary without conflict.",
    ),
)


def _load_aggregate(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _weights_from_aggregate(payload: dict[str, Any]) -> dict[str, int]:
    counts = payload.get("top_aggregate_cue_categories", {})
    if not isinstance(counts, dict):
        return {}
    weights: dict[str, int] = {}
    for key, value in counts.items():
        try:
            weights[str(key)] = max(1, min(10, int(float(value))))
        except (TypeError, ValueError):
            weights[str(key)] = 1
    return weights


def build_fixtures(payload: dict[str, Any], *, count: int = 60, seed: int = DEFAULT_SEED) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    weights = _weights_from_aggregate(payload)
    templates = list(TEMPLATES)
    rows: list[dict[str, Any]] = []
    required_categories = ["unclear_timing", "response_asymmetry", "pressure_urgency", "repair_opportunity", "boundary", "reassurance", "hard_negative"]
    for category in required_categories:
        template = next(item for item in templates if item.category == category)
        rows.append(_row_from_template(template, len(rows) + 1))
    while len(rows) < count:
        weighted_templates: list[Template] = []
        for template in templates:
            weight = 1 + sum(weights.get(label, 0) for label in template.cue_labels)
            weighted_templates.extend([template] * max(1, weight))
        rows.append(_row_from_template(rng.choice(weighted_templates), len(rows) + 1))
    return rows


def _row_from_template(template: Template, index: int) -> dict[str, Any]:
    text = " ".join(message for _, message in template.messages)
    return {
        "fixture_id": f"synthetic_dynamics_{index:04d}",
        "synthetic": True,
        "not_copied_from_real_chat": True,
        "source": "aggregate-pattern-inspired synthetic fixture",
        "category": template.category,
        "weak_label": template.category,
        "cue_labels": list(template.cue_labels),
        "speaker_roles": ["self", "other"],
        "messages": [{"speaker_role": role, "text": message, "synthetic": True} for role, message in template.messages],
        "text": text,
        "notes": template.notes,
        "privacy_note": "No names, dates, locations, private references, or copied private phrases.",
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.expanduser().resolve().relative_to(root.expanduser().resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export synthetic WhatsApp dynamics fixtures from aggregate-only reports.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--count", type=int, default=60)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)

    payload = _load_aggregate(Path(args.input).expanduser().resolve())
    rows = build_fixtures(payload, count=max(60, args.count), seed=args.seed)
    output = Path(args.output).expanduser().resolve()
    if not _is_under(output, SYNTHETIC_ROOT):
        print("Refusing synthetic fixture output outside data/synthetic/private_inspired.", file=sys.stderr)
        return 1
    write_jsonl(output, rows)
    print(json.dumps({"status": "ok", "synthetic_fixture_count": len(rows), "output": str(output)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
