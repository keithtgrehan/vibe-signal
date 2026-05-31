"""Deterministic communication-clarity support cards."""

from __future__ import annotations

import re
from typing import Any

from ..safety.validator import validate_payload


ASK_PATTERNS = (
    re.compile(r"\b(can|could|will|would)\s+you\b", re.IGNORECASE),
    re.compile(r"\bplease\b", re.IGNORECASE),
    re.compile(r"\bconfirm\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+(time|day|date|next)\b", re.IGNORECASE),
)
PRESSURE_PATTERNS = (
    re.compile(r"\byou\s+must\b", re.IGNORECASE),
    re.compile(r"\bneed\s+you\s+to\b", re.IGNORECASE),
    re.compile(r"\bright\s+now\b", re.IGNORECASE),
    re.compile(r"\bnow\s+or\s+else\b", re.IGNORECASE),
    re.compile(r"\bor\s+else\b", re.IGNORECASE),
    re.compile(r"\bif\s+you\s+do(?:n'?t| not)\b", re.IGNORECASE),
)


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", str(text or ""))


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", " ".join(str(text or "").split()))
    return [part.strip() for part in parts if part.strip()]


def _base_card(card_type: str, status: str, summary: str, observations: list[str], suggestion: str) -> dict[str, Any]:
    card = {
        "card_type": card_type,
        "status": status,
        "summary": summary,
        "observations": observations,
        "suggestion": suggestion,
        "limits": [
            "communication-pattern support only",
            "no identity or medical labels",
            "without guessing how the other person feels",
        ],
    }
    errors = validate_payload(card)
    if errors:
        return {
            "card_type": card_type,
            "status": "blocked",
            "summary": "This card was blocked by the safety validator.",
            "observations": [],
            "suggestion": "",
            "limits": ["communication-pattern support only"],
        }
    return card


def _empty(card_type: str) -> dict[str, Any]:
    return _base_card(card_type, "empty", "", [], "")


def _shorten(text: str, *, max_words: int = 24) -> str:
    words = _words(text)
    if not words:
        return ""
    shortened = " ".join(words[:max_words])
    return shortened.rstrip(" ,.;:") + ("." if not shortened.endswith((".", "?", "!")) else "")


def _clean_pressure(text: str) -> str:
    value = " ".join(str(text or "").split())
    replacements = (
        (r"\byou\s+must\b", "could you"),
        (r"\bneed\s+you\s+to\b", "could you"),
        (r"\bright\s+now\b", "when you can"),
        (r"\bnow\s+or\s+else\b", "when you can"),
        (r"\bor\s+else\b", ""),
        (r"\bthis will be a problem\b", "this will help me plan"),
    )
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    return " ".join(value.split()).strip(" ,.;") + "."


def detect_message_overload(text: str) -> dict[str, Any]:
    if not str(text or "").strip():
        return _empty("message_overload")
    words = _words(text)
    sentences = _sentences(text)
    observations: list[str] = []
    if len(words) >= 45:
        observations.append("The message is long enough that scanning may take extra effort.")
    if len(sentences) >= 3:
        observations.append("Several ideas appear in one message.")
    if str(text).count("?") >= 2:
        observations.append("Multiple questions appear together.")
    if not observations:
        observations.append("Length and structure look manageable.")
    return _base_card(
        "message_overload",
        "ok",
        "This may be easier to read if shortened.",
        observations,
        f"Shorter version: {_shorten(text)}",
    )


def detect_unclear_ask(text: str) -> dict[str, Any]:
    if not str(text or "").strip():
        return _empty("unclear_ask")
    explicit = any(pattern.search(text) for pattern in ASK_PATTERNS) or "?" in str(text)
    observations = ["The ask is explicit."] if explicit else ["No direct request wording was found."]
    return _base_card(
        "unclear_ask",
        "ok",
        "The ask is not explicit." if not explicit else "The ask is explicit.",
        observations,
        "A more direct version could be... Could you confirm the specific next step?",
    )


def detect_pressure_language(text: str) -> dict[str, Any]:
    if not str(text or "").strip():
        return _empty("pressure_language")
    matches = [pattern.pattern for pattern in PRESSURE_PATTERNS if pattern.search(text)]
    observations = ["Pressure-style wording appears."] if matches else ["No pressure-style wording was found."]
    return _base_card(
        "pressure_language",
        "ok" if matches else "empty",
        "A lower-pressure version could be clearer." if matches else "",
        observations,
        "A lower-pressure version could be... Could you reply when you have a moment?",
    )


def suggest_lower_pressure_rewrite(text: str) -> dict[str, Any]:
    if not str(text or "").strip():
        return _empty("lower_pressure_rewrite")
    cleaned = _clean_pressure(text)
    return _base_card(
        "lower_pressure_rewrite",
        "ok",
        "A lower-pressure version could be...",
        ["This keeps the request clearer and leaves room for the other person to respond."],
        f"A lower-pressure version could be... {cleaned}",
    )


def suggest_more_direct_rewrite(text: str) -> dict[str, Any]:
    if not str(text or "").strip():
        return _empty("more_direct_rewrite")
    first_sentence = _sentences(text)[0] if _sentences(text) else _shorten(text)
    return _base_card(
        "more_direct_rewrite",
        "ok",
        "A more direct version could be...",
        ["The ask can be placed at the start."],
        f"A more direct version could be... Could you confirm this: {first_sentence}",
    )


def suggest_literal_summary(text: str) -> dict[str, Any]:
    if not str(text or "").strip():
        return _empty("literal_summary")
    summary = _shorten(text, max_words=18)
    return _base_card(
        "literal_summary",
        "ok",
        "This keeps the message clearer without guessing how the other person feels.",
        ["The summary restates visible content only."],
        f"Literal summary: {summary}",
    )


def suggest_repair_message(context_text: str | None = None) -> dict[str, Any]:
    context = _shorten(context_text or "", max_words=12)
    suggestion = "I want to reset this clearly. My main ask is: can we confirm the next step?"
    if context:
        suggestion = f"I want to reset this clearly. Context: {context} My main ask is: can we confirm the next step?"
    return _base_card(
        "repair_message",
        "ok",
        "A repair message can make the ask explicit.",
        ["The message names the reset and asks for one next step."],
        suggestion,
    )
