"""Commerce, entitlement, and billing scaffolding for VibeSignal AI."""

from .analysis_runner import run_metered_analysis
from .api import handle_commerce_request
from .config import (
    FREE_ANALYSIS_LIMIT,
    IOS_MONTHLY_PRODUCT_ID,
    PLAY_MONTHLY_PRODUCT_ID,
    SUBSCRIPTION_PRICE_DISPLAY,
    SUBSCRIPTION_REQUIRED_AFTER_LIMIT,
)
from .service import CommerceService

__all__ = [
    "CommerceService",
    "FREE_ANALYSIS_LIMIT",
    "IOS_MONTHLY_PRODUCT_ID",
    "PLAY_MONTHLY_PRODUCT_ID",
    "SUBSCRIPTION_PRICE_DISPLAY",
    "SUBSCRIPTION_REQUIRED_AFTER_LIMIT",
    "handle_commerce_request",
    "run_metered_analysis",
]
