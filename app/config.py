"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

    # Azure AD Configuration
    client_id: str = ""
    tenant_id: str = ""
    redirect_uri: str = "http://localhost:8000/auth/callback"
    client_secret: str = ""

    # OAuth Scopes
    scopes: list[str] = [
        "User.Read",
        "Mail.ReadWrite",
        "Mail.Send",
        "Calendars.ReadWrite",
        "MailboxSettings.Read"
    ]

    # Security
    secret_key: str = "your-secret-key-change-in-production"


settings = Settings()
