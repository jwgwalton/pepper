# OAuth 2.0 Implementation - Technical Documentation

## Overview

This document provides a comprehensive explanation of the OAuth 2.0 implementation in the Pepper application. Our implementation uses the **Authorization Code Flow with PKCE (Proof Key for Code Exchange)** to securely authenticate users with Microsoft Azure AD and obtain access tokens for Microsoft Graph API operations.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [OAuth Flow Diagram](#oauth-flow-diagram)
- [Components Explained](#components-explained)
- [Security Features](#security-features)
- [Code Walkthrough](#code-walkthrough)
- [Token Lifecycle](#token-lifecycle)
- [Error Handling](#error-handling)

---

## Architecture Overview

The OAuth implementation consists of five main components:

```
┌─────────────────┐
│  Configuration  │  ← Environment variables, settings
│   (config.py)   │
└─────────────────┘
        │
        ▼
┌─────────────────┐     ┌──────────────────┐
│   PKCE Utils    │────▶│  OAuth Router    │  ← API endpoints
│   (pkce.py)     │     │ (routers/auth.py)│
└─────────────────┘     └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Token Storage   │  ← Encrypted storage
                        │(token_storage.py)│
                        └──────────────────┘
```

### Component Responsibilities

1. **Configuration** (`app/config.py`): Manages environment variables and application settings
2. **PKCE Utilities** (`app/pkce.py`): Generates cryptographically secure PKCE parameters
3. **Token Storage** (`app/token_storage.py`): Encrypts and stores OAuth tokens securely
4. **OAuth Router** (`app/routers/auth.py`): Implements the OAuth endpoints and flow logic

---

## OAuth Flow Diagram

Here's the complete OAuth 2.0 Authorization Code Flow with PKCE:

```
┌──────────┐                                                    ┌────────────┐
│  Client  │                                                    │   Azure    │
│ (Browser)│                                                    │     AD     │
└────┬─────┘                                                    └─────┬──────┘
     │                                                                 │
     │  1. GET /auth/login                                            │
     ├────────────────────────────▶┌───────────────┐                 │
     │                              │  Pepper API   │                 │
     │                              └───────┬───────┘                 │
     │                                      │                         │
     │                              2. Generate PKCE pair             │
     │                                 (verifier, challenge)          │
     │                                      │                         │
     │                              3. Store verifier                 │
     │                                 with state                     │
     │                                      │                         │
     │  4. Redirect to Microsoft            │                         │
     │     with code_challenge         ─────┘                         │
     ├────────────────────────────────────────────────────────────────▶
     │                                                                 │
     │  5. User authenticates                                         │
     │     and consents                                               │
     │◀────────────────────────────────────────────────────────────────│
     │                                                                 │
     │  6. Redirect back with                                         │
     │     authorization code + state                                 │
     ├────────────────────────────▶┌───────────────┐                 │
     │                              │  Pepper API   │                 │
     │                              └───────┬───────┘                 │
     │                                      │                         │
     │                              7. Retrieve verifier              │
     │                                 using state                    │
     │                                      │                         │
     │                              8. Exchange code                  │
     │                                 for tokens with                │
     │                                 code_verifier                  │
     │                                      ├──────────────────────────▶
     │                                      │                         │
     │                                      │ 9. Validate PKCE        │
     │                                      │    and return tokens    │
     │                                      │◀────────────────────────│
     │                                      │                         │
     │                              10. Encrypt & store tokens        │
     │                                      │                         │
     │  11. Return user_id                  │                         │
     │     and success message              │                         │
     │◀─────────────────────────────────────┘                         │
     │                                                                 │
```

---

## Components Explained

### 1. Configuration (`app/config.py`)

The configuration module uses Pydantic Settings to load and validate environment variables.

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

    # Azure AD Configuration
    client_id: str = ""
    tenant_id: str = ""
    redirect_uri: str = "http://localhost:8000/auth/callback"
    client_secret: str = ""

    # OAuth Scopes - Permissions requested from Microsoft Graph
    scopes: list[str] = [
        "User.Read",           # Read user profile
        "Mail.ReadWrite",      # Read and write mail
        "Mail.Send",           # Send mail
        "Calendars.ReadWrite", # Manage calendar
        "MailboxSettings.Read" # Read mailbox settings
    ]

    # Security - Used for token encryption
    secret_key: str = "your-secret-key-change-in-production"
```

**Key Features:**
- Type-safe configuration with Pydantic validation
- Automatic `.env` file loading
- Default values for development
- Scopes define what permissions we request from Microsoft

---

### 2. PKCE Utilities (`app/pkce.py`)

PKCE (Proof Key for Code Exchange) adds security to the OAuth flow by preventing authorization code interception attacks.

#### How PKCE Works

1. **Code Verifier**: A high-entropy cryptographic random string (43-128 characters)
2. **Code Challenge**: SHA256 hash of the code verifier, base64-url encoded
3. The challenge is sent during authorization, the verifier during token exchange
4. Azure AD verifies that the verifier matches the original challenge

#### Implementation

```python
def generate_code_verifier(length: int = 128) -> str:
    """Generate a cryptographically random code verifier."""
    # Use secrets module for cryptographic randomness
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(96)).decode('utf-8')
    return code_verifier.rstrip('=')[:length]

def generate_code_challenge(code_verifier: str) -> str:
    """Generate SHA256 code challenge from verifier."""
    # Hash the verifier
    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    # Base64 URL encode without padding
    code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    return code_challenge
```

**Security Benefits:**
- Even if an attacker intercepts the authorization code, they can't use it without the verifier
- The verifier is stored server-side and never exposed to the browser
- SHA256 ensures the verifier can't be derived from the challenge

---

### 3. Token Storage (`app/token_storage.py`)

The token storage system provides encrypted, in-memory storage for OAuth tokens.

#### Token Structure

```python
{
    "access_token": "eyJ0eXAiOiJKV1...",  # JWT token for API calls
    "refresh_token": "M.R3_BAY...",       # Long-lived token for refreshing
    "expires_in": 3600,                    # Token lifetime in seconds
    "scope": "User.Read Mail.ReadWrite",   # Granted permissions
    "token_type": "Bearer",                # Token type for Authorization header
    "stored_at": "2025-10-30T12:00:00"    # Timestamp for expiration checking
}
```

#### Encryption Implementation

```python
class TokenStorage:
    def __init__(self):
        # Generate encryption key from secret
        key = hashlib.sha256(settings.secret_key.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
        self._tokens: dict[str, bytes] = {}  # Encrypted tokens
        self._verifiers: dict[str, str] = {}  # Temporary PKCE verifiers

    def store_tokens(self, user_id: str, tokens: dict) -> None:
        """Store tokens with encryption."""
        tokens["stored_at"] = datetime.utcnow().isoformat()

        # Serialize and encrypt
        token_json = json.dumps(tokens)
        encrypted = self.cipher.encrypt(token_json.encode())
        self._tokens[user_id] = encrypted  # Stored as encrypted bytes
```

**Key Features:**
- **Fernet Encryption**: Uses AES-128 in CBC mode with HMAC for authentication
- **Automatic Timestamps**: Tracks when tokens were stored for expiration checking
- **PKCE Verifier Storage**: Temporarily stores verifiers during OAuth flow
- **One-Time Retrieval**: Code verifiers are removed after use (prevents replay)

#### Expiration Checking

```python
def is_token_expired(self, user_id: str) -> bool:
    """Check if access token is expired."""
    tokens = self.get_tokens(user_id)
    if not tokens:
        return True

    stored_at = datetime.fromisoformat(tokens.get("stored_at"))
    expires_in = tokens.get("expires_in", 0)
    expiry_time = stored_at + timedelta(seconds=expires_in)

    return datetime.utcnow() >= expiry_time
```

**Note**: In production, replace in-memory storage with a database (PostgreSQL, Redis, etc.) for persistence and scalability.

---

### 4. OAuth Router (`app/routers/auth.py`)

The OAuth router implements all the endpoints needed for the complete authentication flow.

#### Endpoint: `GET /auth/login`

**Purpose**: Initiates the OAuth flow by redirecting to Microsoft's login page.

```python
@router.get("/auth/login")
async def login():
    # 1. Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # 2. Generate state for CSRF protection
    state = secrets.token_urlsafe(32)  # Cryptographically random

    # 3. Store verifier temporarily (keyed by state)
    token_storage.store_code_verifier(state, code_verifier)

    # 4. Build authorization URL
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=settings.scopes,
        state=state,
        redirect_uri=settings.redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method="S256"  # SHA256
    )

    # 5. Redirect user to Microsoft
    return RedirectResponse(url=auth_url)
```

**Flow**:
1. Generate unique PKCE pair for this authorization attempt
2. Generate state parameter to prevent CSRF attacks
3. Store the verifier (we'll need it later to exchange the code)
4. Build Microsoft authorization URL with PKCE challenge
5. Redirect browser to Microsoft login

---

#### Endpoint: `GET /auth/callback`

**Purpose**: Handles the redirect back from Microsoft after user authentication.

```python
@router.get("/auth/callback")
async def callback(
    code: str = Query(...),    # Authorization code from Microsoft
    state: str = Query(...)    # State parameter for verification
):
    # 1. Retrieve and verify code verifier
    code_verifier = token_storage.get_code_verifier(state)
    if not code_verifier:
        raise HTTPException(400, "Invalid state parameter")

    # 2. Exchange authorization code for tokens
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=settings.scopes,
        redirect_uri=settings.redirect_uri,
        code_verifier=code_verifier  # Prove we initiated the request
    )

    # 3. Check for errors
    if "error" in result:
        raise HTTPException(400, f"Authentication failed: {result['error']}")

    # 4. Extract user ID from token claims
    user_id = result.get("id_token_claims", {}).get("oid")

    # 5. Store tokens securely
    token_storage.store_tokens(user_id, {
        "access_token": result["access_token"],
        "refresh_token": result.get("refresh_token"),
        "expires_in": result.get("expires_in", 3600),
        "scope": result.get("scope", ""),
        "token_type": result.get("token_type", "Bearer")
    })

    return {
        "message": "Authentication successful",
        "user_id": user_id
    }
```

**Flow**:
1. Verify the state parameter and retrieve the code verifier
2. Use MSAL to exchange the authorization code for tokens (includes PKCE verification)
3. Azure AD validates the code_verifier matches the original code_challenge
4. Extract the user's unique ID (`oid` claim) from the ID token
5. Encrypt and store the tokens for future API calls

---

#### Endpoint: `POST /auth/refresh`

**Purpose**: Refresh an expired access token using the refresh token.

```python
@router.post("/auth/refresh")
async def refresh_token(request: TokenRefreshRequest):
    # 1. Get current tokens
    tokens = token_storage.get_tokens(request.user_id)
    if not tokens or not tokens.get("refresh_token"):
        raise HTTPException(404, "No refresh token available")

    # 2. Acquire new token using refresh token
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_refresh_token(
        tokens["refresh_token"],
        scopes=settings.scopes
    )

    # 3. Check for errors
    if "error" in result:
        raise HTTPException(400, f"Token refresh failed: {result['error']}")

    # 4. Update stored tokens
    token_storage.store_tokens(request.user_id, {
        "access_token": result["access_token"],
        "refresh_token": result.get("refresh_token", tokens["refresh_token"]),
        "expires_in": result.get("expires_in", 3600),
        "scope": result.get("scope", ""),
        "token_type": result.get("token_type", "Bearer")
    })

    return {"message": "Token refreshed successfully"}
```

**Important Notes**:
- Access tokens typically expire after 1 hour
- Refresh tokens can last up to 90 days (configurable in Azure AD)
- Always update the stored refresh token (Microsoft may rotate it)
- Call this endpoint before making API calls if the token is expired

---

#### Endpoint: `POST /auth/logout`

**Purpose**: Revoke tokens and clear the user's session.

```python
@router.post("/auth/logout")
async def logout(request: LogoutRequest):
    deleted = token_storage.delete_tokens(request.user_id)

    if not deleted:
        raise HTTPException(404, "No active session found")

    return {"message": "Logged out successfully"}
```

**Note**: This implementation only removes tokens from our storage. For complete logout, you should also:
1. Call Microsoft's token revocation endpoint
2. Clear any session cookies
3. Redirect to Microsoft's logout URL to clear SSO session

---

#### Endpoint: `GET /auth/status/{user_id}`

**Purpose**: Check if a user is authenticated and if their token is valid.

```python
@router.get("/auth/status/{user_id}")
async def auth_status(user_id: str):
    tokens = token_storage.get_tokens(user_id)

    if not tokens:
        return {"authenticated": False, "user_id": user_id}

    is_expired = token_storage.is_token_expired(user_id)

    return {
        "authenticated": True,
        "user_id": user_id,
        "token_expired": is_expired,
        "has_refresh_token": bool(tokens.get("refresh_token"))
    }
```

**Use Case**: Check authentication status before making API calls. If `token_expired` is true, call `/auth/refresh` first.

---

## Security Features

### 1. PKCE (Proof Key for Code Exchange)

**Problem Solved**: Authorization code interception attacks

**How It Works**:
```
Client generates: verifier (secret)
                      ↓
                   SHA256
                      ↓
Client sends: challenge (public)
                      ↓
Microsoft stores challenge
                      ↓
Client later sends: verifier
                      ↓
Microsoft verifies: SHA256(verifier) == stored challenge
```

**Benefits**:
- Prevents authorization code interception attacks
- No client secret needed for public clients
- Recommended for all OAuth clients by RFC 7636

### 2. State Parameter (CSRF Protection)

**Problem Solved**: Cross-Site Request Forgery attacks

**Implementation**:
- Generate cryptographically random state: `secrets.token_urlsafe(32)`
- Include in authorization URL
- Verify state matches when callback is received
- State is single-use (verifier is deleted after retrieval)

### 3. Token Encryption at Rest

**Problem Solved**: Token exposure if storage is compromised

**Implementation**:
- Fernet symmetric encryption (AES-128-CBC + HMAC)
- Key derived from `SECRET_KEY` environment variable
- Tokens stored as encrypted bytes
- Decryption only happens when tokens are needed

**Encryption Example**:
```python
Plaintext: {"access_token": "eyJ0eXAi..."}
              ↓
           JSON
              ↓
    Fernet.encrypt()
              ↓
Ciphertext: b'gAAAAABh...' (stored)
```

### 4. Secure Token Transmission

- All OAuth endpoints use HTTPS in production
- Tokens never logged or exposed in error messages
- Authorization header format: `Bearer {access_token}`

### 5. Scope Limitation

Only request necessary permissions:
```python
scopes = [
    "User.Read",           # Minimal: Read user profile
    "Mail.ReadWrite",      # Only what's needed for email operations
    "Mail.Send",           # Specific permission to send
    "Calendars.ReadWrite", # Only what's needed for calendar
    "MailboxSettings.Read" # Read-only for settings
]
```

**Best Practice**: Use least-privilege principle - only request scopes you actually use.

---

## Token Lifecycle

### Complete Token Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Token Lifecycle                         │
└─────────────────────────────────────────────────────────────┘

1. LOGIN
   User → /auth/login → Microsoft → /auth/callback
   Result: Access Token (expires in 1 hour)
           Refresh Token (expires in 90 days)

2. USING TOKENS
   Application → Microsoft Graph API
   Header: Authorization: Bearer {access_token}

3. TOKEN EXPIRATION (after ~1 hour)
   Check: is_token_expired() → True
   Action: Call /auth/refresh

4. REFRESH
   Application → /auth/refresh
   Uses: refresh_token
   Result: New access_token, possibly new refresh_token

5. REFRESH TOKEN EXPIRATION (after ~90 days)
   /auth/refresh → Error: "refresh_token_expired"
   Action: User must re-authenticate via /auth/login

6. LOGOUT
   Application → /auth/logout
   Result: All tokens deleted from storage
```

### Token Refresh Strategy

**Proactive Refresh** (Recommended):
```python
def get_access_token(user_id: str) -> str:
    """Get valid access token, refreshing if needed."""
    if token_storage.is_token_expired(user_id):
        # Refresh before token expires
        refresh_token(user_id)

    tokens = token_storage.get_tokens(user_id)
    return tokens["access_token"]
```

**Reactive Refresh** (Alternative):
```python
try:
    response = call_graph_api(access_token)
except UnauthorizedError:
    # Token expired, refresh and retry
    refresh_token(user_id)
    response = call_graph_api(new_access_token)
```

---

## Error Handling

### Common Errors and Solutions

#### 1. Invalid State Parameter
```
Error: "Invalid state parameter or code verifier expired"
Cause: State parameter doesn't match or verifier was already used
Solution: Restart the login flow from /auth/login
```

#### 2. Authorization Code Expired
```
Error: "Authentication failed: invalid_grant - Authorization code expired"
Cause: Too much time passed between authorization and callback
Solution: Authorization codes expire after ~10 minutes, restart login
```

#### 3. Refresh Token Expired
```
Error: "Token refresh failed: invalid_grant - Refresh token expired"
Cause: Refresh token lifetime exceeded (default 90 days)
Solution: User must re-authenticate via /auth/login
```

#### 4. Insufficient Permissions
```
Error: "Access denied - User has not granted permission"
Cause: User declined consent or admin approval required
Solution: Review required scopes, may need admin consent
```

#### 5. Token Storage Decryption Failed
```
Error: Tokens return None after storage
Cause: SECRET_KEY changed, corrupting encrypted tokens
Solution: Users must re-authenticate (tokens cannot be recovered)
```

---

## Testing the Implementation

### Unit Tests

We have comprehensive test coverage (34 tests):

**PKCE Tests** (`tests/test_pkce.py`):
- Code verifier generation and uniqueness
- Code challenge generation and verification
- Length validation

**Token Storage Tests** (`tests/test_token_storage.py`):
- Token encryption/decryption
- Code verifier storage and retrieval
- Token expiration checking
- CRUD operations

**OAuth Route Tests** (`tests/test_auth_routes.py`):
- Login redirect with PKCE
- Callback handling (success and error cases)
- Token refresh (success and error cases)
- Logout
- Authentication status

### Manual Testing

```bash
# 1. Start the server
uv run python main.py

# 2. Open browser and navigate to
http://localhost:8000/auth/login

# 3. Complete Microsoft authentication

# 4. Check authentication status (use user_id from callback)
curl http://localhost:8000/auth/status/{user_id}

# 5. Refresh token
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your_user_id"}'

# 6. Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your_user_id"}'
```

---

## Production Considerations

### 1. Token Storage

**Current**: In-memory storage (data lost on restart)

**Production Options**:
- **PostgreSQL**: Relational database with encryption
- **Redis**: Fast key-value store with expiration
- **Azure Key Vault**: Managed secret storage
- **Cosmos DB**: Azure-native NoSQL database

**Implementation Example** (Redis):
```python
import redis
import json

class RedisTokenStorage:
    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

    def store_tokens(self, user_id: str, tokens: dict):
        # Set with expiration (90 days)
        encrypted = self.cipher.encrypt(json.dumps(tokens).encode())
        self.redis.setex(
            f"tokens:{user_id}",
            7776000,  # 90 days
            encrypted
        )
```

### 2. HTTPS Configuration

**Required for production**:
```python
# Update .env
REDIRECT_URI=https://your-domain.com/auth/callback

# Configure Uvicorn with SSL
uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=443,
    ssl_keyfile="/path/to/key.pem",
    ssl_certfile="/path/to/cert.pem"
)
```

### 3. Secret Management

**Never commit secrets to git**:
```bash
# Use environment variables
export CLIENT_SECRET="..."
export SECRET_KEY="..."

# Or use secret management services
# - Azure Key Vault
# - AWS Secrets Manager
# - HashiCorp Vault
```

### 4. Logging and Monitoring

```python
import logging

logger = logging.getLogger(__name__)

@router.get("/auth/callback")
async def callback(code: str, state: str):
    logger.info(f"OAuth callback received for state: {state}")

    try:
        result = acquire_token(code, state)
        logger.info(f"User authenticated: {result['user_id']}")
    except Exception as e:
        logger.error(f"OAuth error: {e}", exc_info=True)
        raise
```

**What to Log**:
- ✅ Authentication attempts (success/failure)
- ✅ Token refresh events
- ✅ Logout events
- ❌ Never log tokens or secrets

### 5. Rate Limiting

Protect OAuth endpoints from abuse:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login():
    ...
```

### 6. Session Timeout

Implement automatic session expiration:
```python
SESSION_TIMEOUT = timedelta(hours=24)

def is_session_valid(user_id: str) -> bool:
    tokens = token_storage.get_tokens(user_id)
    if not tokens:
        return False

    stored_at = datetime.fromisoformat(tokens["stored_at"])
    return datetime.utcnow() - stored_at < SESSION_TIMEOUT
```

---

## References

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)

---

## Summary

This OAuth implementation provides:

✅ **Security**: PKCE, state parameter, token encryption
✅ **Completeness**: Full OAuth flow with refresh and logout
✅ **Testing**: 34 comprehensive unit tests
✅ **Documentation**: Detailed code comments and guides
✅ **Production-Ready**: With recommended upgrades for scale

The implementation follows OAuth 2.0 best practices and is ready for integration with Microsoft Graph API operations in the next phase of development.
