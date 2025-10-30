"""
Secure token storage system
"""
from typing import Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import json
import base64
import hashlib
from app.config import settings


class TokenStorage:
    """
    In-memory token storage with encryption.
    Note: In production, this should be replaced with a proper database.
    """

    def __init__(self):
        """Initialize token storage with encryption"""
        # Generate encryption key from secret
        key = hashlib.sha256(settings.secret_key.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
        self._tokens: dict[str, bytes] = {}
        self._verifiers: dict[str, str] = {}

    def store_code_verifier(self, state: str, code_verifier: str) -> None:
        """
        Store PKCE code verifier temporarily during OAuth flow.

        Args:
            state: OAuth state parameter (used as key)
            code_verifier: The PKCE code verifier to store
        """
        self._verifiers[state] = code_verifier

    def get_code_verifier(self, state: str) -> Optional[str]:
        """
        Retrieve and remove PKCE code verifier.

        Args:
            state: OAuth state parameter

        Returns:
            The code verifier or None if not found
        """
        return self._verifiers.pop(state, None)

    def store_tokens(self, user_id: str, tokens: dict) -> None:
        """
        Store user tokens securely with encryption.

        Args:
            user_id: Unique identifier for the user
            tokens: Dictionary containing access_token, refresh_token, expires_in, etc.
        """
        # Add timestamp
        tokens["stored_at"] = datetime.utcnow().isoformat()

        # Serialize and encrypt
        token_json = json.dumps(tokens)
        encrypted = self.cipher.encrypt(token_json.encode())
        self._tokens[user_id] = encrypted

    def get_tokens(self, user_id: str) -> Optional[dict]:
        """
        Retrieve and decrypt user tokens.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing tokens or None if not found
        """
        encrypted = self._tokens.get(user_id)
        if not encrypted:
            return None

        try:
            decrypted = self.cipher.decrypt(encrypted)
            tokens = json.loads(decrypted.decode())
            return tokens
        except Exception:
            # If decryption fails, remove corrupted data
            self._tokens.pop(user_id, None)
            return None

    def delete_tokens(self, user_id: str) -> bool:
        """
        Delete user tokens.

        Args:
            user_id: Unique identifier for the user

        Returns:
            True if tokens were deleted, False if not found
        """
        if user_id in self._tokens:
            del self._tokens[user_id]
            return True
        return False

    def is_token_expired(self, user_id: str) -> bool:
        """
        Check if access token is expired.

        Args:
            user_id: Unique identifier for the user

        Returns:
            True if token is expired or not found
        """
        tokens = self.get_tokens(user_id)
        if not tokens:
            return True

        stored_at = datetime.fromisoformat(tokens.get("stored_at", ""))
        expires_in = tokens.get("expires_in", 0)
        expiry_time = stored_at + timedelta(seconds=expires_in)

        return datetime.utcnow() >= expiry_time


# Global token storage instance
token_storage = TokenStorage()
