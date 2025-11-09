"""
Configuration management for Fraud Detection service.
"""

import os
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation"""

    # Application
    APP_NAME: str = "Fraud Detection Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    # Database - Required in production
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/aura_fraud_detection",
        description="PostgreSQL database connection string"
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Validate DATABASE_URL is set in production"""
        env = info.data.get("ENVIRONMENT", "development")
        if env == "production" and "localhost" in v:
            raise ValueError("DATABASE_URL must not use localhost in production")
        return v

    # Redis (for caching and real-time processing)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/3")

    # Plaid API (Bank integration)
    PLAID_CLIENT_ID: str = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET: str = os.getenv("PLAID_SECRET", "")
    PLAID_ENVIRONMENT: str = os.getenv("PLAID_ENVIRONMENT", "sandbox")  # sandbox, development, production
    PLAID_WEBHOOK_URL: Optional[str] = os.getenv("PLAID_WEBHOOK_URL")

    # Encryption (for sensitive data)
    ENCRYPTION_KEY: str = os.getenv(
        "ENCRYPTION_KEY",
        "your-32-byte-encryption-key-here-change-in-production"
    )

    # Azure Key Vault (for production secrets)
    AZURE_KEY_VAULT_URL: Optional[str] = os.getenv("AZURE_KEY_VAULT_URL")

    # ML Model Storage
    MODEL_STORAGE_TYPE: str = os.getenv("MODEL_STORAGE_TYPE", "azure")  # azure or s3
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER: str = os.getenv("AZURE_STORAGE_CONTAINER", "ml-models")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET", "aura-ml-models")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")

    # Fraud Detection Configuration
    DEFAULT_FRAUD_THRESHOLD: float = float(os.getenv("DEFAULT_FRAUD_THRESHOLD", "0.75"))
    HIGH_RISK_THRESHOLD: float = float(os.getenv("HIGH_RISK_THRESHOLD", "0.90"))
    AUTO_CASE_CREATION_THRESHOLD: float = float(os.getenv("AUTO_CASE_CREATION_THRESHOLD", "0.85"))

    # Transaction monitoring
    MAX_DAILY_TRANSACTIONS_LIMIT: int = int(os.getenv("MAX_DAILY_TRANSACTIONS_LIMIT", "1000"))
    LARGE_TRANSACTION_AMOUNT: float = float(os.getenv("LARGE_TRANSACTION_AMOUNT", "10000.00"))

    # Velocity checks (number of transactions in time window)
    VELOCITY_CHECK_WINDOW_MINUTES: int = int(os.getenv("VELOCITY_CHECK_WINDOW_MINUTES", "60"))
    MAX_TRANSACTIONS_PER_HOUR: int = int(os.getenv("MAX_TRANSACTIONS_PER_HOUR", "10"))

    # Geographic anomaly detection
    MAX_GEOGRAPHIC_DISTANCE_MILES: float = float(os.getenv("MAX_GEOGRAPHIC_DISTANCE_MILES", "500"))
    SUSPICIOUS_COUNTRY_CODES: list = ["XX", "YY"]  # Configure based on risk profile

    # Notifications
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    ALERT_EMAIL_FROM: str = os.getenv("ALERT_EMAIL_FROM", "alerts@auraaudit.ai")
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_PHONE: Optional[str] = os.getenv("TWILIO_FROM_PHONE")

    # Background jobs
    TRANSACTION_SYNC_INTERVAL_MINUTES: int = int(os.getenv("TRANSACTION_SYNC_INTERVAL_MINUTES", "15"))
    MODEL_RETRAINING_INTERVAL_DAYS: int = int(os.getenv("MODEL_RETRAINING_INTERVAL_DAYS", "7"))

    # API Keys
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS Configuration
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    ).split(",")

    # Feature flags
    ENABLE_ML_MODELS: bool = os.getenv("ENABLE_ML_MODELS", "true").lower() == "true"
    ENABLE_REAL_TIME_MONITORING: bool = os.getenv("ENABLE_REAL_TIME_MONITORING", "true").lower() == "true"
    ENABLE_ANOMALY_DETECTION: bool = os.getenv("ENABLE_ANOMALY_DETECTION", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
