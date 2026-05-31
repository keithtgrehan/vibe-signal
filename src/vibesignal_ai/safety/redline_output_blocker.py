"""Deterministic red-line blocker for user-facing Vibe outputs."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
POLICY_PATH = ROOT / "redline_policy.json"
PHRASES_PATH = ROOT / "blocked_phrases.yml"


def _load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _load_phrases() -> dict[str, Any]:
    return yaml.safe_load(PHRASES_PATH.read_text(encoding="utf-8")) or {}


def _safe_replacement(categories: list[str]) -> str:
    policy = _load_policy()
    category_map = policy.get("categories", {})
    for category in categories:
        replacement = category_map.get(category, {}).get("safe_replacement")
        if replacement:
            return str(replacement)
    return "Use neutral communication-pattern language with evidence spans."


def find_redline_categories(text: str) -> list[str]:
    lowered = str(text or "").lower()
    config = _load_phrases()
    categories: list[str] = []

    for row in config.get("phrases", []) or []:
        phrase = str(row.get("phrase", "")).lower().strip()
        category = str(row.get("category", "")).strip()
        if phrase and category and phrase in lowered and category not in categories:
            categories.append(category)

    for row in config.get("regexes", []) or []:
        pattern = str(row.get("pattern", "")).strip()
        category = str(row.get("category", "")).strip()
        if pattern and category and re.search(pattern, lowered, flags=re.IGNORECASE) and category not in categories:
            categories.append(category)

    return categories


def check_output_text(text: str) -> dict[str, Any]:
    categories = find_redline_categories(text)
    if categories:
        return {
            "status": "block",
            "categories": categories,
            "safe_replacement": _safe_replacement(categories),
        }
    return {"status": "allow", "categories": [], "safe_replacement": ""}


def validate_output_text(text: str, *, field_name: str = "text") -> list[str]:
    result = check_output_text(text)
    if result["status"] == "allow":
        return []
    categories = ", ".join(result["categories"])
    return [f"{field_name} contains red-line output category: {categories}"]
