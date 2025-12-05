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

    @field_validator('DATABASE_URL')
    @classmethod
    def fix_asyncpg_ssl(cls, v: str) -> str:
        """
        Fix SSL mode for asyncpg driver
        PostgreSQL uses sslmode=require but asyncpg uses ssl=require
        """
        if 'sslmode=' in v:
            v = v.replace('sslmode=', 'ssl=')
        return v

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

    # Azure AD Configuration for Admin Portal
    AZURE_AD_ENABLED: bool = True
    AZURE_AD_TENANT_ID: str = "002fa7de-1afd-4945-86e1-79281af841ad"
    AZURE_AD_CLIENT_ID: str = "a5608ed5-c6f8-4db9-b50f-b62e2b24c966"
    AZURE_AD_CLIENT_SECRET: str = ""  # Set via environment variable
    AZURE_AD_AUTHORITY: str = "https://login.microsoftonline.com/002fa7de-1afd-4945-86e1-79281af841ad"
    AZURE_AD_REDIRECT_URI: str = "https://admin.auraai.toroniandcompany.com/auth/callback"
    AZURE_AD_SCOPES: List[str] = ["User.Read", "openid", "profile", "email"]

    # OIDC Configuration (Optional - for other providers)
    OIDC_ENABLED: bool = False
    OIDC_ISSUER: str = "https://login.microsoftonline.com/<tenant-id>/v2.0"
    OIDC_CLIENT_ID: str = ""
    OIDC_CLIENT_SECRET: str = ""
    OIDC_AUDIENCE: str = "api://atlas"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://cpa.auraai.toroniandcompany.com",
        "https://client.auraai.toroniandcompany.com",
        "https://portal.auraai.toroniandcompany.com",
        "https://admin.auraai.toroniandcompany.com",
        "https://auraai.toroniandcompany.com",
        "https://www.auraai.toroniandcompany.com"
    ]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Application URLs (for invitation links)
    APP_URL: str = "https://auraai.toroniandcompany.com"
    CPA_APP_URL: str = "https://cpa.auraai.toroniandcompany.com"
    ADMIN_APP_URL: str = "https://admin.auraai.toroniandcompany.com"
    RD_CLIENT_APP_URL: str = "https://rdclient.auraai.toroniandcompany.com"

    # Email Configuration
    EMAIL_PROVIDER: str = "smtp"
    EMAIL_FROM: str = "noreply@auraai.toroniandcompany.com"
    EMAIL_FROM_NAME: str = "Aura Audit AI"
    SMTP_HOST: str = "smtp.office365.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Security
    BCRYPT_ROUNDS: int = 12


settings = Settings()
