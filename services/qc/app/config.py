"""Configuration settings for QC Service"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # QC Settings
    AUTO_RUN_QC_ON_STATUS_CHANGE: bool = True
    ALLOW_PARTNER_WAIVERS: bool = True
    REQUIRE_WAIVER_JUSTIFICATION_MIN_LENGTH: int = 10


settings = Settings()
