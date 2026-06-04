#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


RAW_EXTENSIONS = {
    ".txt",
    ".json",
    ".jsonl",
    ".csv",
    ".md",
    ".html",
    ".pdf",
    ".mp3",
    ".wav",
    ".m4a",
    ".mp4",
    ".mov",
    ".webm",
    ".srt",
    ".vtt",
    ".png",
    ".jpg",
    ".jpeg",
    ".heic",
    ".arrow",
    ".bin",
    ".db",
    ".faiss",
    ".joblib",
    ".npy",
    ".npz",
    ".onnx",
    ".parquet",
    ".pkl",
    ".pt",
    ".pth",
    ".safetensors",
    ".sqlite",
}
RISK_MARKERS = (
    "raw/",
    "chats/",
    "whatsapp/",
    "platform_exports/",
    "screenshots/",
    "audio/",
    "video/",
    "transcripts/",
    "provider_outputs/",
    "provider_raw/",
    "exports/raw",
    "user_data/",
    "private/",
    "downloads/",
    "models/",
    "vectors/",
    "embeddings/",
    "checkpoints/",
    "training_runs/",
    "data/external/",
    "data/vibe_training/raw/",
    "data/vibe_training/derived/",
    "data/vibe_training/corpus/",
    "reports/vibe_training/raw/",
    "reddit/",
    "twitter/",
    "tweets/",
    "tweet_exports/",
    "goemotions/",
    "tweeteval/",
    "daily_dialog/",
    "dair_ai/",
    "empathetic_dialogues/",
)
SAFE_PREFIXES = (
    "docs/",
    "configs/",
    "schemas/",
    "tests/fixtures/",
    "data/synthetic/whatsapp/",
    "reports/synthetic_whatsapp/",
    "data/vibe_gold/example_",
    "data/review/.gitkeep",
    "data/restricted/private_whatsapp/.gitkeep",
    "data/restricted/private_whatsapp/readme.md",
    "reports/.gitkeep",
)


def staged_paths(cwd: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_safe_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return any(normalized.startswith(prefix) for prefix in SAFE_PREFIXES)


def looks_restricted(path: str) -> bool:
    normalized = path.replace("\\", "/").lower().lstrip("./")
    if is_safe_path(normalized):
        return False
    return Path(normalized).suffix in RAW_EXTENSIONS and any(marker in normalized for marker in RISK_MARKERS)


def find_restricted(paths: list[str]) -> list[str]:
    return [path for path in paths if looks_restricted(path)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail closed when raw Vibe chats/audio/video/transcripts/provider outputs are staged or listed.")
    parser.add_argument("paths", nargs="*", help="Paths to check. If omitted with --staged, staged git paths are checked.")
    parser.add_argument("--staged", action="store_true", help="Check currently staged git paths.")
    parser.add_argument("--cwd", default=".", help="Repository root for staged checks.")
    args = parser.parse_args(argv)

    paths = list(args.paths)
    if args.staged or not paths:
        paths = staged_paths(Path(args.cwd))

    flagged = find_restricted(paths)
    if flagged:
        print("Vibe restricted artifact check failed. Raw personal data or provider artifacts must stay out of git:", file=sys.stderr)
        for path in flagged:
            print(f"- {path}", file=sys.stderr)
        return 1
    print(f"Vibe restricted artifact check passed: {len(paths)} path(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
