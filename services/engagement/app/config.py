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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
