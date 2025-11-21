"""
SOC Copilot Configuration
Environment-based settings using Pydantic
"""
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, field_validator


class Settings(BaseSettings):
    """Application settings with validation"""

    # Application
    APP_NAME: str = "SOC Copilot"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Firm Branding
    FIRM_NAME: str = "Fred J. Toroni & Company Certified Public Accountants"
    FIRM_LICENSE: Optional[str] = None

    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=2, env="WORKERS")

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/soc_copilot",
        env="DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Security
    JWT_SECRET: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # SSO/OIDC
    OIDC_ENABLED: bool = Field(default=False, env="OIDC_ENABLED")
    OIDC_PROVIDER: Optional[str] = Field(default=None, env="OIDC_PROVIDER")
    OIDC_CLIENT_ID: Optional[str] = Field(default=None, env="OIDC_CLIENT_ID")
    OIDC_CLIENT_SECRET: Optional[str] = Field(default=None, env="OIDC_CLIENT_SECRET")
    OIDC_DISCOVERY_URL: Optional[str] = Field(default=None, env="OIDC_DISCOVERY_URL")

    # MFA
    MFA_REQUIRED_FOR_ROLES: List[str] = Field(
        default=["CPA_PARTNER", "AUDIT_MANAGER"],
        env="MFA_REQUIRED_FOR_ROLES"
    )

    # AI/LLM
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = 0.3
    ENABLE_AI_PLANNING: bool = Field(default=True, env="ENABLE_AI_PLANNING")
    ENABLE_AI_EVIDENCE_ANALYSIS: bool = Field(default=True, env="ENABLE_AI_EVIDENCE_ANALYSIS")
    ENABLE_AI_REPORT_GENERATION: bool = Field(default=True, env="ENABLE_AI_REPORT_GENERATION")

    # RAG / Vector Store
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(default="us-west1-gcp", env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = Field(default="soc-copilot-standards", env="PINECONE_INDEX_NAME")

    # Storage (S3/Azure Blob)
    STORAGE_PROVIDER: str = Field(default="local", env="STORAGE_PROVIDER")  # local, s3, azure
    S3_BUCKET_NAME: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    S3_REGION: Optional[str] = Field(default="us-east-1", env="S3_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = Field(default=None, env="AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME: Optional[str] = Field(default="soc-evidence", env="AZURE_CONTAINER_NAME")

    # Evidence Collection
    MAX_EVIDENCE_FILE_SIZE_MB: int = 100
    ALLOWED_EVIDENCE_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "text/plain",
        "text/csv",
        "application/json",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]

    # Integration Connectors
    OKTA_DOMAIN: Optional[str] = Field(default=None, env="OKTA_DOMAIN")
    OKTA_API_TOKEN: Optional[str] = Field(default=None, env="OKTA_API_TOKEN")
    SPLUNK_HOST: Optional[str] = Field(default=None, env="SPLUNK_HOST")
    SPLUNK_TOKEN: Optional[str] = Field(default=None, env="SPLUNK_TOKEN")
    JIRA_URL: Optional[str] = Field(default=None, env="JIRA_URL")
    JIRA_EMAIL: Optional[str] = Field(default=None, env="JIRA_EMAIL")
    JIRA_API_TOKEN: Optional[str] = Field(default=None, env="JIRA_API_TOKEN")

    # Reporting
    REPORT_WATERMARK_ENABLED: bool = True
    REPORT_RESTRICTED_DISTRIBUTION_DEFAULT: bool = True

    # Compliance
    DATA_RETENTION_YEARS: int = 7  # SOC standard
    ENABLE_AUDIT_TRAIL: bool = True
    ENABLE_RLS: bool = True

    # Performance
    EVIDENCE_INDEXING_BATCH_SIZE: int = 1000
    MAX_CONCURRENT_EVIDENCE_INGESTION: int = 10

    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
