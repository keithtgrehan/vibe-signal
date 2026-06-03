#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

try:
    from generate_synthetic_whatsapp_fixtures import (
        DEFAULT_ENGINE_REPORT_DIR,
        DEFAULT_SEED,
        build_api_regression_report,
        evaluate_conversation_with_api,
        normalize_api_url,
        select_for_api_regression,
        write_jsonl,
    )
except ImportError:  # pragma: no cover - exercised when imported as tools.run_synthetic_fixture_regression
    from tools.generate_synthetic_whatsapp_fixtures import (
        DEFAULT_ENGINE_REPORT_DIR,
        DEFAULT_SEED,
        build_api_regression_report,
        evaluate_conversation_with_api,
        normalize_api_url,
        select_for_api_regression,
        write_jsonl,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "synthetic" / "whatsapp" / "conversations.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _api_url_from_args(value: str | None) -> str:
    candidate = value or os.environ.get("VIBE_SIGNAL_API_URL")
    if not candidate:
        raise ValueError("api-url or VIBE_SIGNAL_API_URL is required")
    return normalize_api_url(candidate)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run synthetic WhatsApp fixtures through the real /api/analyze endpoint.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--engine-report-dir", default=str(DEFAULT_ENGINE_REPORT_DIR))
    args = parser.parse_args(argv)

    api_url = _api_url_from_args(args.api_url)
    conversations = read_jsonl(Path(args.input))
    selected = select_for_api_regression(conversations, limit=args.limit, seed=int(args.seed))
    responses: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []
    for conversation in selected:
        response, evaluation = evaluate_conversation_with_api(conversation, api_url=api_url, timeout=float(args.timeout))
        responses.append(response)
        evaluations.append(evaluation)

    report_dir = Path(args.engine_report_dir)
    write_jsonl(report_dir / "synthetic_regression_api_responses.jsonl", responses)
    write_jsonl(report_dir / "synthetic_regression_results.jsonl", evaluations)
    (report_dir / "synthetic_regression_report.md").write_text(
        build_api_regression_report(conversations, selected, evaluations, api_url=api_url, seed=int(args.seed)).replace(
            "# Engine API Regression Report",
            "# Synthetic Fixture API Regression Report",
            1,
        ),
        encoding="utf-8",
    )

    summary = {
        "status": "synthetic_regression_complete",
        "api_url": api_url,
        "input": str(Path(args.input)),
        "engine_report_dir": str(report_dir),
        "fixture_conversations": len(conversations),
        "evaluated_conversations": len(evaluations),
        "passed_evaluations": sum(1 for row in evaluations if row.get("passed") is True),
        "api_errors": sum(1 for row in evaluations if row.get("api_error") is True),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["api_errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
