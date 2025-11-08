"""Configuration for Tax Computation Engine"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "tax-engine"
    SERVICE_PORT: int = 8026
    ENVIRONMENT: str = "development"

    DATABASE_URL: str
    REDIS_URL: str

    # Feature Flags
    FEATURE_TAX_ENGINE_V1: bool = True
    FEATURE_1040_CALCULATION: bool = True
    FEATURE_STATE_TAX: bool = False  # V2
    FEATURE_CORPORATE_TAX: bool = False  # V2

    # Calculation Settings
    TAX_YEAR_DEFAULT: int = 2024
    CALCULATION_PRECISION: int = 2  # Decimal places

    JWT_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
