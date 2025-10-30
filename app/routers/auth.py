"""
OAuth 2.0 authentication routes for Microsoft Azure AD
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import msal
import secrets
from app.config import settings
from app.pkce import generate_pkce_pair
from app.token_storage import token_storage


router = APIRouter(prefix="/auth", tags=["authentication"])


class TokenRefreshRequest(BaseModel):
    """Request body for token refresh"""
    user_id: str


class LogoutRequest(BaseModel):
    """Request body for logout"""
    user_id: str


def get_msal_app():
    """Create and return MSAL ConfidentialClientApplication"""
    return msal.ConfidentialClientApplication(
        settings.client_id,
        authority=f"https://login.microsoftonline.com/{settings.tenant_id}",
        client_credential=settings.client_secret if settings.client_secret else None,
    )


@router.get("/login")
async def login():
    """
    Initiate OAuth 2.0 login flow with PKCE.
    Redirects user to Microsoft login page.
    """
    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store code verifier for later use
    token_storage.store_code_verifier(state, code_verifier)

    # Build authorization URL
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=settings.scopes,
        state=state,
        redirect_uri=settings.redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )

    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(
    code: str = Query(..., description="Authorization code from Microsoft"),
    state: str = Query(..., description="State parameter for CSRF protection")
):
    """
    Handle OAuth callback from Microsoft.
    Exchanges authorization code for access token.
    """
    # Retrieve code verifier
    code_verifier = token_storage.get_code_verifier(state)
    if not code_verifier:
        raise HTTPException(
            status_code=400,
            detail="Invalid state parameter or code verifier expired"
        )

    # Exchange code for tokens
    msal_app = get_msal_app()
    try:
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=settings.scopes,
            redirect_uri=settings.redirect_uri,
            code_verifier=code_verifier
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to acquire token: {str(e)}"
        )

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=f"Authentication failed: {result.get('error_description', result['error'])}"
        )

    # Extract user ID from token (use 'oid' claim as unique identifier)
    user_id = result.get("id_token_claims", {}).get("oid")
    if not user_id:
        raise HTTPException(
            status_code=500,
            detail="Failed to extract user ID from token"
        )

    # Store tokens securely
    token_storage.store_tokens(user_id, {
        "access_token": result["access_token"],
        "refresh_token": result.get("refresh_token"),
        "expires_in": result.get("expires_in", 3600),
        "scope": result.get("scope", ""),
        "token_type": result.get("token_type", "Bearer")
    })

    return {
        "message": "Authentication successful",
        "user_id": user_id,
        "scopes": result.get("scope", "").split(" ")
    }


@router.post("/refresh")
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh an expired access token using refresh token.
    """
    # Get current tokens
    tokens = token_storage.get_tokens(request.user_id)
    if not tokens:
        raise HTTPException(
            status_code=404,
            detail="No tokens found for this user"
        )

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="No refresh token available"
        )

    # Acquire new token using refresh token
    msal_app = get_msal_app()
    try:
        result = msal_app.acquire_token_by_refresh_token(
            refresh_token,
            scopes=settings.scopes
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh token: {str(e)}"
        )

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=f"Token refresh failed: {result.get('error_description', result['error'])}"
        )

    # Update stored tokens
    token_storage.store_tokens(request.user_id, {
        "access_token": result["access_token"],
        "refresh_token": result.get("refresh_token", refresh_token),
        "expires_in": result.get("expires_in", 3600),
        "scope": result.get("scope", ""),
        "token_type": result.get("token_type", "Bearer")
    })

    return {
        "message": "Token refreshed successfully",
        "user_id": request.user_id
    }


@router.post("/logout")
async def logout(request: LogoutRequest):
    """
    Revoke tokens and log out user.
    Note: This removes tokens from storage. Full revocation requires
    calling Microsoft's token revocation endpoint.
    """
    deleted = token_storage.delete_tokens(request.user_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="No active session found for this user"
        )

    return {
        "message": "Logged out successfully",
        "user_id": request.user_id
    }


@router.get("/status/{user_id}")
async def auth_status(user_id: str):
    """
    Check authentication status for a user.
    """
    tokens = token_storage.get_tokens(user_id)

    if not tokens:
        return {
            "authenticated": False,
            "user_id": user_id
        }

    is_expired = token_storage.is_token_expired(user_id)

    return {
        "authenticated": True,
        "user_id": user_id,
        "token_expired": is_expired,
        "has_refresh_token": bool(tokens.get("refresh_token"))
    }
