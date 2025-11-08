"""Configuration settings for Accounting Integrations Service"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"
    )

    # QuickBooks Online
    QBO_CLIENT_ID: str = os.getenv("QBO_CLIENT_ID", "")
    QBO_CLIENT_SECRET: str = os.getenv("QBO_CLIENT_SECRET", "")
    QBO_REDIRECT_URI: str = os.getenv("QBO_REDIRECT_URI", "http://localhost:8000/quickbooks/callback")
    QBO_ENVIRONMENT: str = os.getenv("QBO_ENVIRONMENT", "sandbox")  # sandbox or production

    # Xero
    XERO_CLIENT_ID: str = os.getenv("XERO_CLIENT_ID", "")
    XERO_CLIENT_SECRET: str = os.getenv("XERO_CLIENT_SECRET", "")
    XERO_REDIRECT_URI: str = os.getenv("XERO_REDIRECT_URI", "http://localhost:8000/xero/callback")

    # NetSuite
    NETSUITE_ACCOUNT_ID: str = os.getenv("NETSUITE_ACCOUNT_ID", "")
    NETSUITE_CONSUMER_KEY: str = os.getenv("NETSUITE_CONSUMER_KEY", "")
    NETSUITE_CONSUMER_SECRET: str = os.getenv("NETSUITE_CONSUMER_SECRET", "")
    NETSUITE_TOKEN_ID: str = os.getenv("NETSUITE_TOKEN_ID", "")
    NETSUITE_TOKEN_SECRET: str = os.getenv("NETSUITE_TOKEN_SECRET", "")

    # Sage Intacct
    SAGE_COMPANY_ID: str = os.getenv("SAGE_COMPANY_ID", "")
    SAGE_USER_ID: str = os.getenv("SAGE_USER_ID", "")
    SAGE_USER_PASSWORD: str = os.getenv("SAGE_USER_PASSWORD", "")
    SAGE_SENDER_ID: str = os.getenv("SAGE_SENDER_ID", "")
    SAGE_SENDER_PASSWORD: str = os.getenv("SAGE_SENDER_PASSWORD", "")

    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # 32-byte key for token encryption

    # General
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
