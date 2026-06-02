from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import urlparse


VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
ENVIRONMENT_ALIASES = {
    "local": "local",
    "development": "local",
    "dev": "local",
    "staging": "staging",
    "stage": "staging",
    "production": "production",
    "prod": "production",
    "test": "test",
}


@dataclass(frozen=True)
class BackendSettings:
    allowed_origins: tuple[str, ...] = ()
    environment: str = "local"
    version: str = "0.1.0"
    log_level: str = "INFO"
    config_warnings: tuple[str, ...] = field(default_factory=tuple)
    raw_message_persistence_enabled: bool = False
    raw_message_logging_enabled: bool = False
    safe_request_logging_enabled: bool = True
    analytics_tracking_enabled: bool = False
    training_enabled: bool = False


def _normalize_environment(value: str) -> tuple[str, tuple[str, ...]]:
    normalized = str(value or "local").strip().lower()
    if not normalized:
        return "local", ()
    if normalized in ENVIRONMENT_ALIASES:
        return ENVIRONMENT_ALIASES[normalized], ()
    return "local", ("unsupported_environment_defaulted_to_local",)


def _parse_allowed_origins(raw_value: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    origins: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    for raw_origin in str(raw_value or "").split(","):
        origin = raw_origin.strip().rstrip("/")
        if not origin:
            continue
        if "*" in origin:
            warnings.append("wildcard_origin_rejected")
            continue
        parsed = urlparse(origin)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            warnings.append("unsupported_origin_scheme_rejected")
            continue
        if parsed.path or parsed.query or parsed.fragment:
            warnings.append("origin_must_not_include_path_query_or_fragment")
            continue
        normalized = f"{parsed.scheme}://{parsed.netloc}"
        if normalized not in seen:
            origins.append(normalized)
            seen.add(normalized)
    return tuple(origins), tuple(dict.fromkeys(warnings))


def load_backend_settings(environ: Mapping[str, str] | None = None) -> BackendSettings:
    source = os.environ if environ is None else environ
    warnings: list[str] = []
    allowed_origins, origin_warnings = _parse_allowed_origins(
        source.get("VIBE_BACKEND_ALLOWED_ORIGINS", "")
    )
    warnings.extend(origin_warnings)

    log_level = str(source.get("VIBE_BACKEND_LOG_LEVEL", "INFO")).strip().upper() or "INFO"
    if log_level not in VALID_LOG_LEVELS:
        warnings.append("unsupported_log_level_defaulted_to_info")
        log_level = "INFO"
    environment, environment_warnings = _normalize_environment(
        source.get("VIBE_BACKEND_ENV", "local")
    )
    warnings.extend(environment_warnings)

    return BackendSettings(
        allowed_origins=allowed_origins,
        environment=environment,
        version=str(source.get("VIBE_BACKEND_VERSION", "0.1.0")).strip() or "0.1.0",
        log_level=log_level,
        config_warnings=tuple(dict.fromkeys(warnings)),
    )
