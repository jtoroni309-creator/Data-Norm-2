"""
Configuration management for Financial Analysis service.
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Financial Analysis Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/aura_financial_analysis"
    )

    # Redis (for caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/4")

    # SEC EDGAR API
    SEC_USER_AGENT: str = os.getenv("SEC_USER_AGENT", "Aura Audit AI support@auraaudit.ai")
    SEC_API_BASE_URL: str = "https://data.sec.gov"
    SEC_EDGAR_SEARCH_URL: str = "https://efts.sec.gov/LATEST/search-index"

    # Rate limiting for SEC
    SEC_REQUESTS_PER_SECOND: float = 0.1  # Max 10 requests per second per SEC guidelines

    # OpenAI API (for LLM analysis)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")

    # Azure OpenAI (alternative)
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    # Vector Database (for RAG)
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "financial-statements")

    # Qdrant (alternative vector DB)
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "financial_statements")

    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "azure")  # azure or s3
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER: str = os.getenv("AZURE_STORAGE_CONTAINER", "financial-data")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")

    # ML Model Storage
    MODEL_STORAGE_CONTAINER: str = os.getenv("MODEL_STORAGE_CONTAINER", "ml-models")

    # Analysis Configuration
    DEFAULT_MATERIALITY_PERCENTAGE: float = float(os.getenv("DEFAULT_MATERIALITY_PERCENTAGE", "0.05"))  # 5%
    PERFORMANCE_MATERIALITY_PERCENTAGE: float = float(os.getenv("PERFORMANCE_MATERIALITY_PERCENTAGE", "0.75"))  # 75% of materiality
    TRIVIAL_THRESHOLD_PERCENTAGE: float = float(os.getenv("TRIVIAL_THRESHOLD_PERCENTAGE", "0.05"))  # 5% of materiality

    # Risk Thresholds
    HIGH_RISK_DEBT_TO_EQUITY: float = float(os.getenv("HIGH_RISK_DEBT_TO_EQUITY", "2.0"))
    LOW_LIQUIDITY_CURRENT_RATIO: float = float(os.getenv("LOW_LIQUIDITY_CURRENT_RATIO", "1.0"))
    GOING_CONCERN_RISK_THRESHOLD: float = float(os.getenv("GOING_CONCERN_RISK_THRESHOLD", "0.75"))

    # Industry Benchmarking
    ENABLE_INDUSTRY_BENCHMARKING: bool = os.getenv("ENABLE_INDUSTRY_BENCHMARKING", "true").lower() == "true"
    PEER_COMPARISON_COUNT: int = int(os.getenv("PEER_COMPARISON_COUNT", "5"))

    # Training Configuration
    TRAINING_BATCH_SIZE: int = int(os.getenv("TRAINING_BATCH_SIZE", "32"))
    TRAINING_EPOCHS: int = int(os.getenv("TRAINING_EPOCHS", "10"))
    TRAINING_LEARNING_RATE: float = float(os.getenv("TRAINING_LEARNING_RATE", "0.001"))
    VALIDATION_SPLIT: float = float(os.getenv("VALIDATION_SPLIT", "0.2"))

    # Background Jobs
    EDGAR_SYNC_INTERVAL_HOURS: int = int(os.getenv("EDGAR_SYNC_INTERVAL_HOURS", "24"))
    MODEL_RETRAINING_INTERVAL_DAYS: int = int(os.getenv("MODEL_RETRAINING_INTERVAL_DAYS", "30"))

    # API Keys
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Feature Flags
    ENABLE_AI_ANALYSIS: bool = os.getenv("ENABLE_AI_ANALYSIS", "true").lower() == "true"
    ENABLE_AUTO_OPINION: bool = os.getenv("ENABLE_AUTO_OPINION", "true").lower() == "true"
    ENABLE_RAG: bool = os.getenv("ENABLE_RAG", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
