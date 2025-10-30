
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pepper is a voice-controlled AI agent for Microsoft Outlook operations (email and calendar management). It integrates FastAPI backend with Microsoft Graph API, using Claude's tool calling capabilities for natural language interactions.

The project is in early development stages. See TODO.md for the complete implementation roadmap across 6 stages:
1. Backend API with Microsoft Graph integration
2. LLM agent with tool calling
3. Desktop voice interface prototype
4. Mobile app foundation (iOS/Android)
5. Mobile voice integration
6. Production hardening

## Development Setup

### Package Management
This project uses **uv** (not pip or poetry) for all dependency management:

```bash
# Install dependencies
uv sync

# Add new dependencies
uv add <package-name>

# Run Python scripts
uv run python main.py
uv run pytest
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `CLIENT_ID`: Azure AD application client ID
- `TENANT_ID`: Azure AD tenant ID
- `REDIRECT_URI`: OAuth callback URL (default: http://localhost:8000/auth/callback)
- `CLIENT_SECRET`: (Optional) For confidential client flows

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_<module>.py

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

### Development Server
```bash
# Start FastAPI server (when implemented)
uv run uvicorn main:app --reload
```

## Architecture & Key Concepts

### Authentication Flow
The project implements OAuth 2.0 with PKCE (Proof Key for Code Exchange) for secure authentication with Microsoft:
1. User initiates login → redirects to Microsoft login page
2. User authorizes → Microsoft redirects back with authorization code
3. Backend exchanges code for access/refresh tokens using PKCE
4. Tokens are stored securely (encrypted database or session)
5. Access tokens are refreshed automatically when expired

### Microsoft Graph API Integration
The backend wraps Microsoft Graph API endpoints for:

**Email Operations:**
- `writeEmail()`: Create draft emails
- `sendEmail()`: Send emails (requires confirmation)
- `searchEmails()`: Query emails by folder, date, or keywords
- `readEmail()`: Retrieve full email content

**Calendar Operations:**
- `checkSchedulingAssistant()`: Find available meeting times
- `scheduleMeeting()`: Create calendar events (requires confirmation)

All operations use the authenticated Microsoft Graph client with error handling, retries (exponential backoff), and request/response logging.

### LLM Agent Tool Calling
The agent uses Claude's structured tool calling to translate natural language requests into API operations:

1. **Tool Registry**: Whitelist of allowed tools with JSON schemas
2. **Tool Validator**: Validates tool names and parameters, sanitizes inputs (XSS prevention, email format validation)
3. **Tool Executor**: Maps tool calls to GraphClient API wrappers
4. **Confirmation System**: Destructive actions (send_email, schedule_meeting) require explicit user approval before execution
5. **Conversation Management**: Maintains message history for multi-turn interactions

### Security Considerations
- Never bypass the tool whitelist or confirmation system
- All user inputs to tools must be sanitized (especially email content)
- Access tokens should never be logged or exposed in responses
- OAuth redirect URIs must match exactly what's registered in Azure AD
- Test all destructive operations in a safe test environment first

## Project Structure

Currently minimal structure with:
- `main.py`: Entry point (placeholder)
- `pyproject.toml`: uv/Python project configuration
- `.env.example`: Template for required environment variables
- `TODO.md`: Comprehensive multi-stage implementation plan

As development progresses, expect these directories:
- `src/`: Main application code
  - `auth/`: OAuth controllers and token management
  - `graph/`: Microsoft Graph API wrappers
  - `agent/`: LLM agent controller and tool execution
  - `api/`: FastAPI routes and endpoints
- `tests/`: Unit and integration tests mirroring src/ structure

## Testing Strategy

**Unit Tests** (mock Graph API):
- Test each API wrapper independently
- Validate tool schemas and parameter validation
- Test error handling for expired tokens, rate limits, invalid inputs

**Integration Tests** (real Microsoft account):
- End-to-end OAuth flow testing
- Token refresh mechanisms
- All email and calendar operations
- Confirmation flow for destructive actions

**Agent Tests**:
- Multi-turn conversation handling
- Tool call validation and execution
- Security: attempt to bypass whitelist or confirmations

Create a Postman/Thunder Client collection for manual API testing during development.

## Dependencies

Key packages:
- **FastAPI/Uvicorn**: Web framework and ASGI server
- **msgraph-core**: Microsoft Graph API SDK
- **azure-identity**: Azure AD authentication
- **msal**: Microsoft Authentication Library (OAuth/token management)
- **httpx**: HTTP client for API requests
- **python-dotenv**: Environment variable management
- **pytest**: Testing framework

## Development Workflow

When implementing new features:
1. Consult TODO.md for implementation order and dependencies
2. Start with backend API wrappers before agent integration
3. Write unit tests alongside implementation (not after)
4. Test with real Microsoft test tenant before production
5. Always implement confirmation dialogs for destructive operations
6. Add detailed error handling and logging for debugging

## Microsoft Graph API Notes

- API calls require proper scopes in Azure AD app registration (Mail.ReadWrite, Calendars.ReadWrite, etc.)
- Rate limits apply - implement exponential backoff for retries
- Use batch requests where possible for efficiency
- Test timezone handling carefully for calendar operations
- Email search supports KQL (Keyword Query Language) syntax
