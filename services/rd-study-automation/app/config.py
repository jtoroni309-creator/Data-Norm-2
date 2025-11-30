"""
Configuration settings for R&D Study Automation Service.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Service configuration from environment variables."""

    # Service metadata
    SERVICE_NAME: str = "rd-study-automation"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS - Allow all origins since requests come through nginx proxy
    CORS_ORIGINS: List[str] = ["*"]

    # Auth (JWT)
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 8

    # Row-Level Security
    RLS_ENABLED: bool = True

    # OpenAI / LLM Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_TEMPERATURE: float = 0.2  # Lower for consistency
    OPENAI_MAX_TOKENS: int = 4000

    # Azure OpenAI (alternative)
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = "gpt-4"  # Chat model deployment name
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"

    # S3/MinIO for document storage
    S3_ENDPOINT: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minio"
    S3_SECRET_KEY: str = "minio123"
    S3_BUCKET_DOCUMENTS: str = "rd-study-documents"
    S3_BUCKET_OUTPUTS: str = "rd-study-outputs"

    # OCR Service
    OCR_SERVICE_URL: str = "http://ocr-service:8000"
    ENABLE_OCR: bool = True

    # Feature Flags
    ENABLE_AI_QUALIFICATION: bool = True
    ENABLE_AI_NARRATIVES: bool = True
    ENABLE_AI_DATA_INGESTION: bool = True
    ENABLE_AI_INTERVIEW_BOT: bool = True
    ENABLE_BENCHMARKS: bool = True

    # R&D Credit Calculation Defaults
    DEFAULT_FEDERAL_RATE_REGULAR: float = 0.20  # 20%
    DEFAULT_FEDERAL_RATE_ASC: float = 0.14  # 14%
    DEFAULT_BASE_PERIOD_YEARS: int = 4
    MIN_BASE_AMOUNT_PERCENTAGE: float = 0.03  # 3% floor

    # Confidence Thresholds
    MIN_CONFIDENCE_AUTO_APPROVE: float = 0.85
    MIN_CONFIDENCE_INCLUDE: float = 0.60
    FLAG_CONFIDENCE_THRESHOLD: float = 0.70

    # Rules Engine
    RULES_VERSION: str = "2024.1"
    RULES_DIRECTORY: str = "/app/rules"

    # Output Generation
    PDF_TEMPLATE_DIR: str = "/app/templates/pdf"
    EXCEL_TEMPLATE_DIR: str = "/app/templates/excel"

    # Inter-service URLs
    IDENTITY_SERVICE_URL: str = "http://api-identity:8000"
    ENGAGEMENT_SERVICE_URL: str = "http://api-engagement:8000"
    LLM_SERVICE_URL: str = "http://api-llm:8000"
    DOCUMENT_SERVICE_URL: str = "http://api-document:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
