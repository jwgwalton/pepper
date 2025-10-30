"""
Utility functions for working with Microsoft Graph API client.
Provides easy integration between token storage and GraphClient.
"""
from typing import Optional
from app.graph_client import GraphClient, TokenExpiredError
from app.token_storage import token_storage


def get_graph_client(user_id: str) -> Optional[GraphClient]:
    """
    Create a GraphClient instance for a user using their stored access token.

    Args:
        user_id: User ID to retrieve tokens for

    Returns:
        GraphClient instance if tokens exist and are valid, None otherwise

    Example:
        >>> client = get_graph_client("user123")
        >>> if client:
        ...     emails = client.search_emails(query="urgent")
    """
    tokens = token_storage.get_tokens(user_id)
    if not tokens:
        return None

    access_token = tokens.get("access_token")
    if not access_token:
        return None

    return GraphClient(access_token)


def ensure_valid_token(user_id: str) -> bool:
    """
    Check if user has a valid token, considering expiration.

    Args:
        user_id: User ID to check

    Returns:
        True if user has a valid non-expired token

    Example:
        >>> if ensure_valid_token("user123"):
        ...     # Token is valid, proceed with API call
        ... else:
        ...     # Need to refresh or re-authenticate
    """
    tokens = token_storage.get_tokens(user_id)
    if not tokens:
        return False

    if token_storage.is_token_expired(user_id):
        return False

    return True
