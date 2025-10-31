# Pepper 🌶️

A voice-controlled AI agent for Microsoft Outlook, powered by Claude and Microsoft Graph API.

## Overview

Pepper is an intelligent assistant that lets you manage your email and calendar using natural language voice commands. Built with FastAPI, Microsoft Graph API, and Claude's advanced language understanding, Pepper makes Outlook operations as simple as having a conversation.

**Example interactions:**
- "Draft an email to john@example.com about tomorrow's meeting"
- "Find all emails from Sarah about the budget report"
- "Schedule a meeting with the team for Friday at 2 PM"
- "What's on my calendar for next week?"

## Features

### Current Features (Stage 1 - Backend API) ✅

- **OAuth 2.0 Authentication**: Secure authentication with Microsoft using PKCE flow
- **Email Operations**:
  - Create and send emails
  - Search emails by folder, date, sender, or keywords
  - Read full email content and attachments metadata
- **Calendar Operations**:
  - Check availability using scheduling assistant
  - Create and schedule meetings
  - Query calendar events
- **Secure Token Management**: Encrypted storage and automatic token refresh
- **Comprehensive Error Handling**: Exponential backoff retries and detailed logging

### Planned Features

- **🎙️ Voice Interface**: Natural language voice commands for hands-free operation
- **🤖 AI Agent**: Claude-powered natural language understanding
- **📱 Mobile Apps**: Native iOS and Android applications
- **🖥️ Desktop App**: Cross-platform desktop application
- **🔒 Enterprise Security**: SOC 2 compliance and advanced security features

See [ROADMAP.md](ROADMAP.md) for the complete development plan.

## Architecture

Pepper is built with a modular architecture:

```
┌─────────────────┐
│  Voice Input    │  (Stage 3+)
└────────┬────────┘
         │
┌────────▼────────┐
│   LLM Agent     │  (Stage 2)
│  (Claude API)   │
└────────┬────────┘
         │
┌────────▼────────┐
│  Backend API    │  (Stage 1) ✅
│   (FastAPI)     │
└────────┬────────┘
         │
┌────────▼────────┐
│ Microsoft Graph │
│      API        │
└─────────────────┘
```

### Key Technologies

- **Backend**: FastAPI, Python 3.11+
- **Authentication**: MSAL (Microsoft Authentication Library), OAuth 2.0 with PKCE
- **Microsoft Integration**: Microsoft Graph API, msgraph-core
- **AI**: Anthropic Claude (planned)
- **Package Management**: uv (ultrafast Python package manager)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Microsoft Azure AD application (see setup guide below)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jwgwalton/pepper.git
   cd pepper
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Azure AD credentials:
   ```env
   CLIENT_ID=your-azure-ad-client-id
   TENANT_ID=your-azure-ad-tenant-id
   REDIRECT_URI=http://localhost:8000/auth/callback
   ```

4. **Set up Azure AD application** (first time only)
   
   Follow the detailed guide in [docs/AZURE_AD_SETUP.md](docs/AZURE_AD_SETUP.md) to:
   - Create an Azure AD app registration
   - Configure API permissions (Mail.ReadWrite, Calendars.ReadWrite)
   - Set up redirect URIs
   - Generate client credentials

### Running the Application

**Start the development server:**
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

**Access the API documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_auth_routes.py
```

## Usage

### Authentication Flow

1. Navigate to `http://localhost:8000/auth/login`
2. You'll be redirected to Microsoft login page
3. After authorization, you'll be redirected back with an access token
4. The token is stored securely and refreshed automatically

### API Examples

**Send an email:**
```bash
curl -X POST "http://localhost:8000/graph/send-email" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Hello from Pepper",
    "body": "This is a test email sent via the Graph API"
  }'
```

**Search emails:**
```bash
curl -X GET "http://localhost:8000/graph/search-emails?query=budget&top=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Check availability:**
```bash
curl -X POST "http://localhost:8000/graph/scheduling-assistant" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "attendees": ["attendee@example.com"],
    "duration_minutes": 60,
    "start_date": "2024-01-15",
    "end_date": "2024-01-19"
  }'
```

See the [API documentation](http://localhost:8000/docs) for all available endpoints.

## Project Structure

```
pepper/
├── app/                    # Main application code
│   ├── config.py          # Configuration and environment variables
│   ├── graph_client.py    # Microsoft Graph API client wrapper
│   ├── graph_utils.py     # Graph API utility functions
│   ├── main.py            # FastAPI application entry point
│   ├── pkce.py            # PKCE flow implementation
│   ├── token_storage.py   # Token management and storage
│   └── routers/           # API route handlers
│       ├── auth.py        # Authentication endpoints
│       └── graph.py       # Graph API endpoints
├── docs/                   # Documentation
│   ├── AZURE_AD_SETUP.md  # Azure AD setup guide
│   └── OAUTH_SETUP.md     # OAuth configuration guide
├── tests/                  # Unit and integration tests
├── .env.example           # Environment variables template
├── CLAUDE.md              # AI assistant guidance
├── pyproject.toml         # Python project configuration
├── ROADMAP.md             # Development roadmap
└── TODO.md                # Detailed task list
```

## Development

### Package Management

This project uses **uv** for dependency management:

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv sync
```

### Code Style

We follow standard Python conventions:
- PEP 8 style guide
- Type hints for function signatures
- Docstrings for public APIs
- Comprehensive error handling

### Testing

- **Unit tests**: Mock external dependencies (Graph API, MSAL)
- **Integration tests**: Test with real Microsoft test tenant (coming soon)
- **Coverage target**: Maintain >80% code coverage

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

### Security Considerations

- **Token Storage**: Access tokens are stored securely with encryption
- **OAuth 2.0 with PKCE**: Prevents authorization code interception attacks
- **Input Validation**: All user inputs are validated and sanitized
- **HTTPS Only**: All external communications use HTTPS
- **Minimal Permissions**: Request only necessary Microsoft Graph permissions

### Reporting Security Issues

Please report security vulnerabilities to [security contact - to be added]. Do not open public issues for security concerns.

## Documentation

- **[ROADMAP.md](ROADMAP.md)**: Complete development roadmap across 6 stages
- **[TODO.md](TODO.md)**: Detailed implementation checklist
- **[CLAUDE.md](CLAUDE.md)**: AI assistant development guidance
- **[docs/AZURE_AD_SETUP.md](docs/AZURE_AD_SETUP.md)**: Azure AD configuration guide
- **[docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md)**: OAuth setup instructions

## License

[To be determined]

## Acknowledgments

- Built with [FastAPI](https://fastapi.tianglo.com/)
- Powered by [Microsoft Graph API](https://developer.microsoft.com/en-us/graph)
- AI capabilities by [Anthropic Claude](https://www.anthropic.com/)
- Package management by [uv](https://github.com/astral-sh/uv)

## Support

For questions, issues, or feature requests:
- Open an issue on [GitHub Issues](https://github.com/jwgwalton/pepper/issues)
- Check existing documentation in the `docs/` directory

---

**Status**: 🚧 Active Development - Stage 1 (Backend API) mostly complete

See [ROADMAP.md](ROADMAP.md) for development progress and upcoming features.
