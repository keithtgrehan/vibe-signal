"""Flags for optional external provider connectors."""

from __future__ import annotations

import os


def _env_flag(name: str, *, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_EXTERNAL_PROVIDERS = _env_flag("VIBESIGNAL_ENABLE_EXTERNAL_PROVIDERS", default=False)
ENABLE_OPENAI_PROVIDER = _env_flag("VIBESIGNAL_ENABLE_OPENAI_PROVIDER", default=False)
ENABLE_ANTHROPIC_PROVIDER = _env_flag("VIBESIGNAL_ENABLE_ANTHROPIC_PROVIDER", default=False)
ENABLE_GROQ_PROVIDER = _env_flag("VIBESIGNAL_ENABLE_GROQ_PROVIDER", default=False)


def provider_flags_snapshot() -> dict[str, bool]:
    return {
        "enable_external_providers": bool(ENABLE_EXTERNAL_PROVIDERS),
        "enable_openai_provider": bool(ENABLE_OPENAI_PROVIDER),
        "enable_anthropic_provider": bool(ENABLE_ANTHROPIC_PROVIDER),
        "enable_groq_provider": bool(ENABLE_GROQ_PROVIDER),
    }
