# backend/test_main.py
"""
Tests for the BYOK enforcement logic in main.py.

run_research is patched throughout so no real API calls are made.
The `used_ips` module-level set is reset before each test via a fixture.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import main
from main import app, used_ips
from schema import CompanyReport, OpenRole


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_REPORT = CompanyReport(
    company_name="Acme Corp",
    one_liner="Acme builds widgets for everyone.",
    tech_stack=["Python"],
    team_size="11-50 employees",
    key_people=["Jane Doe - CEO"],
    funding="Seed - $1M (2024)",
    recent_news=["Launched v2"],
    open_roles=[OpenRole(title="Backend Engineer", link="https://acme.com/jobs/1")],
    pain_points=["Scaling infrastructure"],
    fit_score=7,
    fit_reasoning="Good overlap with Python skills.",
    sources=["https://acme.com"],
)

# Minimal valid request body (no API keys — uses server keys)
SERVER_KEY_BODY = {
    "company_name": "Acme Corp",
    "user_profile": "Python engineer with 5 years experience",
}

# Request body supplying both BYOK keys
BYOK_BODY = {
    "company_name": "Acme Corp",
    "user_profile": "Python engineer with 5 years experience",
    "gemini_api_key": "my-gemini-key",
    "serper_api_key": "my-serper-key",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_used_ips():
    """Clear the in-memory IP set before every test."""
    main.used_ips.clear()
    yield
    main.used_ips.clear()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Tests: first free lookup with server keys
# ---------------------------------------------------------------------------

def test_first_request_server_keys_succeeds(client):
    """An IP that has never made a request should get a successful response."""
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        resp = client.post("/research", json=SERVER_KEY_BODY)
    assert resp.status_code == 200
    assert resp.json()["company_name"] == "Acme Corp"


def test_first_request_adds_ip_to_used_set(client):
    """After a successful server-key request the client IP must be recorded."""
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        client.post("/research", json=SERVER_KEY_BODY)
    # Starlette's TestClient reports the client host as "testclient"
    assert "testclient" in main.used_ips


# ---------------------------------------------------------------------------
# Tests: second request with server keys is blocked
# ---------------------------------------------------------------------------

def test_second_request_server_keys_blocked(client):
    """After the free lookup is consumed, a serverkey request returns 429."""
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        client.post("/research", json=SERVER_KEY_BODY)  # consume free lookup

    with patch("main.run_research", return_value=MINIMAL_REPORT):
        resp = client.post("/research", json=SERVER_KEY_BODY)

    assert resp.status_code == 429
    assert "free lookup" in resp.json()["detail"]


def test_429_detail_message_mentions_keys(client):
    """The 429 detail should instruct the user to supply their own keys."""
    main.used_ips.add("testclient")
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        resp = client.post("/research", json=SERVER_KEY_BODY)
    detail = resp.json()["detail"]
    assert "Gemini" in detail
    assert "Serper" in detail


# ---------------------------------------------------------------------------
# Tests: BYOK requests bypass the limit
# ---------------------------------------------------------------------------

def test_byok_request_always_allowed_even_after_free_lookup(client):
    """A request supplying both keys must never be blocked."""
    main.used_ips.add("testclient")  # simulate IP already used its free lookup
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        resp = client.post("/research", json=BYOK_BODY)
    assert resp.status_code == 200


def test_byok_request_does_not_add_ip(client):
    """A BYOK request must not consume the free-lookup slot."""
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        client.post("/research", json=BYOK_BODY)
    assert "127.0.0.1" not in main.used_ips


def test_byok_request_repeated_always_allowed(client):
    """Multiple BYOK requests from the same IP should all succeed."""
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        for _ in range(3):
            resp = client.post("/research", json=BYOK_BODY)
            assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Tests: only-one-key supplied is treated as "using server keys"
# ---------------------------------------------------------------------------

def test_only_gemini_key_counts_as_server_keys(client):
    """Supplying only gemini_api_key (no serper key) still uses the server's Serper key."""
    main.used_ips.add("testclient")
    body = {**SERVER_KEY_BODY, "gemini_api_key": "my-gemini-key"}
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        resp = client.post("/research", json=body)
    assert resp.status_code == 429


def test_only_serper_key_counts_as_server_keys(client):
    """Supplying only serper_api_key (no gemini key) still uses the server's Gemini key."""
    main.used_ips.add("testclient")
    body = {**SERVER_KEY_BODY, "serper_api_key": "my-serper-key"}
    with patch("main.run_research", return_value=MINIMAL_REPORT):
        resp = client.post("/research", json=body)
    assert resp.status_code == 429


# ---------------------------------------------------------------------------
# Tests: run_research failure does NOT record the IP
# ---------------------------------------------------------------------------

def test_failed_research_does_not_consume_free_lookup(client):
    """If run_research raises, the IP should not be added to used_ips."""
    with patch("main.run_research", side_effect=RuntimeError("API error")):
        resp = client.post("/research", json=SERVER_KEY_BODY)
    assert resp.status_code == 500
    assert "127.0.0.1" not in main.used_ips
