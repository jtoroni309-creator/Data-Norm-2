"""Configuration for Audit Planning service"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/aura_audit"
    )

    # Service configuration
    SERVICE_NAME: str = "audit-planning"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS
    CORS_ORIGINS: list = ["*"]  # Configure for production

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
