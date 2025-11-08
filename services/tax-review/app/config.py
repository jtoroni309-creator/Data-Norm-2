"""Configuration for Tax Review Service"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "tax-review"
    SERVICE_PORT: int = 8028
    ENVIRONMENT: str = "development"

    DATABASE_URL: str
    REDIS_URL: str

    # Feature Flags
    FEATURE_REVIEW_WORKBENCH_V1: bool = True
    FEATURE_VARIANCE_DETECTION: bool = True
    FEATURE_AI_ANOMALY_DETECTION: bool = True

    # Review Settings
    VARIANCE_THRESHOLD_PCT: float = 50.0  # Flag if >50% change vs prior year
    AUTO_APPROVE_THRESHOLD: float = 0.99  # Auto-approve if confidence >= 0.99

    # LLM Service
    LLM_SERVICE_URL: str = "http://api-llm:8000"

    JWT_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
