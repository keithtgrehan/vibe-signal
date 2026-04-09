"""Base abstraction for optional external AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..config.provider_config import ProviderConfig
from .models import ProviderExecutionResult, ProviderPromptPayload, ProviderValidationResult
from .validation import build_validation_result


class BaseProvider(ABC):
    name: str = "provider"
    sdk_name: str = "sdk"

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def summarize(
        self,
        *,
        config: ProviderConfig,
        prompt_payload: ProviderPromptPayload,
    ) -> ProviderExecutionResult:
        raise NotImplementedError

    def validate_credentials(
        self,
        *,
        config: ProviderConfig,
        consent_confirmed: bool = False,
    ) -> ProviderValidationResult:
        if not self.is_available():
            return build_validation_result(
                config=config,
                status="provider_unavailable",
                consent_confirmed=consent_confirmed,
            )
        return build_validation_result(
            config=config,
            status="unknown_error",
            consent_confirmed=consent_confirmed,
            user_message="Provider validation is not implemented for this provider.",
        )
