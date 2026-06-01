"""Deterministic communication-fit matching engine."""

from __future__ import annotations

from .contracts import normalize_match_request, validate_match_request, validate_match_result
from .deterministic_matcher import match_conversation

__all__ = [
    "match_conversation",
    "normalize_match_request",
    "validate_match_request",
    "validate_match_result",
]
