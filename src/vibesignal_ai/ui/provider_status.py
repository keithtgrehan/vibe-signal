"""Frontend-safe provider readiness payloads."""

from __future__ import annotations

from typing import Any

from ..safety.validator import assert_safe_payload

STATUS_COPY = {
    "local_only": (
        "Local-only default",
        "Local deterministic analysis is active and no external provider will be called.",
    ),
    "provider_disabled": (
        "Provider disabled",
        "This provider path is off, so summaries stay local-only.",
    ),
    "provider_not_configured": (
        "Provider not configured",
        "This provider path is enabled in concept, but the provider details are not fully configured yet.",
    ),
    "secure_storage_unavailable": (
        "Secure storage unavailable",
        "Secure on-device storage is required before a BYOK credential can be saved for this provider.",
    ),
    "provider_enabled_no_credential": (
        "Credential needed",
        "Secure storage is available, but no provider credential is currently stored on-device.",
    ),
    "provider_ready": (
        "Provider ready",
        "This provider can be requested explicitly, while local analysis still remains the default path.",
    ),
    "provider_error": (
        "Provider error",
        "The provider path hit an error and no external summary should be treated as available.",
    ),
}


def determine_provider_status(
    *,
    provider_mode: str = "local_only",
    provider_name: str = "none",
    enabled: bool = False,
    auth_mode: str = "disabled",
    secure_storage_available: bool = False,
    credential_present: bool = False,
    error_message: str = "",
) -> str:
    normalized_mode = str(provider_mode or "local_only").strip() or "local_only"
    normalized_name = str(provider_name or "none").strip().lower() or "none"
    normalized_auth = str(auth_mode or "disabled").strip() or "disabled"

    if str(error_message or "").strip():
        return "provider_error"
    if normalized_mode == "local_only":
        return "local_only"
    if normalized_mode == "provider_disabled" or not enabled or normalized_auth == "disabled":
        return "provider_disabled"
    if normalized_name in {"", "none"}:
        return "provider_not_configured"
    if normalized_auth == "byok" and not secure_storage_available:
        return "secure_storage_unavailable"
    if normalized_auth == "byok" and not credential_present:
        return "provider_enabled_no_credential"
    if normalized_auth in {"byok", "backend_proxy"}:
        return "provider_ready"
    return "provider_not_configured"


def build_provider_status_payload(
    *,
    provider_name: str,
    display_name: str | None = None,
    enabled: bool,
    auth_mode: str,
    provider_mode: str = "local_only",
    model_name: str = "",
    secure_storage_available: bool = False,
    credential_present: bool = False,
    external_processing_used: bool = False,
    local_first_default: bool = True,
    error_message: str = "",
    status_override: str | None = None,
) -> dict[str, Any]:
    status = str(status_override or "").strip() or determine_provider_status(
        provider_mode=provider_mode,
        provider_name=provider_name,
        enabled=enabled,
        auth_mode=auth_mode,
        secure_storage_available=secure_storage_available,
        credential_present=credential_present,
        error_message="",
    )
    label, default_message = STATUS_COPY[status]
    payload = {
        "provider_name": str(provider_name or "none").strip().lower() or "none",
        "display_name": str(display_name or provider_name or "Provider").strip() or "Provider",
        "enabled": bool(enabled),
        "auth_mode": str(auth_mode or "disabled").strip() or "disabled",
        "status": status,
        "status_label": label,
        "status_message": str(error_message or default_message).strip() or default_message,
        "secure_storage_available": bool(secure_storage_available),
        "credential_present": bool(credential_present),
        "requires_secure_storage": str(auth_mode or "").strip() == "byok",
        "local_first_default": bool(local_first_default),
        "external_processing_used": bool(external_processing_used),
        "model_name": str(model_name or "").strip(),
        "can_request_summary": status == "provider_ready",
        "safe_to_render": True,
    }
    assert_safe_payload(payload)
    return payload
