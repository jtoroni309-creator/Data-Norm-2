"""Configuration settings for Normalize Service"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Service Info
    SERVICE_NAME: str = "normalize"
    VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"

    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://frontend:3000"
    ]

    # ML Model Settings
    ML_MODEL_PATH: str = "/app/models/account_mapper.pkl"
    ML_CONFIDENCE_THRESHOLD: float = 0.75  # Minimum confidence for auto-mapping
    SIMILARITY_THRESHOLD: float = 0.6  # String similarity threshold

    # Feature Engineering
    USE_TFIDF_VECTORIZER: bool = True
    NGRAM_RANGE_MIN: int = 1
    NGRAM_RANGE_MAX: int = 3
    MAX_FEATURES: int = 1000

    # Training Data
    MIN_TRAINING_SAMPLES: int = 10  # Minimum samples per account type

    # MLflow Integration
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"
    MLFLOW_EXPERIMENT_NAME: str = "account-mapping"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
