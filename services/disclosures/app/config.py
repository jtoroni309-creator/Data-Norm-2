"""Configuration settings for Ingestion Service"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Database
    DATABASE_URL: str = "postgresql://atlas:atlas@db:5432/atlas"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # S3 / Object Storage
    S3_ENDPOINT: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minio"
    S3_SECRET_KEY: str = "minio123"
    S3_BUCKET: str = "atlas-binders"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # EDGAR API
    EDGAR_BASE_URL: str = "https://data.sec.gov"
    EDGAR_USER_AGENT: str = "Aura Audit AI contact@aura-audit.ai"

    # Security
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "atlas-ingestion"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://jaeger:4318"


settings = Settings()
