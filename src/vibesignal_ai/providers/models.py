"""Typed data models for optional external provider calls."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderPromptPayload:
    provider_name: str
    system_prompt: str
    user_prompt: str
    content_source: str
    signal_bundle: dict[str, Any]
    selected_excerpts: list[str]

    def to_safe_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderExecutionResult:
    provider_name: str
    model_name: str
    output_text: str
    raw_response_meta: dict[str, Any]
    external_processing_used: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderValidationResult:
    provider_name: str
    model_name: str
    status: str
    ready: bool
    user_message: str
    auth_mode: str
    secure_storage_available: bool
    credential_present: bool
    consent_confirmed: bool
    timeout_seconds: int
    http_status: int | None = None
    error_code: str = ""

    def to_safe_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderGateResult:
    provider_name: str
    allowed: bool
    status: str
    user_message: str
    requires_consent: bool
    secure_storage_available: bool
    credential_present: bool
    validation_status: str

    def to_safe_dict(self) -> dict[str, Any]:
        return asdict(self)
