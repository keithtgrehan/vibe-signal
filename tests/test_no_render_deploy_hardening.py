from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
GO_NO_GO = REPO_ROOT / "docs" / "proof" / "closed_beta" / "closed_beta_go_no_go.md"
RUNBOOK = REPO_ROOT / "docs" / "ops" / "render_vercel_deployment_runbook.md"
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "prod_smoke_custom_domain.sh"


REQUIRED_CORS_ORIGINS = (
    "https://www.vibe-signal.com",
    "https://vibe-signal.com",
    "https://vibe-signal.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:19006",
    "http://localhost:8081",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_documents_custom_domain_static_legal_and_cors_origins() -> None:
    text = _read(README)

    assert "Primary web app: [https://www.vibe-signal.com]" in text
    assert "Fallback/preview web app: [https://vibe-signal.vercel.app]" in text
    assert "Vercel deploys the frontend and Render deploys the backend separately." in text
    assert "Static legal pages render from the web bundle and work without Render." in text
    for origin in REQUIRED_CORS_ORIGINS:
        assert origin in text


def test_closed_beta_go_no_go_reflects_current_no_render_state() -> None:
    text = _read(GO_NO_GO)

    assert "Date: 2026-06-05." in text
    assert "| Web custom domain | `PASS` | `https://www.vibe-signal.com` is the primary live web app." in text
    assert "| Static legal pages | `PASS` | Public legal tabs render from the Vercel web bundle without Render." in text
    assert "| Backend custom-domain CORS | `PENDING_RENDER_REDEPLOY` |" in text
    assert "| Real-device iPhone/TestFlight QA | `NOT RUN` |" in text
    assert "Tester invites remain `BLOCKED`" in text
    assert "legal review still required" in text.lower()


def test_runbook_exists_with_deployment_flows_and_smoke_commands() -> None:
    text = _read(RUNBOOK)

    for required in (
        "Vercel deployment flow",
        "Render deployment flow",
        "Required Render environment variables",
        "Required Vercel environment variables",
        "CORS failure diagnosis",
        "Stale Render diagnosis",
        "Custom domain DNS notes",
        "Exact smoke commands",
        "Known symptoms and fixes",
        "scripts/prod_smoke_custom_domain.sh",
        "curl -i https://vibe-signal.onrender.com/api/status",
        "curl -i -X OPTIONS https://vibe-signal.onrender.com/api/analyze",
    ):
        assert required in text


def test_custom_domain_smoke_script_contains_required_checks_and_synthetic_only_payload() -> None:
    text = _read(SMOKE_SCRIPT)

    assert text.startswith("#!/usr/bin/env bash\nset -euo pipefail\n")
    for required in (
        "PASS",
        "FAIL",
        "https://www.vibe-signal.com",
        "https://vibe-signal.com",
        "https://vibe-signal.onrender.com/healthz",
        "https://vibe-signal.onrender.com/api/status",
        "https://vibe-signal.onrender.com/api/analyze",
        "Origin: https://www.vibe-signal.com",
        "Alex: Are you still up for talking tonight?",
        "/legal/privacy",
        "/api/legal/privacy",
        "frontend legal pages are static-first",
    ):
        assert required in text

    blocked_private_markers = ("password", "phone number", "private chat", "real user")
    lowered = text.lower()
    for marker in blocked_private_markers:
        assert marker not in lowered


def test_hardening_docs_do_not_claim_compliance_or_production_approval() -> None:
    combined = "\n".join(_read(path) for path in (README, GO_NO_GO, RUNBOOK))

    forbidden_claims = (
        r"\bGDPR compliant\b",
        r"\bEU AI Act compliant\b",
        r"\blegally approved\b",
        r"\bsolicitor approved\b",
        r"\bproduction ready\b",
        r"\bready for tester invites\b",
    )
    for pattern in forbidden_claims:
        assert not re.search(pattern, combined, flags=re.IGNORECASE)
