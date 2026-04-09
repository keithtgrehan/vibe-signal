"""Provider manager for optional external AI summaries."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..config.provider_config import (
    ProviderConfig,
    disabled_provider_config,
    load_provider_config,
)
from ..safety.validator import assert_safe_payload
from ..ui.provider_status import build_provider_status_payload
from .anthropic_provider import AnthropicProvider
from .base import BaseProvider
from .groq_provider import GroqProvider
from .models import ProviderExecutionResult, ProviderGateResult, ProviderValidationResult
from .openai_provider import OpenAIProvider
from .prompt_builder import build_provider_prompt
from .validation import build_validation_result


def _provider_registry() -> dict[str, BaseProvider]:
    return {
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "groq": GroqProvider(),
    }


def _safe_summary_contract(
    *,
    config: ProviderConfig,
    content_source: str,
    output_text: str,
    external_processing_used: bool,
    safety_validated: bool,
) -> dict[str, Any]:
    payload = {
        "provider_name": config.provider_name,
        "auth_mode": config.auth_mode,
        "model_name": config.model_name,
        "content_source": content_source,
        "external_processing_used": bool(external_processing_used),
        "output_text": str(output_text or "").strip(),
        "output_label": "external_ai_summary",
        "safety_validated": bool(safety_validated),
    }
    assert_safe_payload(payload)
    return payload


class ProviderManager:
    def __init__(self, registry: dict[str, BaseProvider] | None = None) -> None:
        self.registry = registry or _provider_registry()

    def validate_provider_connection(
        self,
        *,
        provider_name: str | None,
        provider_auth_mode: str = "byok",
        provider_model_name: str | None = None,
        provider_base_url: str | None = None,
        provider_timeout_seconds: int | None = None,
        provider_api_key: str | None = None,
        provider_secure_storage_available: bool = False,
        provider_credential_present: bool | None = None,
        consent_confirmed: bool = False,
    ) -> ProviderValidationResult:
        normalized_name = str(provider_name or "").strip().lower()
        if not normalized_name:
            config = disabled_provider_config("none")
            return build_validation_result(
                config=config,
                status="missing_credentials",
                user_message="Choose a provider before continuing.",
                consent_confirmed=consent_confirmed,
            )

        credential_present = bool(provider_credential_present)
        if provider_api_key and provider_credential_present is None:
            credential_present = True

        config = load_provider_config(
            normalized_name,
            auth_mode=provider_auth_mode,
            model_name=provider_model_name,
            base_url=provider_base_url,
            timeout_seconds=provider_timeout_seconds,
            credential_present=credential_present,
            secure_storage_available=provider_secure_storage_available,
            api_key_secret=provider_api_key,
        )
        provider = self.registry.get(config.provider_name)
        if not consent_confirmed:
            return build_validation_result(
                config=config,
                status="consent_required",
                consent_confirmed=False,
            )
        if config.auth_mode != "byok":
            return build_validation_result(
                config=config,
                status="provider_unavailable",
                user_message="This mobile flow only supports BYOK provider authentication.",
                consent_confirmed=consent_confirmed,
            )
        if not config.secure_storage_available:
            return build_validation_result(
                config=config,
                status="secure_storage_unavailable",
                consent_confirmed=consent_confirmed,
            )
        if not config.credential_present or not config.api_key_secret:
            return build_validation_result(
                config=config,
                status="missing_credentials",
                consent_confirmed=consent_confirmed,
            )
        if not config.enabled or provider is None or not provider.is_available():
            return build_validation_result(
                config=config,
                status="provider_unavailable",
                consent_confirmed=consent_confirmed,
            )
        return provider.validate_credentials(config=config, consent_confirmed=consent_confirmed)

    def gate_external_summary_request(
        self,
        *,
        provider_name: str | None,
        consent_confirmed: bool,
        secure_storage_available: bool,
        credential_present: bool,
        validation_status: str,
    ) -> ProviderGateResult:
        normalized_name = str(provider_name or "").strip().lower()
        if not normalized_name:
            return ProviderGateResult(
                provider_name="none",
                allowed=False,
                status="provider_not_configured",
                user_message="Choose a provider before continuing.",
                requires_consent=True,
                secure_storage_available=bool(secure_storage_available),
                credential_present=bool(credential_present),
                validation_status=str(validation_status or "").strip(),
            )
        if not consent_confirmed:
            return ProviderGateResult(
                provider_name=normalized_name,
                allowed=False,
                status="consent_required",
                user_message="You must confirm provider consent before continuing.",
                requires_consent=True,
                secure_storage_available=bool(secure_storage_available),
                credential_present=bool(credential_present),
                validation_status=str(validation_status or "").strip(),
            )
        if not secure_storage_available:
            return ProviderGateResult(
                provider_name=normalized_name,
                allowed=False,
                status="secure_storage_unavailable",
                user_message="Secure storage is unavailable on this device.",
                requires_consent=True,
                secure_storage_available=False,
                credential_present=bool(credential_present),
                validation_status=str(validation_status or "").strip(),
            )
        if not credential_present:
            return ProviderGateResult(
                provider_name=normalized_name,
                allowed=False,
                status="missing_credentials",
                user_message="A stored API key is required before continuing.",
                requires_consent=True,
                secure_storage_available=True,
                credential_present=False,
                validation_status=str(validation_status or "").strip(),
            )
        if str(validation_status or "").strip() != "ready":
            return ProviderGateResult(
                provider_name=normalized_name,
                allowed=False,
                status=str(validation_status or "unknown_error").strip() or "unknown_error",
                user_message="Provider validation must succeed before continuing.",
                requires_consent=True,
                secure_storage_available=True,
                credential_present=True,
                validation_status=str(validation_status or "").strip(),
            )
        return ProviderGateResult(
            provider_name=normalized_name,
            allowed=True,
            status="ready",
            user_message="The provider is ready to use.",
            requires_consent=True,
            secure_storage_available=True,
            credential_present=True,
            validation_status="ready",
        )

    def run_optional_summary(
        self,
        *,
        provider_mode: str,
        provider_name: str | None,
        provider_auth_mode: str = "disabled",
        provider_model_name: str | None = None,
        provider_base_url: str | None = None,
        provider_timeout_seconds: int | None = None,
        provider_api_key: str | None = None,
        provider_secure_storage_available: bool = False,
        provider_credential_present: bool | None = None,
        signals: dict[str, Any],
        selected_excerpts: list[str] | None = None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        requested_mode = str(provider_mode or "local_only").strip() or "local_only"
        selected_excerpts = [str(item or "").strip() for item in (selected_excerpts or []) if str(item or "").strip()]
        credential_present = bool(provider_credential_present)
        if provider_api_key and provider_credential_present is None:
            credential_present = True

        if requested_mode == "local_only":
            status_payload = build_provider_status_payload(
                provider_name="none",
                display_name="Local-only",
                enabled=False,
                auth_mode="disabled",
                provider_mode="local_only",
            )
            return None, {
                "requested_provider_mode": "local_only",
                "provider_mode": "local_only",
                "provider_name": "none",
                "auth_mode": "disabled",
                "model_name": "",
                "content_source": "signals_only",
                "external_processing_used": False,
                "status": "local_only",
                "safety_validated": False,
                "error_message": "",
                "provider_available": False,
                "secure_storage_available": False,
                "secure_storage_used_for_provider_auth": False,
                "credential_present": False,
                "provider_status": status_payload,
                "local_result_primary": True,
                "external_summary_secondary": True,
                "result_origin": "local",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }

        if requested_mode == "provider_disabled":
            config = disabled_provider_config(provider_name or "none")
            status_payload = build_provider_status_payload(
                provider_name=config.provider_name,
                display_name=config.display_name,
                enabled=False,
                auth_mode=config.auth_mode,
                provider_mode="provider_disabled",
                model_name=config.model_name,
                status_override="provider_disabled",
            )
            return None, {
                "requested_provider_mode": "provider_disabled",
                "provider_mode": "provider_disabled",
                "provider_name": config.provider_name,
                "auth_mode": config.auth_mode,
                "model_name": config.model_name,
                "content_source": "signals_only",
                "external_processing_used": False,
                "status": "provider_disabled",
                "safety_validated": False,
                "error_message": "Provider mode was explicitly disabled.",
                "provider_available": False,
                "secure_storage_available": False,
                "secure_storage_used_for_provider_auth": False,
                "credential_present": False,
                "provider_status": status_payload,
                "local_result_primary": True,
                "external_summary_secondary": True,
                "result_origin": "local",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }

        config = load_provider_config(
            str(provider_name or "").strip().lower(),
            auth_mode=provider_auth_mode,
            model_name=provider_model_name,
            base_url=provider_base_url,
            timeout_seconds=provider_timeout_seconds,
            credential_present=credential_present,
            secure_storage_available=provider_secure_storage_available,
            api_key_secret=provider_api_key,
        )
        prompt_payload = build_provider_prompt(
            provider_name=config.provider_name,
            signals=signals,
            selected_excerpts=selected_excerpts,
        )
        status_payload = build_provider_status_payload(
            provider_name=config.provider_name,
            display_name=config.display_name,
            enabled=config.enabled,
            auth_mode=config.auth_mode,
            provider_mode="external_summary_optional",
            model_name=config.model_name,
            secure_storage_available=config.secure_storage_available,
            credential_present=config.credential_present,
        )
        meta = {
            "requested_provider_mode": requested_mode,
            "provider_mode": "external_summary_optional",
            "provider_name": config.provider_name,
            "display_name": config.display_name,
            "auth_mode": config.auth_mode,
            "model_name": config.model_name,
            "content_source": prompt_payload.content_source,
            "external_processing_used": False,
            "status": status_payload["status"],
            "safety_validated": False,
            "error_message": "",
            "provider_available": False,
            "secure_storage_available": config.secure_storage_available,
            "secure_storage_used_for_provider_auth": config.secure_storage_used_for_provider_auth,
            "credential_present": config.credential_present,
            "provider_status": status_payload,
            "local_result_primary": True,
            "external_summary_secondary": True,
            "result_origin": "local",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        provider = self.registry.get(config.provider_name)
        if not config.enabled or config.auth_mode == "disabled":
            meta["provider_mode"] = "provider_disabled"
            meta["error_message"] = "Provider is not enabled or not configured."
            meta["provider_status"] = build_provider_status_payload(
                provider_name=config.provider_name,
                display_name=config.display_name,
                enabled=False,
                auth_mode=config.auth_mode,
                provider_mode="provider_disabled",
                model_name=config.model_name,
                secure_storage_available=config.secure_storage_available,
                credential_present=config.credential_present,
                status_override="provider_disabled",
            )
            meta["status"] = meta["provider_status"]["status"]
            return None, meta
        if config.auth_mode == "byok" and not config.secure_storage_available:
            meta["provider_mode"] = "provider_disabled"
            meta["status"] = "secure_storage_unavailable"
            meta["error_message"] = "Secure on-device storage is required before a BYOK credential can be used."
            meta["provider_status"] = build_provider_status_payload(
                provider_name=config.provider_name,
                display_name=config.display_name,
                enabled=config.enabled,
                auth_mode=config.auth_mode,
                provider_mode="external_summary_optional",
                model_name=config.model_name,
                secure_storage_available=False,
                credential_present=False,
                error_message=meta["error_message"],
                status_override="secure_storage_unavailable",
            )
            return None, meta
        if config.auth_mode == "byok" and not config.credential_present:
            meta["provider_mode"] = "provider_disabled"
            meta["status"] = "provider_enabled_no_credential"
            meta["error_message"] = "No securely stored provider credential is available yet."
            meta["provider_status"] = build_provider_status_payload(
                provider_name=config.provider_name,
                display_name=config.display_name,
                enabled=config.enabled,
                auth_mode=config.auth_mode,
                provider_mode="external_summary_optional",
                model_name=config.model_name,
                secure_storage_available=config.secure_storage_available,
                credential_present=False,
                error_message=meta["error_message"],
                status_override="provider_enabled_no_credential",
            )
            return None, meta
        if provider is None:
            meta["provider_mode"] = "provider_disabled"
            meta["error_message"] = "Provider is not registered."
            meta["status"] = "provider_not_configured"
            meta["provider_status"] = build_provider_status_payload(
                provider_name=config.provider_name,
                display_name=config.display_name,
                enabled=config.enabled,
                auth_mode=config.auth_mode,
                provider_mode="external_summary_optional",
                model_name=config.model_name,
                secure_storage_available=config.secure_storage_available,
                credential_present=config.credential_present,
                error_message=meta["error_message"],
                status_override="provider_not_configured",
            )
            return None, meta
        if not provider.is_available():
            meta["provider_mode"] = "provider_disabled"
            meta["error_message"] = f"{config.provider_name} SDK is not installed."
            meta["status"] = "provider_disabled"
            meta["provider_status"] = build_provider_status_payload(
                provider_name=config.provider_name,
                display_name=config.display_name,
                enabled=config.enabled,
                auth_mode=config.auth_mode,
                provider_mode="provider_disabled",
                model_name=config.model_name,
                secure_storage_available=config.secure_storage_available,
                credential_present=config.credential_present,
                error_message=meta["error_message"],
                status_override="provider_disabled",
            )
            return None, meta

        meta["provider_available"] = True
        try:
            result = provider.summarize(config=config, prompt_payload=prompt_payload)
        except Exception as exc:
            meta["status"] = "provider_error"
            meta["error_message"] = str(exc)
            meta["provider_status"] = build_provider_status_payload(
                provider_name=config.provider_name,
                display_name=config.display_name,
                enabled=config.enabled,
                auth_mode=config.auth_mode,
                provider_mode="external_summary_optional",
                model_name=config.model_name,
                secure_storage_available=config.secure_storage_available,
                credential_present=config.credential_present,
                error_message=meta["error_message"],
                status_override="provider_error",
            )
            return None, meta

        return self._handle_result(config=config, prompt_payload=prompt_payload, result=result, base_meta=meta)

    def _handle_result(
        self,
        *,
        config: ProviderConfig,
        prompt_payload: Any,
        result: ProviderExecutionResult,
        base_meta: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        meta = dict(base_meta)
        try:
            summary = _safe_summary_contract(
                config=config,
                content_source=prompt_payload.content_source,
                output_text=result.output_text,
                external_processing_used=result.external_processing_used,
                safety_validated=True,
            )
            meta.update(
                {
                    "external_processing_used": bool(result.external_processing_used),
                    "status": "success",
                    "safety_validated": True,
                    "result_origin": "external_provider",
                    "raw_response_meta": result.raw_response_meta,
                    "provider_status": build_provider_status_payload(
                        provider_name=config.provider_name,
                        display_name=config.display_name,
                        enabled=config.enabled,
                        auth_mode=config.auth_mode,
                        provider_mode="external_summary_optional",
                        model_name=config.model_name,
                        secure_storage_available=config.secure_storage_available,
                        credential_present=config.credential_present,
                        external_processing_used=bool(result.external_processing_used),
                    ),
                }
            )
            return summary, meta
        except Exception as exc:
            summary = _safe_summary_contract(
                config=config,
                content_source=prompt_payload.content_source,
                output_text="",
                external_processing_used=result.external_processing_used,
                safety_validated=False,
            )
            meta.update(
                {
                    "external_processing_used": bool(result.external_processing_used),
                    "status": "safety_rejected",
                    "safety_validated": False,
                    "result_origin": "external_provider",
                    "error_message": str(exc),
                    "raw_response_meta": result.raw_response_meta,
                    "provider_status": build_provider_status_payload(
                        provider_name=config.provider_name,
                        display_name=config.display_name,
                        enabled=config.enabled,
                        auth_mode=config.auth_mode,
                        provider_mode="external_summary_optional",
                        model_name=config.model_name,
                        secure_storage_available=config.secure_storage_available,
                        credential_present=config.credential_present,
                        external_processing_used=bool(result.external_processing_used),
                    ),
                }
            )
            return summary, meta
