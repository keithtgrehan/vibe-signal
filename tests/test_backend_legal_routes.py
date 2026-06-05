from __future__ import annotations

import re

from fastapi.testclient import TestClient

from backend.app import app


PUBLIC_PLACEHOLDER_RE = re.compile(r"\[[^\]]*(?:REQUIRES|REQUIRED)[^\]]*\]")


def test_legal_routes_return_draft_review_boundaries() -> None:
    client = TestClient(app)

    for path in (
        "/legal/privacy",
        "/legal/terms",
        "/legal/data-deletion",
        "/legal/data-export",
        "/legal/match-disclaimer",
    ):
        response = client.get(path)

        assert response.status_code == 200, path
        body = response.json()
        assert body["status"] == "draft_requires_legal_review"
        assert body["not_legal_advice"] is True
        assert body["closed_beta_only"] is True
        assert body["production_compliance_claimed"] is False
        assert body["raw_message_persistence_added"] is False
        assert body["account_storage_added"] is False
        assert body["analytics_tracking_added"] is False
        assert body["training_use_added"] is False
        assert body["title"]
        assert body["document_ref"].startswith("docs/")
        assert body["sections"]
        assert body["intro"].startswith("Vibe Signal is currently in closed beta / early public beta.")
        assert body["groups"]
        assert not PUBLIC_PLACEHOLDER_RE.search(" ".join(body["sections"]))
        assert "legal review before public launch" in body["review_note"].lower()


def test_match_disclaimer_route_keeps_required_safety_copy() -> None:
    client = TestClient(app)

    response = client.get("/legal/match-disclaimer")

    assert response.status_code == 200
    body = response.json()
    combined_copy = " ".join(body["sections"]).lower()
    assert "communication-support only" in combined_copy
    assert "wording-based suggestions only" in combined_copy
    assert "closed beta / early public beta" in combined_copy
    assert "vibe signal does not know intent, attraction, truthfulness, diagnosis, or outcomes." in combined_copy
    assert "not therapy" in combined_copy
    assert "not emergency/crisis support" in combined_copy


def test_api_legal_alias_routes_return_existing_public_drafts() -> None:
    client = TestClient(app)

    aliases = {
        "/api/legal/privacy": "Privacy",
        "/api/legal/terms": "Terms",
        "/api/legal/data-request": "Data request/delete",
        "/api/legal/disclaimer": "Disclaimer",
    }
    for path, title in aliases.items():
        response = client.get(path)

        assert response.status_code == 200, path
        body = response.json()
        assert body["title"] == title
        assert body["status"] == "draft_requires_legal_review"
        assert body["sections"]


def test_legal_routes_include_required_public_draft_content() -> None:
    client = TestClient(app)

    privacy = client.get("/legal/privacy").json()
    privacy_copy = " ".join(privacy["sections"])
    assert "Status: draft_requires_legal_review" in privacy_copy
    assert "Keith Grehan" in privacy_copy
    assert "keith.t.grehan@gmail.com" in privacy_copy
    assert "Berlin, Germany; full address available on valid legal request" in privacy_copy
    assert "https://www.vibe-signal.com" in privacy_copy
    assert "Email provider - Gmail." in privacy_copy
    assert "AI provider - Disabled unless explicitly enabled." in privacy_copy
    assert "External log streaming - none configured." in privacy_copy
    assert "Feedback metadata: 90 days during beta." in privacy_copy
    assert "Legal/data request correspondence: 24 months unless legal review changes this." in privacy_copy
    assert "Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes." in privacy_copy
    assert "Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes." in privacy_copy
    assert "No raw messages are used for training." in privacy_copy
    assert "No analytics, cookies, or tracking are added by this implementation." in privacy_copy
    assert "Draft lawful-basis mapping, subject to legal review:" in privacy_copy
    assert "Submitted text for analysis: consent and/or steps requested by the user to use the service." in privacy_copy
    assert "Infrastructure logs: legitimate interests in security, debugging, abuse prevention, and service reliability." in privacy_copy
    assert "This lawful-basis mapping is a draft and requires legal review before public launch." in privacy_copy
    assert "Berliner Beauftragte für Datenschutz und Informationsfreiheit" in privacy_copy
    assert "Alt-Moabit 59–61, 10555 Berlin, Germany." in privacy_copy
    assert "Email: mailbox@datenschutz-berlin.de." in privacy_copy
    assert "This authority information should be verified before public launch." in privacy_copy

    terms = client.get("/legal/terms").json()
    terms_copy = " ".join(terms["sections"])
    assert "Only submit text you have permission to analyze." in terms_copy
    assert "Prohibited use includes stalking, harassment, coercion, manipulation, or trying to make someone respond." in terms_copy
    assert "Account features are not currently implemented." in terms_copy
    assert "Payment features are not currently implemented." in terms_copy
    assert "To the maximum extent permitted by applicable law, Vibe Signal is provided as a draft beta service without guarantees of uninterrupted availability, accuracy, or error-free operation." in terms_copy
    assert "This clause requires legal review before public launch." in terms_copy
    assert "These Terms are drafted with Germany as the expected governing-law jurisdiction" in terms_copy

    data_request = client.get("/legal/data-deletion").json()
    data_request_copy = " ".join(data_request["sections"])
    assert "Send data requests to: keith.t.grehan@gmail.com." in data_request_copy
    for required in ("access/export", "deletion", "correction", "objection/restriction"):
        assert required in data_request_copy
    assert "Vibe Signal aims to respond to verified privacy requests without undue delay" in data_request_copy
    assert "where GDPR applies, within one month of receipt" in data_request_copy
    assert "This section requires legal review before public launch." in data_request_copy

    disclaimer = client.get("/legal/match-disclaimer").json()
    disclaimer_copy = " ".join(disclaimer["sections"])
    assert "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes." in disclaimer_copy
