"""Thin optional Groq provider adapter."""

from __future__ import annotations

import json

try:  # pragma: no cover - optional dependency
    from groq import Groq
except Exception:  # pragma: no cover - optional dependency
    Groq = None

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None

from ..config.provider_config import ProviderConfig
from .base import BaseProvider
from .models import ProviderExecutionResult, ProviderPromptPayload, ProviderValidationResult
from .validation import build_validation_result, map_provider_exception


class GroqProvider(BaseProvider):
    name = "groq"
    sdk_name = "groq"

    def is_available(self) -> bool:
        return Groq is not None or OpenAI is not None

    def summarize(
        self,
        *,
        config: ProviderConfig,
        prompt_payload: ProviderPromptPayload,
    ) -> ProviderExecutionResult:
        api_key = config.api_key_secret if config.auth_mode == "byok" else None

        if Groq is not None:
            client = Groq(api_key=api_key, base_url=config.base_url or None, timeout=config.timeout_seconds)
            response = client.chat.completions.create(
                model=config.model_name,
                temperature=0,
                messages=[
                    {"role": "system", "content": prompt_payload.system_prompt},
                    {"role": "user", "content": prompt_payload.user_prompt},
                ],
                response_format={"type": "json_object"},
            )
        elif OpenAI is not None:
            client = OpenAI(
                api_key=api_key,
                base_url=config.base_url or "https://api.groq.com/openai/v1",
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
        else:
            raise RuntimeError("No Groq-compatible SDK is installed.")

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
        if Groq is None and OpenAI is None:
            return build_validation_result(
                config=config,
                status="provider_unavailable",
                consent_confirmed=consent_confirmed,
            )
        try:
            timeout_seconds = min(max(int(config.timeout_seconds), 3), 15)
            if Groq is not None:
                client = Groq(
                    api_key=config.api_key_secret if config.auth_mode == "byok" else None,
                    base_url=config.base_url or None,
                    timeout=timeout_seconds,
                )
                client.chat.completions.create(
                    model=config.model_name,
                    temperature=0,
                    max_tokens=1,
                    messages=[{"role": "user", "content": "Reply with OK."}],
                )
            else:
                client = OpenAI(
                    api_key=config.api_key_secret if config.auth_mode == "byok" else None,
                    base_url=config.base_url or "https://api.groq.com/openai/v1",
                    timeout=timeout_seconds,
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
