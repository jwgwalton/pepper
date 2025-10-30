"""
PKCE (Proof Key for Code Exchange) utilities for OAuth 2.0
"""
import base64
import hashlib
import secrets


def generate_code_verifier(length: int = 128) -> str:
    """
    Generate a cryptographically random code verifier for PKCE.

    Args:
        length: Length of the verifier (43-128 characters)

    Returns:
        Base64 URL-encoded random string
    """
    if not 43 <= length <= 128:
        raise ValueError("Code verifier length must be between 43 and 128")

    # Generate random bytes
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(96)).decode('utf-8')
    # Remove padding and truncate to desired length
    return code_verifier.rstrip('=')[:length]


def generate_code_challenge(code_verifier: str) -> str:
    """
    Generate a code challenge from a code verifier using SHA256.

    Args:
        code_verifier: The code verifier string

    Returns:
        Base64 URL-encoded SHA256 hash of the verifier
    """
    # Hash the verifier
    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    # Base64 URL encode without padding
    code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    return code_challenge


def generate_pkce_pair() -> tuple[str, str]:
    """
    Generate a PKCE code verifier and challenge pair.

    Returns:
        Tuple of (code_verifier, code_challenge)
    """
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    return code_verifier, code_challenge
