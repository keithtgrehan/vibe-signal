"""Structured provider consent payloads for future UI flows."""

from __future__ import annotations

from typing import Any

from ..config.provider_config import secure_storage_requirements
from ..safety.validator import assert_safe_payload

_DISCLOSURE_TEMPLATES = {
    "openai": "Local analysis stays on device by default. If you enable OpenAI, the selected structured signals and any excerpt you choose will be sent to OpenAI for an external AI summary.",
    "anthropic": "Local analysis stays on device by default. If you enable Anthropic, the selected structured signals and any excerpt you choose will be sent to Anthropic for an external AI summary.",
    "groq": "Local analysis stays on device by default. If you enable Groq, the selected structured signals and any excerpt you choose will be sent to Groq for an external AI summary.",
}


def build_provider_consent_payload(
    provider_name: str,
    *,
    auth_mode: str = "disabled",
) -> dict[str, Any]:
    normalized = str(provider_name or "").strip().lower()
    payload = {
        "provider_name": normalized,
        "auth_mode": auth_mode,
        "title": f"{normalized.title()} External AI Consent" if normalized else "External AI Consent",
        "summary": _DISCLOSURE_TEMPLATES.get(
            normalized,
            "Local analysis stays on device by default. If you enable an external provider, only the selected content should be sent.",
        ),
        "bullets": [
            "Local deterministic analysis stays on device by default.",
            "Only selected content should be sent to the chosen provider when external mode is enabled.",
            "Submit only content you have the right to use.",
            "Provider credentials are stored securely on-device when supported.",
            "The provider can be disconnected later.",
        ],
        "secure_storage_requirements": secure_storage_requirements(),
    }
    assert_safe_payload(payload)
    return payload


def list_provider_consent_payloads() -> list[dict[str, Any]]:
    return [
        build_provider_consent_payload("openai", auth_mode="byok"),
        build_provider_consent_payload("anthropic", auth_mode="byok"),
        build_provider_consent_payload("groq", auth_mode="byok"),
    ]
