"""
Configuration for Audit ML Service
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class AuditMLSettings(BaseSettings):
    """Audit ML Service Configuration"""

    # Model Training
    TARGET_ACCURACY: float = 0.99
    MIN_TRAINING_SAMPLES: int = 100
    VALIDATION_SPLIT: float = 0.2
    TEST_SPLIT: float = 0.15

    # Data Quality
    MIN_DATA_QUALITY_SCORE: float = 0.9
    MIN_LABEL_AGREEMENT_SCORE: float = 0.8
    REQUIRE_LABEL_VALIDATION: bool = True

    # Feature Engineering
    MAX_FEATURES: int = 500
    FEATURE_SELECTION_METHOD: str = "importance"  # importance, pca, selectkbest
    FEATURE_IMPORTANCE_THRESHOLD: float = 0.01

    # Model Ensemble
    ENSEMBLE_WEIGHTS: dict = {
        'xgboost': 0.40,
        'lightgbm': 0.30,
        'random_forest': 0.20,
        'neural_network': 0.10
    }

    # XGBoost Parameters
    XGB_N_ESTIMATORS: int = 500
    XGB_MAX_DEPTH: int = 8
    XGB_LEARNING_RATE: float = 0.05
    XGB_SUBSAMPLE: float = 0.8
    XGB_COLSAMPLE_BYTREE: float = 0.8

    # LightGBM Parameters
    LGBM_N_ESTIMATORS: int = 500
    LGBM_MAX_DEPTH: int = 7
    LGBM_LEARNING_RATE: float = 0.05
    LGBM_NUM_LEAVES: int = 31

    # Random Forest Parameters
    RF_N_ESTIMATORS: int = 300
    RF_MAX_DEPTH: int = 12
    RF_MIN_SAMPLES_SPLIT: int = 10
    RF_MIN_SAMPLES_LEAF: int = 5

    # PCAOB Compliance Thresholds
    AS_1105_THRESHOLD: float = 0.95  # Audit Evidence
    AS_2110_THRESHOLD: float = 0.98  # Fraud Risk
    AS_2301_THRESHOLD: float = 0.96  # Risk Response
    AS_2401_THRESHOLD: float = 0.94  # Audit Planning
    AS_2415_THRESHOLD: float = 0.97  # Going Concern
    AS_2501_THRESHOLD: float = 0.95  # Estimates
    AS_2810_THRESHOLD: float = 0.96  # Related Party
    AS_3101_THRESHOLD: float = 0.99  # Opinion

    # Continuous Learning
    FEEDBACK_BATCH_SIZE: int = 50
    RETRAINING_FREQUENCY_DAYS: int = 7
    MIN_FEEDBACK_QUALITY_SCORE: float = 0.8

    # Active Learning
    ACTIVE_LEARNING_BATCH_SIZE: int = 100
    UNCERTAINTY_SAMPLING_WEIGHT: float = 0.5
    DIVERSITY_SAMPLING_WEIGHT: float = 0.3
    ERROR_SAMPLING_WEIGHT: float = 0.2

    # Model Storage
    MODEL_STORAGE_TYPE: str = "azure"  # azure, s3, local
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER: str = "audit-ml-models"
    LOCAL_MODEL_DIR: str = "./models"

    # Model Monitoring
    DRIFT_DETECTION_ENABLED: bool = True
    DRIFT_THRESHOLD: float = 0.1
    PERFORMANCE_MONITORING_ENABLED: bool = True
    ALERT_ON_ACCURACY_DROP: float = 0.05  # Alert if accuracy drops by 5%

    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_TENSORBOARD: bool = True
    TENSORBOARD_LOG_DIR: str = "./tensorboard_logs"

    # API
    API_VERSION: str = "v1"
    MAX_PREDICTION_BATCH_SIZE: int = 1000
    PREDICTION_TIMEOUT_SECONDS: int = 30

    # Security
    REQUIRE_AUTHENTICATION: bool = True
    ALLOWED_USERS: list = ["cpa", "auditor", "partner", "manager"]

    class Config:
        env_prefix = "AUDIT_ML_"
        case_sensitive = False


# Singleton settings instance
settings = AuditMLSettings()
