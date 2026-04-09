"""Thin request/response surface for entitlement and purchase actions."""

from __future__ import annotations

from typing import Any

from .models import PurchaseVerificationRequest, PurchaseVerificationResult
from .service import CommerceService
from .verification import build_verification_result, normalize_purchase_artifact_payload


def _error_response(status: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "status": status,
        "message": message,
    }


def handle_commerce_request(
    commerce_service: CommerceService,
    *,
    action: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = payload or {}
    normalized_action = str(action or "").strip().lower()

    if normalized_action == "register_anonymous_user":
        device_installation_id = str(body.get("device_installation_id", "")).strip()
        if not device_installation_id:
            return _error_response("invalid_identity", "device_installation_id is required.")
        user = commerce_service.get_or_create_user(
            device_installation_id=device_installation_id,
            platform=str(body.get("platform", "unknown")).strip() or "unknown",
        )
        return {
            "ok": True,
            "status": "registered",
            "app_user": user.to_dict(),
            "entitlement": commerce_service.get_entitlement(user.app_user_id).to_dict(),
        }

    if normalized_action == "fetch_entitlement":
        app_user_id = str(body.get("app_user_id", "")).strip()
        if app_user_id:
            entitlement = commerce_service.get_entitlement(app_user_id)
            return {
                "ok": True,
                "status": "entitlement_loaded",
                "entitlement": entitlement.to_dict(),
            }
        device_installation_id = str(body.get("device_installation_id", "")).strip()
        if not device_installation_id:
            return _error_response(
                "invalid_identity",
                "device_installation_id is required when app_user_id is not provided.",
            )
        user = commerce_service.get_or_create_user(
            device_installation_id=device_installation_id,
            platform=str(body.get("platform", "unknown")).strip() or "unknown",
        )
        return {
            "ok": True,
            "status": "entitlement_loaded",
            "app_user": user.to_dict(),
            "entitlement": commerce_service.get_entitlement(user.app_user_id).to_dict(),
        }

    if normalized_action == "record_completed_analysis":
        app_user_id = str(body.get("app_user_id", "")).strip()
        analysis_id = str(body.get("analysis_id", "")).strip()
        conversation_id = str(body.get("conversation_id", "")).strip()
        if not app_user_id or not analysis_id or not conversation_id:
            return _error_response(
                "invalid_usage_event",
                "app_user_id, analysis_id, and conversation_id are required.",
            )
        recorded = commerce_service.record_completed_analysis(
            app_user_id=app_user_id,
            analysis_id=analysis_id,
            conversation_id=conversation_id,
        )
        entitlement = commerce_service.get_entitlement(app_user_id)
        return {
            "ok": True,
            "status": "completed_analysis_recorded" if recorded else "completed_analysis_already_recorded",
            "usage_recorded": bool(recorded),
            "entitlement": entitlement.to_dict(),
        }

    if normalized_action == "submit_purchase_verification":
        app_user_id = str(body.get("app_user_id", "")).strip()
        platform = str(body.get("platform", "")).strip().lower()
        product_id = str(body.get("product_id", "")).strip()
        if not app_user_id or not platform or not product_id:
            return _error_response(
                "invalid_purchase_request",
                "app_user_id, platform, and product_id are required.",
            )
        normalized_request = None
        artifact_payload = body.get("purchase_artifact")
        if isinstance(artifact_payload, dict):
            normalized_request, error_message = normalize_purchase_artifact_payload(
                platform=platform,
                product_id=product_id,
                payload=artifact_payload,
            )
            if normalized_request is None:
                return _error_response("invalid_purchase_artifact", error_message)
        else:
            receipt_or_token = str(body.get("receipt_or_token", "")).strip()
            if not receipt_or_token:
                return _error_response(
                    "invalid_purchase_artifact",
                    "A platform-specific purchase_artifact is required.",
                )
            normalized_request = PurchaseVerificationRequest(
                app_user_id=app_user_id,
                platform=platform,
                product_id=product_id,
                receipt_or_token=receipt_or_token,
                transaction_id=str(body.get("transaction_id", "")).strip(),
                original_transaction_id=str(body.get("original_transaction_id", "")).strip(),
                purchase_id=str(body.get("purchase_id", "")).strip(),
            )
        request = PurchaseVerificationRequest(
            app_user_id=app_user_id,
            platform=normalized_request.platform,
            product_id=normalized_request.product_id,
            receipt_or_token=normalized_request.receipt_or_token,
            artifact_type=normalized_request.artifact_type,
            transaction_id=normalized_request.transaction_id or str(body.get("transaction_id", "")).strip(),
            original_transaction_id=normalized_request.original_transaction_id
            or str(body.get("original_transaction_id", "")).strip(),
            purchase_id=str(body.get("purchase_id", "")).strip(),
            artifact_summary=normalized_request.artifact_summary,
        )
        result = build_verification_result(
            request=request,
            verification_state=str(body.get("verification_state", "verification_unavailable")).strip()
            or "verification_unavailable",
            verification_message=str(body.get("verification_message", "Store verification wiring is not live yet.")).strip(),
            expires_at=str(body.get("expires_at", "")).strip(),
            started_at=str(body.get("started_at", "")).strip(),
            purchase_id=str(body.get("purchase_id", "")).strip(),
            transaction_id=str(body.get("transaction_id", "")).strip(),
            original_transaction_id=str(body.get("original_transaction_id", "")).strip(),
        )
        purchase = commerce_service.ingest_purchase_verification(request=request, result=result)
        entitlement = commerce_service.get_entitlement(request.app_user_id)
        return {
            "ok": True,
            "status": result.verification_state,
            "purchase": purchase.to_dict(),
            "entitlement": entitlement.to_dict(),
        }

    if normalized_action == "restore_purchases":
        app_user_id = str(body.get("app_user_id", "")).strip()
        if not app_user_id:
            return _error_response("invalid_restore_request", "app_user_id is required.")
        verification_results = [
            PurchaseVerificationResult(
                verification_state=str(item.get("verification_state", "verification_unavailable")).strip()
                or "verification_unavailable",
                product_id=str(item.get("product_id", "")).strip(),
                platform=str(item.get("platform", "")).strip(),
                purchase_id=str(item.get("purchase_id", "")).strip(),
                transaction_id=str(item.get("transaction_id", "")).strip(),
                original_transaction_id=str(item.get("original_transaction_id", "")).strip(),
                expires_at=str(item.get("expires_at", "")).strip(),
                started_at=str(item.get("started_at", "")).strip(),
                last_verified_at=str(item.get("last_verified_at", "")).strip(),
                verification_message=str(item.get("verification_message", "")).strip(),
                purchase_token_hash=str(item.get("purchase_token_hash", "")).strip(),
            )
            for item in body.get("verification_results", [])
            if isinstance(item, dict)
        ]
        result = commerce_service.restore_purchases(
            app_user_id=app_user_id,
            verification_results=verification_results,
        )
        return {
            "ok": True,
            "status": "restore_completed",
            "restore": result.to_dict(),
        }

    return {
        "ok": False,
        "status": "unknown_action",
        "message": "The requested commerce action is not supported.",
    }
