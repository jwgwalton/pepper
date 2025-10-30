"""
Unit tests for PKCE utilities
"""
import pytest
import base64
import hashlib
from app.pkce import (
    generate_code_verifier,
    generate_code_challenge,
    generate_pkce_pair
)


class TestPKCE:
    """Tests for PKCE code generation"""

    def test_generate_code_verifier_default_length(self):
        """Test code verifier generation with default length"""
        verifier = generate_code_verifier()
        assert len(verifier) == 128
        # Should be URL-safe base64
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in verifier)

    def test_generate_code_verifier_custom_length(self):
        """Test code verifier generation with custom length"""
        verifier = generate_code_verifier(length=64)
        assert len(verifier) == 64

    def test_generate_code_verifier_invalid_length(self):
        """Test code verifier generation with invalid length"""
        with pytest.raises(ValueError):
            generate_code_verifier(length=30)  # Too short
        with pytest.raises(ValueError):
            generate_code_verifier(length=150)  # Too long

    def test_generate_code_challenge(self):
        """Test code challenge generation"""
        verifier = "test_verifier_1234567890"
        challenge = generate_code_challenge(verifier)

        # Verify it's a valid base64 string
        assert len(challenge) > 0
        # Should be URL-safe base64 without padding
        assert '=' not in challenge

        # Verify it matches SHA256 hash
        expected_hash = hashlib.sha256(verifier.encode()).digest()
        expected_challenge = base64.urlsafe_b64encode(expected_hash).decode('utf-8').rstrip('=')
        assert challenge == expected_challenge

    def test_generate_pkce_pair(self):
        """Test generating verifier and challenge pair"""
        verifier, challenge = generate_pkce_pair()

        # Verify verifier
        assert len(verifier) == 128
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in verifier)

        # Verify challenge
        assert len(challenge) > 0
        expected_hash = hashlib.sha256(verifier.encode()).digest()
        expected_challenge = base64.urlsafe_b64encode(expected_hash).decode('utf-8').rstrip('=')
        assert challenge == expected_challenge

    def test_verifier_uniqueness(self):
        """Test that generated verifiers are unique"""
        verifiers = [generate_code_verifier() for _ in range(100)]
        # All should be unique
        assert len(set(verifiers)) == 100
