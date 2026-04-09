"""CLI entry point for VibeSignal AI."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline.run import analyze_conversation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vibesignal_ai",
        description="Deterministic-first conversation pattern analysis.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a conversation input.")
    analyze.add_argument("--input", required=True, help="Input file path.")
    analyze.add_argument(
        "--type",
        required=True,
        choices=[
            "whatsapp",
            "pasted_chat",
            "audio_note",
            "interview_audio",
            "generic_audio",
        ],
        help="Input type.",
    )
    analyze.add_argument(
        "--mode",
        required=True,
        choices=["relationship_chat", "interview", "generic"],
        help="Analysis mode.",
    )
    analyze.add_argument("--out", required=True, help="Output directory.")
    analyze.add_argument(
        "--processing-mode",
        default="on_device_only",
        choices=["on_device_only", "local_plus_summary"],
        help="Whether to keep the run fully local or add the optional summary layer.",
    )
    analyze.add_argument(
        "--expected-language",
        default="en",
        help="Expected language code stored in metadata.",
    )
    analyze.add_argument(
        "--participants",
        nargs="*",
        default=[],
        help="Optional participant names to seed metadata.",
    )
    analyze.add_argument(
        "--rights-asserted",
        action="store_true",
        help="Assert rights for the submitted input.",
    )
    analyze.add_argument(
        "--provider-mode",
        default="local_only",
        choices=["local_only", "external_summary_optional", "provider_disabled"],
        help="Whether to stay fully local or request a separate optional external provider summary.",
    )
    analyze.add_argument(
        "--provider",
        default=None,
        choices=["openai", "anthropic", "groq"],
        help="Optional external provider name.",
    )
    analyze.add_argument(
        "--provider-auth-mode",
        default="disabled",
        choices=["byok", "backend_proxy", "disabled"],
        help="How provider authentication would be handled if external mode is enabled.",
    )
    analyze.add_argument("--provider-model-name", default=None, help="Optional provider model override.")
    analyze.add_argument("--provider-base-url", default=None, help="Optional provider base URL override.")
    analyze.add_argument("--provider-timeout-seconds", type=int, default=None, help="Optional provider timeout override.")
    analyze.add_argument(
        "--provider-excerpt",
        action="append",
        default=[],
        help="Optional excerpt text sent only when external provider mode is explicitly enabled.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        result = analyze_conversation(
            input_path=Path(args.input),
            input_type=args.type,
            mode=args.mode,
            out_dir=Path(args.out),
            processing_mode=args.processing_mode,
            expected_language=args.expected_language,
            participants=args.participants,
            rights_asserted=args.rights_asserted,
            provider_mode=args.provider_mode,
            provider_name=args.provider,
            provider_auth_mode=args.provider_auth_mode,
            provider_model_name=args.provider_model_name,
            provider_base_url=args.provider_base_url,
            provider_timeout_seconds=args.provider_timeout_seconds,
            provider_excerpt_texts=args.provider_excerpt,
        )
        print(result["conversation_root"])
        return 0

    parser.error("Unsupported command")
    return 2
