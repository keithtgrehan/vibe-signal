"""Verification-layer helpers for store purchase ingestion."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Any

from .models import PURCHASE_ARTIFACT_TYPES, PurchaseVerificationRequest, PurchaseVerificationResult


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_receipt_or_token(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def normalize_purchase_artifact_payload(
    *,
    platform: str,
    product_id: str,
    payload: dict[str, Any] | None,
) -> tuple[PurchaseVerificationRequest | None, str]:
    body = payload or {}
    normalized_platform = str(platform or "").strip().lower()
    artifact_type = str(body.get("artifact_type", "")).strip()
    if artifact_type not in PURCHASE_ARTIFACT_TYPES:
        return None, "unsupported artifact_type"
    if normalized_platform == "ios":
        receipt_data = str(body.get("receipt_data_b64", "")).strip()
        if artifact_type != "apple_app_store_receipt" or not receipt_data:
            return None, "ios payload requires apple_app_store_receipt with receipt_data_b64"
        return PurchaseVerificationRequest(
            app_user_id="",
            platform="ios",
            product_id=product_id,
            receipt_or_token=receipt_data,
            artifact_type=artifact_type,
            transaction_id=str(body.get("transaction_id", "")).strip(),
            original_transaction_id=str(body.get("original_transaction_id", "")).strip(),
            artifact_summary={
                "artifact_type": artifact_type,
                "bundle_id": str(body.get("bundle_id", "")).strip(),
                "environment": str(body.get("environment", "")).strip(),
            },
        ), ""
    if normalized_platform == "android":
        purchase_token = str(body.get("purchase_token", "")).strip()
        package_name = str(body.get("package_name", "")).strip()
        if artifact_type != "google_play_purchase_token" or not purchase_token or not package_name:
            return None, "android payload requires google_play_purchase_token with purchase_token and package_name"
        return PurchaseVerificationRequest(
            app_user_id="",
            platform="android",
            product_id=product_id,
            receipt_or_token=purchase_token,
            artifact_type=artifact_type,
            artifact_summary={
                "artifact_type": artifact_type,
                "package_name": package_name,
                "order_id": str(body.get("order_id", "")).strip(),
                "purchase_state": str(body.get("purchase_state", "")).strip(),
                "acknowledged": bool(body.get("acknowledged")),
                "obfuscated_account_id": str(body.get("obfuscated_account_id", "")).strip(),
            },
        ), ""
    return None, "unsupported platform for purchase verification"


def build_verification_result(
    *,
    request: PurchaseVerificationRequest,
    verification_state: str,
    verification_message: str = "",
    expires_at: str = "",
    started_at: str = "",
    purchase_id: str = "",
    transaction_id: str = "",
    original_transaction_id: str = "",
) -> PurchaseVerificationResult:
    return PurchaseVerificationResult(
        verification_state=str(verification_state or "unverified").strip() or "unverified",
        product_id=request.product_id,
        platform=request.platform,
        purchase_id=purchase_id or request.purchase_id or "",
        transaction_id=transaction_id or request.transaction_id,
        original_transaction_id=original_transaction_id or request.original_transaction_id,
        expires_at=str(expires_at or "").strip(),
        started_at=str(started_at or "").strip(),
        last_verified_at=_utc_now(),
        verification_message=str(verification_message or "").strip(),
        purchase_token_hash=hash_receipt_or_token(request.receipt_or_token),
    )
