"""Configuration settings for Identity Service"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT Configuration
    JWT_SECRET: str = "dev-secret-change-in-production-to-256-bit-random-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 8

    # OIDC Configuration (Optional)
    OIDC_ENABLED: bool = False
    OIDC_ISSUER: str = "https://login.microsoftonline.com/<tenant-id>/v2.0"
    OIDC_CLIENT_ID: str = ""
    OIDC_CLIENT_SECRET: str = ""
    OIDC_AUDIENCE: str = "api://atlas"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Security
    BCRYPT_ROUNDS: int = 12


settings = Settings()
