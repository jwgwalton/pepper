# OAuth 2.0 Setup Guide

This guide will help you set up OAuth 2.0 authentication with Microsoft Azure AD for the Pepper application.

## Prerequisites

1. A Microsoft Azure account
2. Access to Azure Active Directory

## Azure AD App Registration

### Step 1: Register Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Fill in the application details:
   - **Name**: Pepper Outlook Agent (or your preferred name)
   - **Supported account types**: Choose based on your needs
     - Single tenant (recommended for development)
     - Multitenant (for production with multiple organizations)
   - **Redirect URI**:
     - Platform: Web
     - URI: `http://localhost:8000/auth/callback`
4. Click **Register**

### Step 2: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add the following permissions:
   - `User.Read` - Read user profile
   - `Mail.ReadWrite` - Read and write mail
   - `Mail.Send` - Send mail as user
   - `Calendars.ReadWrite` - Read and write calendars
   - `MailboxSettings.Read` - Read mailbox settings
4. Click **Grant admin consent** (if you have admin rights)

### Step 3: Create Client Secret (Optional)

For confidential client flows:

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description and set expiration
4. **Copy the secret value immediately** (you won't be able to see it again)

### Step 4: Gather Required Information

From the **Overview** page of your app registration, copy:
- **Application (client) ID**
- **Directory (tenant) ID**

## Environment Configuration

Create a `.env` file in the project root:

```bash
# Microsoft Azure AD Configuration
CLIENT_ID=your_application_client_id_here
TENANT_ID=your_directory_tenant_id_here
REDIRECT_URI=http://localhost:8000/auth/callback

# Client Secret (optional, for confidential clients)
CLIENT_SECRET=your_client_secret_here

# Security - Generate a strong random key
SECRET_KEY=generate_a_strong_random_key_here
```

To generate a strong `SECRET_KEY`, you can use:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Testing the OAuth Flow

### Start the Server

```bash
uv run python main.py
```

The server will start at `http://localhost:8000`

### Test Endpoints

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Initiate Login**
   - Open in browser: `http://localhost:8000/auth/login`
   - You'll be redirected to Microsoft login
   - After authentication, you'll be redirected back with a user_id

3. **Check Auth Status**
   ```bash
   curl http://localhost:8000/auth/status/{user_id}
   ```

4. **Refresh Token**
   ```bash
   curl -X POST http://localhost:8000/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"user_id": "your_user_id"}'
   ```

5. **Logout**
   ```bash
   curl -X POST http://localhost:8000/auth/logout \
     -H "Content-Type: application/json" \
     -d '{"user_id": "your_user_id"}'
   ```

## API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Security Features

### PKCE (Proof Key for Code Exchange)
- Implemented for enhanced security in the OAuth flow
- Protects against authorization code interception attacks
- Uses SHA256 code challenge method

### Token Encryption
- Access and refresh tokens are encrypted at rest
- Uses Fernet symmetric encryption (based on AES)
- Encryption key derived from SECRET_KEY

### State Parameter
- CSRF protection using cryptographically random state parameter
- State is verified during callback

## Troubleshooting

### "Invalid state parameter" error
- This usually means the OAuth flow was interrupted or the code verifier expired
- Try the login flow again from the beginning

### "Missing required environment variables" in health check
- Ensure your `.env` file is in the project root
- Check that all required variables are set
- Restart the server after changing `.env`

### Token refresh fails
- Refresh tokens may expire after 90 days (configurable in Azure AD)
- User may need to re-authenticate

### Redirect URI mismatch
- Ensure the redirect URI in `.env` exactly matches the one in Azure AD
- Check for trailing slashes and http vs https

## Production Considerations

1. **Token Storage**: Replace in-memory storage with a database (PostgreSQL, Redis, etc.)
2. **HTTPS**: Use HTTPS in production (update REDIRECT_URI)
3. **Secret Management**: Use Azure Key Vault or similar for secrets
4. **Token Encryption**: Rotate SECRET_KEY periodically
5. **Logging**: Add audit logging for authentication events
6. **Rate Limiting**: Implement rate limiting on auth endpoints
7. **Session Management**: Consider adding session timeouts
