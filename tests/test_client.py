import pytest
import json
from pathlib import Path
from unittest import mock # For mocking Path.home in get_auth_tokens test

from granola_client import GranolaClient, GranolaAuthError

# Base URL for mocking
BASE_URL = "https://api.granola.ai"

@pytest.fixture
def client_no_token():
    # Client without a token for testing auth retrieval or public endpoints
    return GranolaClient()

@pytest.fixture
def client_with_token():
    return GranolaClient(token="test-token")


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
