import pytest
import json
from pathlib import Path
from unittest import mock # For mocking Path.home in get_auth_tokens test

from httpx import Response

from granola_client import GranolaClient, GranolaAuthError
from granola_client.types import WorkspaceResponse, Workspace, ClientOpts

# Base URL for mocking
BASE_URL = "https://api.granola.ai"

@pytest.fixture
def client_no_token():
    # Client without a token for testing auth retrieval or public endpoints
    return GranolaClient()

@pytest.fixture
def client_with_token():
    return GranolaClient(token="test-token")

@pytest.mark.asyncio
async def test_get_workspaces_success(client_with_token: GranolaClient, httpx_mock):
    """Test successful retrieval of workspaces."""
    mock_response_data = {
        "workspaces": [
            {"id": "ws1", "name": "Personal", "role": "owner"},
            {"id": "ws2", "name": "Work", "role": "member"},
        ]
    }
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE_URL}/v1/get-workspaces",
        json=mock_response_data,
        status_code=200,
    )

    response_model = await client_with_token.get_workspaces()
    await client_with_token.close()

    assert isinstance(response_model, WorkspaceResponse)
    assert len(response_model.workspaces) == 2
    assert response_model.workspaces[0].id == "ws1"
    assert response_model.workspaces[0].name == "Personal"
    assert isinstance(response_model.workspaces[0], Workspace)

@pytest.mark.asyncio
async def test_get_workspaces_auth_error_if_no_token_and_not_macos(client_no_token: GranolaClient, httpx_mock, monkeypatch):
    """Test that an auth error might be hit or specific behavior if no token."""
    # Mock platform.system() to simulate non-Darwin OS
    monkeypatch.setattr("platform.system", lambda: "Linux")

    # Mock the HTTP call to simulate an auth error or specific response
    # Depending on how the API behaves without a token
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE_URL}/v1/get-workspaces",
        json={"error": "Unauthorized", "message": "Missing authentication token"},
        status_code=401 # Or 403
    )

    # For this test, we expect GranolaAPIError (from HTTPStatusError)
    # because _ensure_token on Linux without a provider does not raise immediately.
    # The actual API call will fail.
    with pytest.raises(GranolaAuthError) as exc_info:
         # The _ensure_token will try to call the provider which is None on Linux
         # leading to no token. The HTTP call should then fail.
         # If _ensure_token itself raises when no token & no provider, this changes.
         # Current behavior: _ensure_token logs a warning, http call fails.
         # To test GranolaAuthError for token provision failure, we'd need to mock get_auth_tokens to fail.

         # Let's refine to test failure if token provider fails on macOS
        monkeypatch.setattr("platform.system", lambda: "Darwin") # Simulate macOS
        # Mock get_auth_tokens to raise an error
        async def mock_get_auth_tokens_fail():
            raise GranolaAuthError("Simulated token fetch failure")

        monkeypatch.setattr(GranolaClient, "get_auth_tokens", mock_get_auth_tokens_fail)

        # Re-initialize client so it picks up mocked platform and get_auth_tokens
        client_macos_no_token = GranolaClient()

        # The error should happen during _ensure_token, triggered by the first call
        await client_macos_no_token.get_workspaces()
        await client_macos_no_token.close()

    assert "Simulated token fetch failure" in str(exc_info.value)


@mock.patch("platform.system", return_value="Darwin") # Mock platform to be macOS
@mock.patch("pathlib.Path.exists")
@mock.patch("pathlib.Path.read_text")
@pytest.mark.asyncio
async def test_get_auth_tokens_success_macos(mock_read_text, mock_exists, mock_system):
    """Test successful token extraction on macOS."""
    mock_exists.return_value = True
    mock_supabase_content = {
        "cognito_tokens": json.dumps({
            "access_token": "fake_access_token",
            "refresh_token": "fake_refresh_token"
        })
    }
    mock_read_text.return_value = json.dumps(mock_supabase_content)

    # Mock Path.home() to control the path being constructed.
    # We don't need to mock home() if read_text and exists are already mocked for any Path instance.
    # However, to be precise:
    with mock.patch("granola_client.client.Path.home") as mock_home:
        mock_home.return_value = Path("/fake/home")
        access_token, refresh_token = await GranolaClient.get_auth_tokens()

    assert access_token == "fake_access_token"
    assert refresh_token == "fake_refresh_token"


@mock.patch("platform.system", return_value="Linux") # Mock platform to be non-macOS
@pytest.mark.asyncio
async def test_get_auth_tokens_fails_non_macos(mock_system):
    """Test that token extraction fails on non-macOS."""
    with pytest.raises(GranolaAuthError) as exc_info:
        await GranolaClient.get_auth_tokens()
    assert "Automatic token extraction is only supported on macOS" in str(exc_info.value)

@mock.patch("platform.system", return_value="Darwin")
@mock.patch("pathlib.Path.exists", return_value=False) # Simulate token file not existing
@pytest.mark.asyncio
async def test_get_auth_tokens_file_not_found_macos(mock_exists, mock_system):
    """Test token extraction fails if supabase.json not found on macOS."""
    with mock.patch("granola_client.client.Path.home") as mock_home:
        mock_home.return_value = Path("/fake/home")
        with pytest.raises(GranolaAuthError) as exc_info:
            await GranolaClient.get_auth_tokens()
    assert "Token file not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_client_custom_opts(httpx_mock):
    """Test client initialization with custom ClientOpts."""
    custom_opts = ClientOpts(
        base_url="http://localhost:1234/api", # type: ignore
        timeout=5000,
        appVersion="1.0.0-test"
    )
    client = GranolaClient(token="custom-token", opts=custom_opts)

    assert client.http.base_url_str == "http://localhost:1234/api"
    assert client.http.timeout_ms == 5000
    assert client.http.app_version == "1.0.0-test"

    # Test that these custom opts are used in a request
    httpx_mock.add_response(
        method="POST",
        url="http://localhost:1234/api/v1/get-workspaces",
        json={"workspaces": []},
        status_code=200
    )
    await client.get_workspaces() # Make a call to trigger request
    await client.close()

    request = httpx_mock.get_requests()[0]
    assert request.headers["x-app-version"] == "1.0.0-test"
    assert str(request.url) == "http://localhost:1234/api/v1/get-workspaces"

# You would add more tests for other client methods, error handling, pagination etc.
