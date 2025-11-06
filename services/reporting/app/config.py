"""Configuration settings for Reporting Service"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Service configuration"""

    # Service info
    SERVICE_NAME: str = "reporting"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_TTL: int = 3600

    # Storage (S3/MinIO/Azure Blob)
    STORAGE_BACKEND: str = "s3"  # s3, minio, or azure
    S3_ENDPOINT: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minio"
    S3_SECRET_KEY: str = "minio123"
    S3_BUCKET: str = "reports"
    S3_WORM_BUCKET: str = "atlas-worm"  # Immutable storage for final reports
    S3_REGION: str = "us-east-1"

    # Azure Storage (if using Azure)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: str = "reports"
    AZURE_WORM_CONTAINER: str = "atlas-worm"

    # DocuSign E-signature
    DOCUSIGN_INTEGRATION_KEY: str = ""
    DOCUSIGN_USER_ID: str = ""
    DOCUSIGN_ACCOUNT_ID: str = ""
    DOCUSIGN_BASE_PATH: str = "https://demo.docusign.net/restapi"
    DOCUSIGN_OAUTH_BASE_PATH: str = "account-d.docusign.com"
    DOCUSIGN_PRIVATE_KEY_PATH: str = "/secrets/docusign-private-key.pem"

    # PDF Generation
    PDF_DPI: int = 300
    PDF_PAGE_SIZE: str = "LETTER"
    PDF_COMPRESSION: bool = True
    PDF_EMBED_FONTS: bool = True

    # Report Configuration
    REPORT_RETENTION_DAYS: int = 2555  # 7 years for audit compliance
    REPORT_MAX_SIZE_MB: int = 100
    WATERMARK_TEXT: str = "CONFIDENTIAL"
    WATERMARK_ENABLED: bool = True

    # Templates
    TEMPLATE_DIR: str = "/app/templates"
    ALLOW_CUSTOM_TEMPLATES: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
