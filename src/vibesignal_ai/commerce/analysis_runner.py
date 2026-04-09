"""Metered app-facing analysis runner with entitlement gating."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from ..pipeline.run import analyze_conversation
from .service import CommerceService


def run_metered_analysis(
    *,
    commerce_service: CommerceService,
    app_user_id: str,
    requires_provider: bool = False,
    provider_validation_status: str = "",
    provider_consent_confirmed: bool = True,
    provider_secure_storage_available: bool = True,
    analysis_id: str | None = None,
    **analysis_kwargs: Any,
) -> dict[str, Any]:
    access = commerce_service.check_analysis_access(
        app_user_id=app_user_id,
        requires_provider=requires_provider,
        provider_validation_status=provider_validation_status,
        provider_consent_confirmed=provider_consent_confirmed,
        provider_secure_storage_available=provider_secure_storage_available,
    )
    if not access.allowed:
        return {
            "allowed": False,
            "blocked_reason": access.blocked_reason,
            "provider_gate_status": access.provider_gate_status,
            "provider_required": access.provider_required,
            "entitlement": access.entitlement.to_dict(),
            "analysis_result": None,
            "usage_recorded": False,
        }

    resolved_analysis_id = analysis_id or f"analysis_{uuid4().hex}"
    result = analyze_conversation(**analysis_kwargs)
    usage_recorded = commerce_service.record_completed_analysis(
        app_user_id=app_user_id,
        analysis_id=resolved_analysis_id,
        conversation_id=result["conversation_id"],
    )
    return {
        "allowed": True,
        "blocked_reason": "",
        "provider_gate_status": access.provider_gate_status,
        "provider_required": access.provider_required,
        "entitlement": commerce_service.get_entitlement(app_user_id).to_dict(),
        "analysis_result": result,
        "usage_recorded": usage_recorded,
    }
