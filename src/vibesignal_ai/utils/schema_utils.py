"""Utilities for resilient JSON parsing and normalized summary payloads."""

from __future__ import annotations

import json
import re
from typing import Any

_SUMMARY_KEYS = ("summary", "observations", "limitations")
_WRAPPER_KEYS = ("summary", "result", "data", "output")


def strip_markdown_fences(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""

    direct = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", value, flags=re.IGNORECASE)
    if direct:
        return direct.group(1).strip()

    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", value, flags=re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    return value


def extract_json_object(text: str) -> str | None:
    content = str(text or "")
    if not content:
        return None

    start: int | None = None
    depth = 0
    in_string = False
    escaped = False

    for idx, char in enumerate(content):
        if start is None:
            if char == "{":
                start = idx
                depth = 1
            continue

        if in_string:
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return content[start : idx + 1]

    return None


def _default_summary_payload(reason: str) -> dict[str, Any]:
    return {
        "summary": "Optional summary unavailable; rely on deterministic artifacts.",
        "observations": [],
        "limitations": [reason],
    }


def _unwrap_payload(payload: dict[str, Any]) -> dict[str, Any]:
    current = dict(payload)
    for _ in range(4):
        if len(current) == 1:
            key = next(iter(current))
            candidate = current.get(key)
            if key in _WRAPPER_KEYS and isinstance(candidate, dict):
                current = candidate
                continue
        break
    return current


def safe_json_loads(text: str) -> Any:
    raw = str(text or "")
    cleaned = strip_markdown_fences(raw)
    candidates: list[str] = []

    if cleaned:
        candidates.append(cleaned)
        extracted = extract_json_object(cleaned)
        if extracted:
            candidates.append(extracted)

    extracted_raw = extract_json_object(raw)
    if extracted_raw:
        candidates.append(extracted_raw)

    seen: set[str] = set()
    for candidate in candidates:
        token = candidate.strip()
        if not token or token in seen:
            continue
        seen.add(token)
        try:
            parsed = json.loads(token)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return _unwrap_payload(parsed)
        return parsed

    return _default_summary_payload("LLM/provider output could not be parsed as JSON.")


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [
            item
            for item in (part.strip("- •\t ") for part in re.split(r"\n+|;", value))
            if item
        ]
    if isinstance(value, dict):
        return [
            f"{str(key).strip()}: {str(item).strip()}"
            for key, item in value.items()
            if str(key).strip() and str(item).strip()
        ]
    return []


def normalize_summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return _default_summary_payload("Invalid summary payload type.")

    source = _unwrap_payload(payload)
    aliases: dict[str, tuple[str, ...]] = {
        "summary": (
            "summary",
            "overview",
            "narrative",
            "executive_summary",
            "executiveSummary",
            "conclusion",
        ),
        "observations": (
            "observations",
            "highlights",
            "key_signals",
            "signals",
            "key_points",
            "insights",
        ),
        "limitations": ("limitations", "caveats", "notes", "assumptions"),
    }
    normalized: dict[str, Any] = {"summary": "", "observations": [], "limitations": []}

    for canonical, keys in aliases.items():
        selected: Any = None
        for key in keys:
            if key in source and source[key] is not None:
                selected = source[key]
                break
        if selected is None:
            continue
        if canonical == "summary":
            text = str(selected).strip()
            if text:
                normalized["summary"] = text
        else:
            normalized[canonical] = _as_str_list(selected)

    if not normalized["summary"]:
        normalized["summary"] = "Optional summary unavailable; rely on deterministic artifacts."
    if not normalized["limitations"]:
        normalized["limitations"] = ["Provider output omitted limitations."]
    return normalized
