"""Runtime flags for optional heavy integrations."""

from __future__ import annotations

import os


def _env_flag(name: str, *, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_OPENSMILE = _env_flag("VIBESIGNAL_ENABLE_OPENSMILE", default=False)
ENABLE_NLI = _env_flag("VIBESIGNAL_ENABLE_NLI", default=False)
ENABLE_VAD = _env_flag("VIBESIGNAL_ENABLE_VAD", default=False)

NLI_MODEL_NAME = os.getenv(
    "VIBESIGNAL_NLI_MODEL",
    "MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
)


def opensmile_enabled() -> bool:
    return bool(ENABLE_OPENSMILE)


def vad_enabled() -> bool:
    return bool(ENABLE_VAD)


def runtime_flag_snapshot() -> dict[str, object]:
    return {
        "enable_opensmile": bool(ENABLE_OPENSMILE),
        "enable_nli": bool(ENABLE_NLI),
        "enable_vad": bool(ENABLE_VAD),
        "nli_model_name": NLI_MODEL_NAME,
    }
