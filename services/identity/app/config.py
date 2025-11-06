"""Configuration settings for Identity Service"""
import os
import secrets
from typing import List
from pydantic import field_validator
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

    @field_validator('JWT_SECRET')
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """
        Validate JWT secret strength

        In production environments, the JWT secret MUST be:
        - At least 32 characters long
        - Not the default development secret
        - Cryptographically random
        """
        # Check if running in production (based on common environment indicators)
        is_production = os.getenv("ENVIRONMENT", "development").lower() in ["production", "prod"]

        # Default development secrets that are forbidden in production
        forbidden_secrets = [
            "dev-secret-change-in-production-to-256-bit-random-key",
            "dev-secret",
            "secret",
            "change-me",
        ]

        if is_production:
            # Strict validation for production
            if v in forbidden_secrets:
                raise ValueError(
                    "SECURITY ERROR: Using default JWT_SECRET in production! "
                    f"Generate a secure secret with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

            if len(v) < 32:
                raise ValueError(
                    f"SECURITY ERROR: JWT_SECRET too short ({len(v)} chars). "
                    "Must be at least 32 characters for production. "
                    f"Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

            # Warn if secret appears non-random (all same character, sequential, etc.)
            if len(set(v)) < 10:
                raise ValueError(
                    "SECURITY ERROR: JWT_SECRET appears non-random. "
                    f"Generate a cryptographically secure secret with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
        else:
            # Development mode - just warn
            if v in forbidden_secrets:
                print(f"⚠️  WARNING: Using default JWT_SECRET. This is OK for development but MUST be changed for production!")
                print(f"   Generate a secure secret with: python -c 'import secrets; print(secrets.token_urlsafe(32))'")

        return v

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
