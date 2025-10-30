"""
Unit tests for OAuth authentication routes
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.token_storage import token_storage


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_msal_app():
    """Mock MSAL application"""
    mock_app = MagicMock()
    return mock_app


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear token storage before each test"""
    token_storage._tokens.clear()
    token_storage._verifiers.clear()
    yield


class TestAuthLogin:
    """Tests for /auth/login endpoint"""

    @patch('app.routers.auth.get_msal_app')
    def test_login_redirect(self, mock_get_msal, client):
        """Test login endpoint redirects to Microsoft"""
        mock_app = MagicMock()
        mock_app.get_authorization_request_url.return_value = "https://login.microsoft.com/auth?code=xyz"
        mock_get_msal.return_value = mock_app

        response = client.get("/auth/login", follow_redirects=False)

        assert response.status_code == 307  # Redirect
        assert "login.microsoft.com" in response.headers["location"]
        # Verify MSAL was called with PKCE parameters
        mock_app.get_authorization_request_url.assert_called_once()
        call_kwargs = mock_app.get_authorization_request_url.call_args[1]
        assert "code_challenge" in call_kwargs
        assert call_kwargs["code_challenge_method"] == "S256"


class TestAuthCallback:
    """Tests for /auth/callback endpoint"""

    @patch('app.routers.auth.get_msal_app')
    def test_callback_success(self, mock_get_msal, client):
        """Test successful OAuth callback"""
        # Store a code verifier first
        token_storage.store_code_verifier("test_state", "test_verifier")

        mock_app = MagicMock()
        mock_app.acquire_token_by_authorization_code.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "scope": "User.Read Mail.Read",
            "token_type": "Bearer",
            "id_token_claims": {
                "oid": "user123"
            }
        }
        mock_get_msal.return_value = mock_app

        response = client.get("/auth/callback?code=test_code&state=test_state")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Authentication successful"
        assert data["user_id"] == "user123"

        # Verify tokens were stored
        stored_tokens = token_storage.get_tokens("user123")
        assert stored_tokens is not None
        assert stored_tokens["access_token"] == "test_access_token"

    @patch('app.routers.auth.get_msal_app')
    def test_callback_invalid_state(self, mock_get_msal, client):
        """Test callback with invalid state parameter"""
        response = client.get("/auth/callback?code=test_code&state=invalid_state")

        assert response.status_code == 400
        assert "Invalid state parameter" in response.json()["detail"]

    @patch('app.routers.auth.get_msal_app')
    def test_callback_auth_error(self, mock_get_msal, client):
        """Test callback when authentication fails"""
        token_storage.store_code_verifier("test_state", "test_verifier")

        mock_app = MagicMock()
        mock_app.acquire_token_by_authorization_code.return_value = {
            "error": "invalid_grant",
            "error_description": "Authorization code expired"
        }
        mock_get_msal.return_value = mock_app

        response = client.get("/auth/callback?code=test_code&state=test_state")

        assert response.status_code == 400
        assert "Authentication failed" in response.json()["detail"]


class TestAuthRefresh:
    """Tests for /auth/refresh endpoint"""

    @patch('app.routers.auth.get_msal_app')
    def test_refresh_success(self, mock_get_msal, client):
        """Test successful token refresh"""
        # Store initial tokens
        token_storage.store_tokens("user123", {
            "access_token": "old_token",
            "refresh_token": "refresh_token_xyz",
            "expires_in": 3600
        })

        mock_app = MagicMock()
        mock_app.acquire_token_by_refresh_token.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "scope": "User.Read Mail.Read",
            "token_type": "Bearer"
        }
        mock_get_msal.return_value = mock_app

        response = client.post("/auth/refresh", json={"user_id": "user123"})

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Token refreshed successfully"

        # Verify new tokens were stored
        stored_tokens = token_storage.get_tokens("user123")
        assert stored_tokens["access_token"] == "new_access_token"

    def test_refresh_no_tokens(self, client):
        """Test refresh when no tokens exist"""
        response = client.post("/auth/refresh", json={"user_id": "nonexistent"})

        assert response.status_code == 404
        assert "No tokens found" in response.json()["detail"]

    @patch('app.routers.auth.get_msal_app')
    def test_refresh_error(self, mock_get_msal, client):
        """Test refresh when refresh fails"""
        token_storage.store_tokens("user123", {
            "access_token": "old_token",
            "refresh_token": "refresh_token_xyz",
            "expires_in": 3600
        })

        mock_app = MagicMock()
        mock_app.acquire_token_by_refresh_token.return_value = {
            "error": "invalid_grant",
            "error_description": "Refresh token expired"
        }
        mock_get_msal.return_value = mock_app

        response = client.post("/auth/refresh", json={"user_id": "user123"})

        assert response.status_code == 400
        assert "Token refresh failed" in response.json()["detail"]


class TestAuthLogout:
    """Tests for /auth/logout endpoint"""

    def test_logout_success(self, client):
        """Test successful logout"""
        # Store tokens first
        token_storage.store_tokens("user123", {
            "access_token": "token_xyz",
            "expires_in": 3600
        })

        response = client.post("/auth/logout", json={"user_id": "user123"})

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

        # Verify tokens were deleted
        assert token_storage.get_tokens("user123") is None

    def test_logout_no_session(self, client):
        """Test logout when no session exists"""
        response = client.post("/auth/logout", json={"user_id": "nonexistent"})

        assert response.status_code == 404
        assert "No active session found" in response.json()["detail"]


class TestAuthStatus:
    """Tests for /auth/status endpoint"""

    def test_status_authenticated(self, client):
        """Test status for authenticated user"""
        token_storage.store_tokens("user123", {
            "access_token": "token_xyz",
            "refresh_token": "refresh_xyz",
            "expires_in": 3600
        })

        response = client.get("/auth/status/user123")

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user_id"] == "user123"
        assert data["token_expired"] is False
        assert data["has_refresh_token"] is True

    def test_status_not_authenticated(self, client):
        """Test status for non-authenticated user"""
        response = client.get("/auth/status/nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user_id"] == "nonexistent"

    def test_status_expired_token(self, client):
        """Test status with expired token"""
        token_storage.store_tokens("user123", {
            "access_token": "token_xyz",
            "expires_in": -1  # Expired
        })

        response = client.get("/auth/status/user123")

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["token_expired"] is True
