"""Configuration settings for Engagement Service"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Service configuration"""

    # Service info
    SERVICE_NAME: str = "engagement"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # Auth (for future integration with Identity service)
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    # Row-Level Security
    RLS_ENABLED: bool = True

    # Auditor Firm Information (for confirmations and reports)
    AUDITOR_FIRM_NAME: str = "Aura Audit AI"
    AUDITOR_FIRM_ADDRESS_LINE1: str = "123 Main Street, Suite 100"
    AUDITOR_FIRM_ADDRESS_LINE2: str = ""
    AUDITOR_FIRM_CITY: str = "Anytown"
    AUDITOR_FIRM_STATE: str = "USA"
    AUDITOR_FIRM_POSTAL_CODE: str = "12345"

    # AI/LLM Configuration
    OPENAI_API_KEY: str = "your-openai-api-key-here"
    OPENAI_CHAT_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 2000

    # AI-Enhanced Materiality & Risk Settings
    DEFAULT_MATERIALITY_PERCENTAGE: float = 0.05  # 5% of net income
    PERFORMANCE_MATERIALITY_PERCENTAGE: float = 0.75  # 75% of materiality
    TRIVIAL_THRESHOLD_PERCENTAGE: float = 0.05  # 5% of materiality

    HIGH_RISK_DEBT_TO_EQUITY: float = 2.0
    LOW_LIQUIDITY_CURRENT_RATIO: float = 1.0
    GOING_CONCERN_RISK_THRESHOLD: float = 0.75

    # Feature Flags
    ENABLE_AI_MATERIALITY: bool = True
    ENABLE_AI_RISK_ASSESSMENT: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
