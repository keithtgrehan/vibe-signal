from __future__ import annotations

from scripts.verify_deployed_version import EndpointResult, classify_deploy_version
from scripts import verify_deployed_version


def test_deploy_verifier_reports_current_when_commit_matches() -> None:
    health = EndpointResult(True, 200, {"status": "ok"}, "")
    status = EndpointResult(
        True,
        200,
        {"ok": True, "git_commit": "abc123", "deploy_version": "main-20260603-2100"},
        "",
    )

    result = classify_deploy_version(health=health, status=status, expected_git_commit="abc123")

    assert result["version_status"] == "current"
    assert result["metadata"]["git_commit"] == "abc123"


def test_deploy_verifier_reports_stale_when_commit_differs() -> None:
    health = EndpointResult(True, 200, {"status": "ok"}, "")
    status = EndpointResult(True, 200, {"ok": True, "git_commit": "oldsha"}, "")

    result = classify_deploy_version(health=health, status=status, expected_git_commit="newsha")

    assert result["version_status"] == "stale"
    assert result["reason"] == "git_commit_does_not_match_expected"


def test_deploy_verifier_reports_unverified_when_metadata_missing() -> None:
    health = EndpointResult(True, 200, {"status": "ok"}, "")
    status = EndpointResult(True, 200, {"ok": True}, "")

    result = classify_deploy_version(health=health, status=status, expected_git_commit="newsha")

    assert result["version_status"] == "unverified"
    assert result["metadata"]["git_commit"] == "unknown"


def test_deploy_verifier_cli_allows_unverified_without_expected_commit(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        verify_deployed_version,
        "verify",
        lambda *args, **kwargs: {
            "base_url": "https://example.invalid",
            "version_status": "unverified",
            "reason": "expected_git_commit_not_provided",
            "health_ok": True,
            "status_ok": True,
            "health_status_code": 200,
            "status_status_code": 200,
            "metadata": {
                "git_commit": "abc123",
                "deploy_version": "unknown",
                "build_timestamp": "unknown",
                "service_revision": "service",
            },
            "expected_git_commit": "",
            "non_secret_fields_only": True,
        },
    )

    exit_code = verify_deployed_version.main(["--base-url", "https://example.invalid", "--format", "json"])

    assert exit_code == 0
    assert "unverified" in capsys.readouterr().out
