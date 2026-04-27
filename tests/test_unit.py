"""Unit tests for the bits of granola-client that don't need the live API.

The integration tests in test_client.py exercise the real Granola API and need
a working desktop-app token. These tests cover header construction, token
expiry math, and the 200-with-error envelope detection — all pure logic.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict
from unittest.mock import patch

import httpx
import pytest

from granola_client import GranolaClient
from granola_client._device import get_platform_label
from granola_client.errors import GranolaUnsupportedClientError
from granola_client.http_client import HttpClient, _check_known_error_envelope


def _make_http_client(**kwargs) -> HttpClient:
    return HttpClient(token=kwargs.pop("token", "test-token"), **kwargs)


# --- envelope detection ---------------------------------------------------

def test_envelope_detects_unsupported_client():
    with pytest.raises(GranolaUnsupportedClientError):
        _check_known_error_envelope(b'{"message": "Unsupported client"}')


def test_envelope_passes_real_payloads():
    # Real responses must not trigger; only the {"message": "..."} shape does.
    _check_known_error_envelope(b"")
    _check_known_error_envelope(b'{"docs": []}')
    _check_known_error_envelope(b'{"message": "Some other error"}')
    _check_known_error_envelope(b'{"message": "Unsupported client", "docs": []}')
    _check_known_error_envelope(b"not json at all")


# --- header construction --------------------------------------------------

def test_build_headers_uses_new_schema():
    http = _make_http_client()
    headers = http._build_headers(body_data={"foo": "bar"})

    # New identity headers, mirroring the live Granola Electron app.
    assert "X-Client-Version" in headers
    assert headers["X-Granola-Platform"] in {"macOS", "Windows", "Linux", "web"}
    assert "X-Granola-Os-Version" in headers
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Content-Type"] == "application/json"

    # Old schema must not leak back in — these are what the server rejected.
    for legacy in ("X-App-Version", "X-Client-Type", "X-Client-Id", "X-Client-Platform", "X-Client-Architecture"):
        assert legacy not in headers


def test_build_headers_omits_authorization_without_token():
    http = HttpClient(token=None)
    headers = http._build_headers(body_data=None)
    assert "Authorization" not in headers
    # Bodiless GET path still asks for JSON back.
    assert headers["Accept"] == "application/json"


def test_client_headers_override_defaults():
    http = _make_http_client(opts={"client_headers": {"X-Granola-Workspace-Id": "wsp-123"}})
    headers = http._build_headers(body_data=None)
    assert headers["X-Granola-Workspace-Id"] == "wsp-123"


# --- token expiry math ----------------------------------------------------

def test_is_workos_token_expiring_for_fresh_token():
    now_ms = int(time.time() * 1000)
    tokens = {"obtained_at": now_ms, "expires_in": 21600}  # 6 hours
    assert GranolaClient._is_workos_token_expiring(tokens) is False


def test_is_workos_token_expiring_for_expired_token():
    long_ago_ms = int(time.time() * 1000) - 10 * 3600 * 1000
    tokens = {"obtained_at": long_ago_ms, "expires_in": 3600}
    assert GranolaClient._is_workos_token_expiring(tokens) is True


def test_is_workos_token_expiring_treats_missing_metadata_as_expired():
    # If we can't tell, it's safer to refresh than to send a stale bearer.
    assert GranolaClient._is_workos_token_expiring({}) is True
    assert GranolaClient._is_workos_token_expiring({"obtained_at": 1}) is True


def test_is_workos_token_expiring_honours_leeway():
    now_ms = int(time.time() * 1000)
    tokens = {"obtained_at": now_ms - 21500 * 1000, "expires_in": 21600}  # 100s left
    assert GranolaClient._is_workos_token_expiring(tokens, leeway_s=200) is True
    assert GranolaClient._is_workos_token_expiring(tokens, leeway_s=10) is False


# --- platform label -------------------------------------------------------

@pytest.mark.parametrize(
    "system,expected",
    [("Darwin", "macOS"), ("Windows", "Windows"), ("Linux", "Linux")],
)
def test_get_platform_label(system: str, expected: str):
    assert get_platform_label(system) == expected


# --- mocked end-to-end: refresh on 401 -----------------------------------

@pytest.mark.asyncio
async def test_request_raw_refreshes_token_and_retries_on_401(httpx_mock):
    """A 401 should drop the cached token and let the provider re-issue one."""
    call_count = {"n": 0}

    async def provider() -> str:
        call_count["n"] += 1
        return f"token-v{call_count['n']}"

    http = HttpClient(token=None, base_url="https://api.example.test")
    http.set_token_provider(provider)

    httpx_mock.add_response(
        url="https://api.example.test/v2/foo",
        status_code=401,
        json={"message": "Unauthorized"},
    )
    httpx_mock.add_response(
        url="https://api.example.test/v2/foo",
        status_code=200,
        json={"ok": True},
    )

    response = await http._request_raw("POST", "/v2/foo", body_data={"x": 1})

    assert response.status_code == 200
    assert call_count["n"] == 2  # initial fetch + post-401 re-fetch

    # The successful retry must carry the new token.
    second_request = httpx_mock.get_requests()[-1]
    assert second_request.headers["Authorization"] == "Bearer token-v2"

    await http.close()


@pytest.mark.asyncio
async def test_request_raw_does_not_loop_on_persistent_401(httpx_mock):
    """If the refreshed token still 401s, surface the error — don't loop forever."""
    async def provider() -> str:
        return "always-stale"

    http = HttpClient(token=None, base_url="https://api.example.test", opts={"retries": 0})
    http.set_token_provider(provider)

    httpx_mock.add_response(
        url="https://api.example.test/v2/foo",
        status_code=401,
        json={"message": "Unauthorized"},
        is_reusable=True,
    )

    from granola_client.errors import GranolaAPIError
    with pytest.raises(GranolaAPIError) as exc:
        await http._request_raw("POST", "/v2/foo", body_data={})
    assert exc.value.status_code == 401
    # Initial call + one refresh-then-retry == 2 hits, not infinite.
    assert len(httpx_mock.get_requests()) == 2

    await http.close()
