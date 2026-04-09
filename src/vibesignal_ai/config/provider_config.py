"""Provider configuration interfaces for local-first optional connectors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import provider_flags

PROVIDER_DEFAULTS = {
    "openai": {
        "display_name": "OpenAI",
        "model_name": "gpt-4.1-mini",
        "base_url": "https://api.openai.com/v1",
        "timeout_seconds": 30,
    },
    "anthropic": {
        "display_name": "Anthropic",
        "model_name": "claude-3-5-haiku-latest",
        "base_url": "https://api.anthropic.com",
        "timeout_seconds": 30,
    },
    "groq": {
        "display_name": "Groq",
        "model_name": "llama-3.1-8b-instant",
        "base_url": "https://api.groq.com/openai/v1",
        "timeout_seconds": 30,
    },
}

PROVIDER_FLAG_MAP = {
    "openai": "ENABLE_OPENAI_PROVIDER",
    "anthropic": "ENABLE_ANTHROPIC_PROVIDER",
    "groq": "ENABLE_GROQ_PROVIDER",
}


@dataclass(frozen=True)
class ProviderConfig:
    provider_name: str
    display_name: str
    enabled: bool
    auth_mode: str
    model_name: str
    base_url: str
    timeout_seconds: int
    credential_present: bool
    secure_storage_available: bool
    secure_storage_used_for_provider_auth: bool
    api_key_secret: str | None = None

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "auth_mode": self.auth_mode,
            "model_name": self.model_name,
            "base_url": self.base_url,
            "timeout_seconds": self.timeout_seconds,
            "credential_present": self.credential_present,
            "secure_storage_available": self.secure_storage_available,
            "secure_storage_used_for_provider_auth": self.secure_storage_used_for_provider_auth,
        }


def allowed_provider_names() -> list[str]:
    return sorted(PROVIDER_DEFAULTS)


def allowed_auth_modes() -> list[str]:
    return ["byok", "backend_proxy", "disabled"]


def _provider_flag_enabled(provider_name: str) -> bool:
    flag_name = PROVIDER_FLAG_MAP.get(provider_name)
    if not flag_name:
        return False
    return bool(getattr(provider_flags, flag_name, False))


def load_provider_config(
    provider_name: str,
    *,
    auth_mode: str = "disabled",
    model_name: str | None = None,
    base_url: str | None = None,
    timeout_seconds: int | None = None,
    credential_present: bool = False,
    secure_storage_available: bool = False,
    api_key_secret: str | None = None,
) -> ProviderConfig:
    normalized = str(provider_name or "").strip().lower()
    defaults = PROVIDER_DEFAULTS.get(normalized, {})
    enabled = (
        bool(provider_flags.ENABLE_EXTERNAL_PROVIDERS)
        and bool(_provider_flag_enabled(normalized))
        and auth_mode != "disabled"
        and normalized in PROVIDER_DEFAULTS
    )
    auth_mode_normalized = auth_mode if auth_mode in allowed_auth_modes() else "disabled"
    secure_storage_used = auth_mode_normalized == "byok" and bool(secure_storage_available)
    return ProviderConfig(
        provider_name=normalized or "none",
        display_name=str(defaults.get("display_name", normalized.title() or "Provider")).strip(),
        enabled=enabled,
        auth_mode=auth_mode_normalized,
        model_name=str(model_name or defaults.get("model_name", "")).strip(),
        base_url=str(base_url or defaults.get("base_url", "")).strip(),
        timeout_seconds=int(timeout_seconds or defaults.get("timeout_seconds", 30)),
        credential_present=bool(credential_present),
        secure_storage_available=bool(secure_storage_available),
        secure_storage_used_for_provider_auth=bool(secure_storage_used),
        api_key_secret=str(api_key_secret).strip() if api_key_secret else None,
    )


def disabled_provider_config(provider_name: str = "none") -> ProviderConfig:
    normalized = str(provider_name or "none").strip().lower() or "none"
    defaults = PROVIDER_DEFAULTS.get(normalized, {})
    return ProviderConfig(
        provider_name=normalized,
        display_name=str(defaults.get("display_name", normalized.title() or "Provider")).strip(),
        enabled=False,
        auth_mode="disabled",
        model_name=str(defaults.get("model_name", "")).strip(),
        base_url=str(defaults.get("base_url", "")).strip(),
        timeout_seconds=int(defaults.get("timeout_seconds", 30)),
        credential_present=False,
        secure_storage_available=False,
        secure_storage_used_for_provider_auth=False,
        api_key_secret=None,
    )


def secure_storage_requirements() -> list[str]:
    return [
        "BYOK credentials must be stored in iOS Keychain or Android secure encrypted storage.",
        "If secure storage is unavailable, credential saving must fail closed.",
        "Disconnecting a provider must delete the stored credential.",
        "Provider-owned backend proxy keys must never be stored in the mobile client.",
    ]
