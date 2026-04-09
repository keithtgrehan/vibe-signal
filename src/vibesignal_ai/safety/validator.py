"""Safety validation for UI and optional summary outputs."""

from __future__ import annotations

import re
from typing import Any

from .banned_terms import BANNED_PATTERNS, BANNED_TERMS

SOFT_VERDICT_TRIGGERS = (
    r"\bthis suggests\b",
    r"\bthis indicates\b",
    r"\bthis implies\b",
    r"\bthis means\b",
    r"\bthis points to\b",
    r"\bevidence of\b",
    r"\bstrong sign of\b",
    r"\bappears to show\b",
)
SOFT_VERDICT_TARGETS = (
    r"intent",
    r"motive",
    r"secret",
    r"hidden",
    r"dishonest",
    r"deceptive",
    r"guilty",
    r"innocent",
    r"toxic",
    r"abusive",
    r"affair",
    r"cheat",
    r"truth",
    r"lie",
    r"job",
    r"interview",
    r"pass",
    r"fail",
    r"hired",
    r"rejected",
)


def find_banned_terms(text: str) -> list[str]:
    lowered = str(text or "").lower()
    matches = []
    for term in sorted(BANNED_TERMS):
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, lowered):
            matches.append(term)
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, lowered):
            matches.append(pattern)
    return matches


def find_soft_verdict_language(text: str) -> list[str]:
    lowered = str(text or "").lower()
    matches: list[str] = []
    for trigger in SOFT_VERDICT_TRIGGERS:
        for target in SOFT_VERDICT_TARGETS:
            pattern = trigger + r"(?:\W+\w+){0,6}\W+" + target
            if re.search(pattern, lowered):
                matches.append(pattern)
    return matches


def validate_text(text: str, *, field_name: str = "text") -> list[str]:
    banned_matches = find_banned_terms(text)
    soft_matches = find_soft_verdict_language(text)
    errors: list[str] = []
    if banned_matches:
        errors.append(
            f"{field_name} contains banned output language: {', '.join(banned_matches)}"
        )
    if soft_matches:
        errors.append(
            f"{field_name} contains implication-heavy verdict phrasing: {', '.join(soft_matches)}"
        )
    return errors


def validate_payload(payload: Any, *, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            errors.extend(validate_payload(value, path=f"{path}.{key}"))
        return errors
    if isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(validate_payload(value, path=f"{path}[{index}]"))
        return errors
    if isinstance(payload, str):
        errors.extend(validate_text(payload, field_name=path))
    return errors


def assert_safe_payload(payload: Any) -> None:
    errors = validate_payload(payload)
    if errors:
        raise RuntimeError("; ".join(errors))
