"""
Configuration for Regulation A/B Audit Service
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Regulation A/B Audit Service"
    APP_VERSION: str = "1.0.0"
    PORT: int = int(os.getenv("PORT", "8011"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/aura_audit"
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))

    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL_VERSION: str = os.getenv("AI_MODEL_VERSION", "gpt-4-turbo")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.2"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "4000"))

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    # Storage (S3/MinIO)
    STORAGE_ENDPOINT: str = os.getenv("STORAGE_ENDPOINT", "http://localhost:9000")
    STORAGE_ACCESS_KEY: str = os.getenv("STORAGE_ACCESS_KEY", "minioadmin")
    STORAGE_SECRET_KEY: str = os.getenv("STORAGE_SECRET_KEY", "minioadmin")
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "reg-ab-audit")
    STORAGE_REGION: str = os.getenv("STORAGE_REGION", "us-east-1")

    # Redis (for caching and background tasks)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Feature Flags
    ENABLE_AI_COMPLIANCE: bool = os.getenv("ENABLE_AI_COMPLIANCE", "true").lower() == "true"
    ENABLE_AUTO_WORKPAPERS: bool = os.getenv("ENABLE_AUTO_WORKPAPERS", "true").lower() == "true"
    ENABLE_AUTO_REPORTS: bool = os.getenv("ENABLE_AUTO_REPORTS", "true").lower() == "true"

    # Compliance Rules
    COMPLIANCE_RULES_CACHE_TTL: int = int(os.getenv("COMPLIANCE_RULES_CACHE_TTL", "3600"))
    MIN_CONFIDENCE_THRESHOLD: float = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.7"))

    # Notifications
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@auraaudit.ai")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
