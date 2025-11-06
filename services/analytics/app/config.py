"""Configuration settings for Analytics Service"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Service configuration"""

    # Service info
    SERVICE_NAME: str = "analytics"
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

    # Analytics Thresholds
    ROUND_DOLLAR_THRESHOLD: float = 0.001  # 0.1% tolerance
    OUTLIER_Z_SCORE_THRESHOLD: float = 3.0  # Standard deviations
    ISOLATION_FOREST_CONTAMINATION: float = 0.1  # Expected anomaly rate

    # ML Model
    ML_MODEL_PATH: str = "/models/isolation_forest.pkl"
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
