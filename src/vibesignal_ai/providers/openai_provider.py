"""Thin optional OpenAI provider adapter."""

from __future__ import annotations

import json
from typing import Any

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None

from ..config.provider_config import ProviderConfig
from .base import BaseProvider
from .models import ProviderExecutionResult, ProviderPromptPayload, ProviderValidationResult
from .validation import build_validation_result, map_provider_exception


class OpenAIProvider(BaseProvider):
    name = "openai"
    sdk_name = "openai"

    def is_available(self) -> bool:
        return OpenAI is not None

    def summarize(
        self,
        *,
        config: ProviderConfig,
        prompt_payload: ProviderPromptPayload,
    ) -> ProviderExecutionResult:
        if OpenAI is None:
            raise RuntimeError("OpenAI SDK is not installed.")

        api_key = config.api_key_secret if config.auth_mode == "byok" else None
        client = OpenAI(
            api_key=api_key,
            base_url=config.base_url or None,
            timeout=config.timeout_seconds,
        )
        response = client.chat.completions.create(
            model=config.model_name,
            temperature=0,
            messages=[
                {"role": "system", "content": prompt_payload.system_prompt},
                {"role": "user", "content": prompt_payload.user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
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
        if OpenAI is None:
            return build_validation_result(
                config=config,
                status="provider_unavailable",
                consent_confirmed=consent_confirmed,
            )
        try:
            client = OpenAI(
                api_key=config.api_key_secret if config.auth_mode == "byok" else None,
                base_url=config.base_url or None,
                timeout=min(max(int(config.timeout_seconds), 3), 15),
            )
            client.chat.completions.create(
                model=config.model_name,
                temperature=0,
                max_tokens=1,
                messages=[{"role": "user", "content": "Reply with OK."}],
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
