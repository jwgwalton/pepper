"""
Unit tests for token storage
"""
import pytest
from datetime import datetime, timedelta
from app.token_storage import TokenStorage


@pytest.fixture
def storage():
    """Create a fresh token storage instance for each test"""
    return TokenStorage()


class TestTokenStorage:
    """Tests for token storage functionality"""

    def test_store_and_retrieve_code_verifier(self, storage):
        """Test storing and retrieving PKCE code verifier"""
        state = "test_state_123"
        verifier = "test_verifier_xyz"

        storage.store_code_verifier(state, verifier)
        retrieved = storage.get_code_verifier(state)

        assert retrieved == verifier

    def test_get_code_verifier_removes_it(self, storage):
        """Test that getting a code verifier removes it from storage"""
        state = "test_state_123"
        verifier = "test_verifier_xyz"

        storage.store_code_verifier(state, verifier)
        storage.get_code_verifier(state)
        # Second retrieval should return None
        retrieved = storage.get_code_verifier(state)

        assert retrieved is None

    def test_get_nonexistent_code_verifier(self, storage):
        """Test retrieving a non-existent code verifier"""
        retrieved = storage.get_code_verifier("nonexistent")
        assert retrieved is None

    def test_store_and_retrieve_tokens(self, storage):
        """Test storing and retrieving user tokens"""
        user_id = "user123"
        tokens = {
            "access_token": "access_token_xyz",
            "refresh_token": "refresh_token_abc",
            "expires_in": 3600,
            "scope": "User.Read Mail.Read",
            "token_type": "Bearer"
        }

        storage.store_tokens(user_id, tokens)
        retrieved = storage.get_tokens(user_id)

        assert retrieved is not None
        assert retrieved["access_token"] == tokens["access_token"]
        assert retrieved["refresh_token"] == tokens["refresh_token"]
        assert retrieved["expires_in"] == tokens["expires_in"]
        assert "stored_at" in retrieved

    def test_get_nonexistent_tokens(self, storage):
        """Test retrieving tokens for non-existent user"""
        retrieved = storage.get_tokens("nonexistent_user")
        assert retrieved is None

    def test_delete_tokens(self, storage):
        """Test deleting user tokens"""
        user_id = "user123"
        tokens = {
            "access_token": "access_token_xyz",
            "expires_in": 3600
        }

        storage.store_tokens(user_id, tokens)
        assert storage.get_tokens(user_id) is not None

        deleted = storage.delete_tokens(user_id)
        assert deleted is True
        assert storage.get_tokens(user_id) is None

    def test_delete_nonexistent_tokens(self, storage):
        """Test deleting tokens for non-existent user"""
        deleted = storage.delete_tokens("nonexistent_user")
        assert deleted is False

    def test_is_token_expired_not_expired(self, storage):
        """Test checking if token is expired (not expired case)"""
        user_id = "user123"
        tokens = {
            "access_token": "access_token_xyz",
            "expires_in": 3600  # 1 hour
        }

        storage.store_tokens(user_id, tokens)
        is_expired = storage.is_token_expired(user_id)

        assert is_expired is False

    def test_is_token_expired_expired(self, storage):
        """Test checking if token is expired (expired case)"""
        user_id = "user123"
        tokens = {
            "access_token": "access_token_xyz",
            "expires_in": -1  # Already expired
        }

        storage.store_tokens(user_id, tokens)
        is_expired = storage.is_token_expired(user_id)

        assert is_expired is True

    def test_is_token_expired_nonexistent(self, storage):
        """Test checking if token is expired for non-existent user"""
        is_expired = storage.is_token_expired("nonexistent_user")
        assert is_expired is True

    def test_token_encryption(self, storage):
        """Test that tokens are encrypted in storage"""
        user_id = "user123"
        tokens = {
            "access_token": "very_secret_token",
            "expires_in": 3600
        }

        storage.store_tokens(user_id, tokens)

        # Access internal storage - token should be encrypted
        encrypted = storage._tokens[user_id]
        assert isinstance(encrypted, bytes)
        # Should not contain the plaintext token
        assert b"very_secret_token" not in encrypted

    def test_update_tokens(self, storage):
        """Test updating tokens for same user"""
        user_id = "user123"
        old_tokens = {
            "access_token": "old_token",
            "expires_in": 3600
        }
        new_tokens = {
            "access_token": "new_token",
            "expires_in": 7200
        }

        storage.store_tokens(user_id, old_tokens)
        storage.store_tokens(user_id, new_tokens)
        retrieved = storage.get_tokens(user_id)

        assert retrieved["access_token"] == "new_token"
        assert retrieved["expires_in"] == 7200
