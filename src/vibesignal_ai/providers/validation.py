"""Provider validation helpers and error normalization."""

from __future__ import annotations

from typing import Any

from ..config.provider_config import ProviderConfig
from .models import ProviderValidationResult

VALIDATION_MESSAGES = {
    "ready": "The provider is ready to use.",
    "missing_credentials": "A stored API key is required before continuing.",
    "secure_storage_unavailable": "Secure storage is unavailable on this device.",
    "invalid_credentials": "The API key was rejected by the provider.",
    "provider_timeout": "The provider did not respond in time.",
    "rate_limited": "The provider rate limit was hit. Try again later.",
    "provider_unavailable": "The provider is unavailable right now.",
    "consent_required": "You must confirm provider consent before continuing.",
    "unknown_error": "The provider returned an unexpected error.",
}

VALIDATION_STATUSES = tuple(VALIDATION_MESSAGES)


def build_validation_result(
    *,
    config: ProviderConfig,
    status: str,
    user_message: str | None = None,
    ready: bool | None = None,
    consent_confirmed: bool = False,
    http_status: int | None = None,
    error_code: str = "",
) -> ProviderValidationResult:
    normalized_status = str(status or "unknown_error").strip() or "unknown_error"
    return ProviderValidationResult(
        provider_name=config.provider_name,
        model_name=config.model_name,
        status=normalized_status,
        ready=bool(ready if ready is not None else normalized_status == "ready"),
        user_message=str(user_message or VALIDATION_MESSAGES.get(normalized_status, VALIDATION_MESSAGES["unknown_error"])).strip(),
        auth_mode=config.auth_mode,
        secure_storage_available=bool(config.secure_storage_available),
        credential_present=bool(config.credential_present),
        consent_confirmed=bool(consent_confirmed),
        timeout_seconds=int(config.timeout_seconds),
        http_status=http_status,
        error_code=str(error_code or "").strip(),
    )


def _status_from_http(http_status: int | None) -> str | None:
    if http_status is None:
        return None
    if http_status in {401, 403}:
        return "invalid_credentials"
    if http_status == 429:
        return "rate_limited"
    if http_status in {408, 504}:
        return "provider_timeout"
    if http_status >= 500:
        return "provider_unavailable"
    return None


def map_provider_exception(exc: Exception) -> tuple[str, str, int | None, str]:
    text = str(exc or "").strip()
    lowered = text.lower()
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)

    status = _status_from_http(status_code)
    if status is not None:
        return status, VALIDATION_MESSAGES[status], status_code, text

    if any(token in lowered for token in ("timed out", "timeout", "deadline exceeded")):
        return "provider_timeout", VALIDATION_MESSAGES["provider_timeout"], status_code, text
    if any(token in lowered for token in ("rate limit", "too many requests")):
        return "rate_limited", VALIDATION_MESSAGES["rate_limited"], status_code, text
    if any(token in lowered for token in ("unauthorized", "invalid api key", "authentication", "forbidden")):
        return "invalid_credentials", VALIDATION_MESSAGES["invalid_credentials"], status_code, text
    if any(token in lowered for token in ("service unavailable", "connection error", "network", "temporarily unavailable")):
        return "provider_unavailable", VALIDATION_MESSAGES["provider_unavailable"], status_code, text
    return "unknown_error", VALIDATION_MESSAGES["unknown_error"], status_code, text
