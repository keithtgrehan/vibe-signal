"""Commerce service for anonymous identity, entitlement computation, and purchase syncing."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from uuid import uuid4

from .config import CommerceConfig
from .models import (
    AnalysisAccessResult,
    AppUserRecord,
    BillingProduct,
    EntitlementSnapshot,
    PurchaseRecord,
    PurchaseRestoreResult,
    PurchaseVerificationRequest,
    PurchaseVerificationResult,
)
from .store import CommerceStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_timestamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _hash_token(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _subscription_status_from_verification(result: PurchaseVerificationResult) -> str:
    mapping = {
        "verified_active": "active",
        "verified_grace_period": "grace_period",
        "verified_expired": "expired",
        "revoked": "revoked",
        "refunded": "refunded",
        "unverified": "unverified",
        "invalid_receipt_or_token": "invalid_receipt_or_token",
        "verification_unavailable": "verification_unavailable",
    }
    return mapping.get(result.verification_state, "inactive")


class CommerceService:
    def __init__(self, db_path: str | Path | None = None, config: CommerceConfig | None = None) -> None:
        if config is not None and db_path is not None:
            self.config = replace(config, state_db_path=Path(db_path).expanduser().resolve())
        elif config is not None:
            self.config = config
        elif db_path is not None:
            self.config = CommerceConfig(state_db_path=Path(db_path).expanduser().resolve())
        else:
            self.config = CommerceConfig()
        self.store = CommerceStore(self.config.state_db_path)

    def list_products(self) -> list[BillingProduct]:
        return [
            BillingProduct(
                product_id=self.config.ios_monthly_product_id,
                platform="ios",
                display_name="VibeSignal Pro Monthly",
                price_display=self.config.subscription_price_display,
            ),
            BillingProduct(
                product_id=self.config.play_monthly_product_id,
                platform="android",
                display_name="VibeSignal Pro Monthly",
                price_display=self.config.subscription_price_display,
            ),
        ]

    def register_anonymous_user(self, *, device_installation_id: str, platform: str) -> AppUserRecord:
        existing = self.store.get_app_user_by_device(device_installation_id)
        if existing is not None:
            return existing
        user = AppUserRecord(
            app_user_id=f"app_user_{uuid4().hex}",
            device_installation_id=str(device_installation_id or "").strip(),
            platform=str(platform or "unknown").strip() or "unknown",
            created_at=_utc_now(),
        )
        return self.store.insert_app_user(user)

    def get_user(self, app_user_id: str) -> AppUserRecord:
        user = self.store.get_app_user(app_user_id)
        if user is None:
            raise KeyError(f"unknown app_user_id: {app_user_id}")
        return user

    def get_or_create_user(self, *, device_installation_id: str, platform: str) -> AppUserRecord:
        return self.register_anonymous_user(device_installation_id=device_installation_id, platform=platform)

    def _derive_subscription(self, purchases: list[PurchaseRecord]) -> tuple[str, str, str]:
        if not purchases:
            return "inactive", "", ""
        now = datetime.now(timezone.utc)
        for purchase in purchases:
            expires_at = _parse_timestamp(purchase.expires_at)
            if purchase.verification_state == "verified_active":
                if expires_at and expires_at < now:
                    continue
                return "active", purchase.product_id, purchase.verification_state
            if purchase.verification_state == "verified_grace_period":
                return "grace_period", purchase.product_id, purchase.verification_state
        for status in (
            "verified_expired",
            "revoked",
            "refunded",
            "unverified",
            "invalid_receipt_or_token",
            "verification_unavailable",
        ):
            for purchase in purchases:
                if purchase.verification_state == status:
                    return _subscription_status_from_verification(
                        PurchaseVerificationResult(
                            verification_state=purchase.verification_state,
                            product_id=purchase.product_id,
                            platform=purchase.platform,
                            purchase_id=purchase.purchase_id,
                        )
                    ), purchase.product_id, purchase.verification_state
        return "inactive", "", ""

    def get_entitlement(self, app_user_id: str) -> EntitlementSnapshot:
        self.get_user(app_user_id)
        usage_count = self.store.count_completed_analyses(app_user_id)
        free_remaining = max(0, self.config.free_analysis_limit - usage_count)
        subscription_status, active_product_id, verification_state = self._derive_subscription(
            self.store.list_purchases(app_user_id)
        )

        blocked_reason = ""
        entitlement_state = "free_available"
        if subscription_status in {"active", "grace_period"}:
            entitlement_state = "subscription_active"
        elif free_remaining > 0:
            entitlement_state = "free_available"
        else:
            entitlement_state = "blocked"
            if subscription_status == "expired":
                blocked_reason = "subscription_expired"
            elif subscription_status in {"revoked", "refunded", "inactive"}:
                blocked_reason = "subscription_inactive" if subscription_status != "inactive" else "free_limit_reached"
            elif subscription_status in {"unverified", "invalid_receipt_or_token", "verification_unavailable"}:
                blocked_reason = "purchase_unverified"
            else:
                blocked_reason = "free_limit_reached"

        return EntitlementSnapshot(
            app_user_id=app_user_id,
            usage_count=usage_count,
            free_remaining=free_remaining,
            free_analysis_limit=self.config.free_analysis_limit,
            subscription_status=subscription_status,
            entitlement_state=entitlement_state,
            blocked_reason=blocked_reason,
            active_product_id=active_product_id,
            purchase_verification_state=verification_state,
            subscription_required_after_limit=self.config.subscription_required_after_limit,
            support_contact_ref=self.config.support_contact_ref,
            privacy_policy_route_ref=self.config.privacy_policy_route_ref,
            terms_route_ref=self.config.terms_route_ref,
        )

    def check_analysis_access(
        self,
        *,
        app_user_id: str,
        requires_provider: bool = False,
        provider_validation_status: str = "",
        provider_consent_confirmed: bool = True,
        provider_secure_storage_available: bool = True,
    ) -> AnalysisAccessResult:
        entitlement = self.get_entitlement(app_user_id)

        if requires_provider:
            if not provider_consent_confirmed:
                return AnalysisAccessResult(
                    allowed=False,
                    blocked_reason="missing_consent",
                    entitlement=entitlement,
                    provider_gate_status="consent_required",
                    provider_required=True,
                )
            if not provider_secure_storage_available:
                return AnalysisAccessResult(
                    allowed=False,
                    blocked_reason="secure_storage_unavailable",
                    entitlement=entitlement,
                    provider_gate_status="secure_storage_unavailable",
                    provider_required=True,
                )
            normalized_status = str(provider_validation_status or "").strip()
            if normalized_status and normalized_status != "ready":
                return AnalysisAccessResult(
                    allowed=False,
                    blocked_reason="provider_not_ready",
                    entitlement=entitlement,
                    provider_gate_status=normalized_status,
                    provider_required=True,
                )

        return AnalysisAccessResult(
            allowed=entitlement.entitlement_state != "blocked",
            blocked_reason=entitlement.blocked_reason,
            entitlement=entitlement,
            provider_gate_status=str(provider_validation_status or "").strip(),
            provider_required=requires_provider,
        )

    def record_completed_analysis(
        self,
        *,
        app_user_id: str,
        analysis_id: str,
        conversation_id: str,
    ) -> bool:
        self.get_user(app_user_id)
        return self.store.record_completed_analysis(
            app_user_id=app_user_id,
            analysis_id=analysis_id,
            conversation_id=conversation_id,
            completed_at=_utc_now(),
        )

    def ingest_purchase_verification(
        self,
        *,
        request: PurchaseVerificationRequest,
        result: PurchaseVerificationResult,
    ) -> PurchaseRecord:
        self.get_user(request.app_user_id)
        purchase = PurchaseRecord(
            app_user_id=request.app_user_id,
            platform=result.platform,
            product_id=result.product_id,
            purchase_id=result.purchase_id or request.purchase_id or f"purchase_{uuid4().hex}",
            verification_state=result.verification_state,
            purchase_token_hash=result.purchase_token_hash or _hash_token(request.receipt_or_token),
            transaction_id=result.transaction_id or request.transaction_id,
            original_transaction_id=result.original_transaction_id or request.original_transaction_id,
            expires_at=result.expires_at,
            started_at=result.started_at,
            last_verified_at=result.last_verified_at or _utc_now(),
            verification_message=result.verification_message,
        )
        return self.store.upsert_purchase(purchase)

    def restore_purchases(
        self,
        *,
        app_user_id: str,
        verification_results: list[PurchaseVerificationResult],
    ) -> PurchaseRestoreResult:
        restored_ids: list[str] = []
        for result in verification_results:
            purchase = PurchaseRecord(
                app_user_id=app_user_id,
                platform=result.platform,
                product_id=result.product_id,
                purchase_id=result.purchase_id,
                verification_state=result.verification_state,
                purchase_token_hash=result.purchase_token_hash or _hash_token(result.purchase_id),
                transaction_id=result.transaction_id,
                original_transaction_id=result.original_transaction_id,
                expires_at=result.expires_at,
                started_at=result.started_at,
                last_verified_at=result.last_verified_at or _utc_now(),
                verification_message=result.verification_message,
            )
            self.store.upsert_purchase(purchase)
            restored_ids.append(purchase.purchase_id)
        return PurchaseRestoreResult(
            app_user_id=app_user_id,
            restored_count=len(restored_ids),
            entitlement=self.get_entitlement(app_user_id),
            synced_purchase_ids=restored_ids,
        )

    def sync_purchases(
        self,
        *,
        app_user_id: str,
        verification_results: list[PurchaseVerificationResult],
    ) -> PurchaseRestoreResult:
        purchases = [
            PurchaseRecord(
                app_user_id=app_user_id,
                platform=result.platform,
                product_id=result.product_id,
                purchase_id=result.purchase_id,
                verification_state=result.verification_state,
                purchase_token_hash=result.purchase_token_hash or _hash_token(result.purchase_id),
                transaction_id=result.transaction_id,
                original_transaction_id=result.original_transaction_id,
                expires_at=result.expires_at,
                started_at=result.started_at,
                last_verified_at=result.last_verified_at or _utc_now(),
                verification_message=result.verification_message,
            )
            for result in verification_results
        ]
        self.store.replace_purchases(app_user_id, purchases)
        return PurchaseRestoreResult(
            app_user_id=app_user_id,
            restored_count=len(purchases),
            entitlement=self.get_entitlement(app_user_id),
            synced_purchase_ids=[purchase.purchase_id for purchase in purchases],
        )
