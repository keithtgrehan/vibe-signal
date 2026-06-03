#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


SAFE_STATUS_FIELDS = ("git_commit", "deploy_version", "build_timestamp", "service_revision")


@dataclass(frozen=True)
class EndpointResult:
    ok: bool
    status_code: int | None
    payload: dict[str, Any]
    error: str


def _fetch_json(url: str, *, timeout_seconds: float = 10.0) -> EndpointResult:
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            body = response.read(65536).decode("utf-8", errors="replace")
            payload = json.loads(body) if body.strip() else {}
            return EndpointResult(True, int(response.status), payload if isinstance(payload, dict) else {}, "")
    except urllib.error.HTTPError as exc:
        return EndpointResult(False, int(exc.code), {}, f"http_error_{exc.code}")
    except Exception as exc:  # noqa: BLE001 - CLI verifier must report bounded failures.
        return EndpointResult(False, None, {}, exc.__class__.__name__)


def _metadata(status_payload: dict[str, Any]) -> dict[str, str]:
    return {field: str(status_payload.get(field) or "unknown") for field in SAFE_STATUS_FIELDS}


def classify_deploy_version(
    *,
    health: EndpointResult,
    status: EndpointResult,
    expected_git_commit: str | None = None,
) -> dict[str, Any]:
    metadata = _metadata(status.payload)
    health_ok = health.ok and str(health.payload.get("status", "")).lower() == "ok"
    status_ok = status.ok and status.payload.get("ok") is True
    git_commit = metadata["git_commit"]
    expected = str(expected_git_commit or "").strip()

    if not health_ok or not status_ok:
        version_status = "unverified"
        reason = "health_or_status_endpoint_unavailable"
    elif git_commit == "unknown":
        version_status = "unverified"
        reason = "git_commit_metadata_missing"
    elif expected and git_commit != expected:
        version_status = "stale"
        reason = "git_commit_does_not_match_expected"
    elif expected and git_commit == expected:
        version_status = "current"
        reason = "git_commit_matches_expected"
    else:
        version_status = "unverified"
        reason = "expected_git_commit_not_provided"

    return {
        "version_status": version_status,
        "reason": reason,
        "health_ok": health_ok,
        "status_ok": status_ok,
        "health_status_code": health.status_code,
        "status_status_code": status.status_code,
        "metadata": metadata,
        "expected_git_commit": expected or "",
        "non_secret_fields_only": True,
    }


def verify(base_url: str, *, expected_git_commit: str | None = None, timeout_seconds: float = 10.0) -> dict[str, Any]:
    normalized = base_url.rstrip("/")
    health = _fetch_json(f"{normalized}/healthz", timeout_seconds=timeout_seconds)
    status = _fetch_json(f"{normalized}/api/status", timeout_seconds=timeout_seconds)
    return {
        "base_url": normalized,
        **classify_deploy_version(health=health, status=status, expected_git_commit=expected_git_commit),
    }


def _markdown(payload: dict[str, Any]) -> str:
    metadata = payload["metadata"]
    lines = [
        "# Deployed Version Verification",
        "",
        f"- Base URL: `{payload['base_url']}`",
        f"- Version status: `{payload['version_status']}`",
        f"- Reason: `{payload['reason']}`",
        f"- Health endpoint: `{'PASS' if payload['health_ok'] else 'FAIL'}`",
        f"- Status endpoint: `{'PASS' if payload['status_ok'] else 'FAIL'}`",
        f"- Expected git commit: `{payload.get('expected_git_commit') or 'not provided'}`",
        "",
        "## Safe Metadata",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in metadata.items())
    lines.extend(
        [
            "",
            "This verifier reads only allowlisted `/api/status` fields. It does not expose secrets, raw environment dumps, request bodies, or user content.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify deployed Vibe Signal backend version metadata.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--expected-git-commit", default="")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    args = parser.parse_args(argv)

    payload = verify(
        args.base_url,
        expected_git_commit=args.expected_git_commit or None,
        timeout_seconds=float(args.timeout_seconds),
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_markdown(payload))
    if not payload["health_ok"] or not payload["status_ok"] or payload["version_status"] == "stale":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
