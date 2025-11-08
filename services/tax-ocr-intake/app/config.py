"""
Configuration for Tax OCR Intake Service
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Service settings with environment variable support"""

    # Service
    SERVICE_NAME: str = "tax-ocr-intake"
    SERVICE_PORT: int = 8025
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # LLM Service
    LLM_SERVICE_URL: str = "http://api-llm:8000"

    # Storage (MinIO/S3)
    STORAGE_ENDPOINT: str = "minio:9000"
    STORAGE_ACCESS_KEY: str
    STORAGE_SECRET_KEY: str
    STORAGE_BUCKET: str = "tax-documents"
    STORAGE_SECURE: bool = False

    # Feature Flags
    FEATURE_TAX_OCR_V1: bool = True
    FEATURE_AI_CLASSIFICATION: bool = True
    FEATURE_AUTO_ACCEPT_THRESHOLD: float = 0.98
    FEATURE_REVIEW_QUEUE_THRESHOLD: float = 0.80

    # OCR Settings
    OCR_MODEL: str = "gpt-4-vision-preview"
    OCR_MAX_PAGES_PER_BATCH: int = 50
    OCR_TIMEOUT_SECONDS: int = 300

    # Document Processing
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: list[str] = ["application/pdf", "image/jpeg", "image/png", "image/tiff"]

    # Security
    JWT_SECRET: str
    ENCRYPTION_KEY: str  # Fernet key for SSN/EIN encryption

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
