"""
Application Configuration
Supports Keycloak/OIDC integration for future authentication
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    app_name: str = "CrewAI Studio API"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_prefix: str = "/api"
    api_docs_url: str = "/docs"
    api_redoc_url: str = "/redoc"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Database
    database_url: str = os.getenv("DB_URL", "sqlite:///crewai.db")

    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8501",  # Streamlit default
        "http://localhost:8000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

    # Security - JWT (Fallback, will be replaced by Keycloak)
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Keycloak/OIDC (for future integration)
    keycloak_enabled: bool = os.getenv("KEYCLOAK_ENABLED", "false").lower() == "true"
    keycloak_server_url: Optional[str] = os.getenv("KEYCLOAK_SERVER_URL")
    keycloak_realm: Optional[str] = os.getenv("KEYCLOAK_REALM")
    keycloak_client_id: Optional[str] = os.getenv("KEYCLOAK_CLIENT_ID")
    keycloak_client_secret: Optional[str] = os.getenv("KEYCLOAK_CLIENT_SECRET")

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    # File Upload
    upload_dir: str = "knowledge"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
