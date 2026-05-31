#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vibesignal_ai.features.cue_taxonomy import detect_cues  # noqa: E402


def _read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.text_file is not None:
        return Path(args.text_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze local text with deterministic Vibe cue rules.")
    parser.add_argument("--text", help="Inline local text to analyze.")
    parser.add_argument("--text-file", help="Local text file to analyze. No provider or dataset fetch is performed.")
    parser.add_argument("--conversation-id", default="manual_cli_input")
    parser.add_argument("--message-id", default="m1")
    parser.add_argument("--speaker-role", default="self")
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)

    text = _read_text(args)
    messages = [
        {
            "id": args.message_id,
            "author": args.speaker_role,
            "speaker_role": args.speaker_role,
            "text": text,
        }
    ]
    payload = {
        "conversation_id": args.conversation_id,
        "analysis_mode": "deterministic_local_only",
        "dataset_downloaded": False,
        "provider_used": False,
        "model_trained": False,
        "vector_artifacts_created": False,
        "evidence_objects": detect_cues(messages, conversation_id=args.conversation_id),
    }
    serialized = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
