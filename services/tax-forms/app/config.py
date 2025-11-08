"""Configuration for Tax Forms Service"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "tax-forms"
    SERVICE_PORT: int = 8027
    ENVIRONMENT: str = "development"

    DATABASE_URL: str
    REDIS_URL: str

    # Feature Flags
    FEATURE_TAX_FORMS_V1: bool = True
    FEATURE_FORM_1040: bool = True
    FEATURE_EFILE_GENERATION: bool = True

    # Storage
    STORAGE_ENDPOINT: str = "minio:9000"
    STORAGE_ACCESS_KEY: str
    STORAGE_SECRET_KEY: str
    STORAGE_BUCKET: str = "tax-forms"
    STORAGE_SECURE: bool = False

    JWT_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
