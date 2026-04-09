"""Thin optional Anthropic provider adapter."""

from __future__ import annotations

import json

try:  # pragma: no cover - optional dependency
    from anthropic import Anthropic
except Exception:  # pragma: no cover - optional dependency
    Anthropic = None

from ..config.provider_config import ProviderConfig
from .base import BaseProvider
from .models import ProviderExecutionResult, ProviderPromptPayload, ProviderValidationResult
from .validation import build_validation_result, map_provider_exception


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    sdk_name = "anthropic"

    def is_available(self) -> bool:
        return Anthropic is not None

    def summarize(
        self,
        *,
        config: ProviderConfig,
        prompt_payload: ProviderPromptPayload,
    ) -> ProviderExecutionResult:
        if Anthropic is None:
            raise RuntimeError("Anthropic SDK is not installed.")

        api_key = config.api_key_secret if config.auth_mode == "byok" else None
        client = Anthropic(api_key=api_key, base_url=config.base_url or None, timeout=config.timeout_seconds)
        response = client.messages.create(
            model=config.model_name,
            max_tokens=300,
            temperature=0,
            system=prompt_payload.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt_payload.user_prompt}],
                }
            ],
        )
        text_parts = []
        for block in getattr(response, "content", []):
            text = getattr(block, "text", "")
            if text:
                text_parts.append(text)
        parsed = json.loads("".join(text_parts) or "{}")
        output_text = str(parsed.get("output_text", "")).strip()
        return ProviderExecutionResult(
            provider_name=self.name,
            model_name=config.model_name,
            output_text=output_text,
            raw_response_meta={
                "id": getattr(response, "id", ""),
                "usage": str(getattr(response, "usage", "")),
            },
        )

    def validate_credentials(
        self,
        *,
        config: ProviderConfig,
        consent_confirmed: bool = False,
    ) -> ProviderValidationResult:
        if Anthropic is None:
            return build_validation_result(
                config=config,
                status="provider_unavailable",
                consent_confirmed=consent_confirmed,
            )
        try:
            client = Anthropic(
                api_key=config.api_key_secret if config.auth_mode == "byok" else None,
                base_url=config.base_url or None,
                timeout=min(max(int(config.timeout_seconds), 3), 15),
            )
            client.messages.create(
                model=config.model_name,
                max_tokens=1,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": "Reply with OK."}],
                    }
                ],
            )
            return build_validation_result(
                config=config,
                status="ready",
                consent_confirmed=consent_confirmed,
            )
        except Exception as exc:
            status, message, http_status, error_code = map_provider_exception(exc)
            return build_validation_result(
                config=config,
                status=status,
                user_message=message,
                consent_confirmed=consent_confirmed,
                http_status=http_status,
                error_code=error_code,
            )
