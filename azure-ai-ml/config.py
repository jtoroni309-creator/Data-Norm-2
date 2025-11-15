"""
Azure AI/ML Training Environment Configuration

Centralized configuration for all Azure services and ML training parameters
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project Settings
    PROJECT_NAME: str = "Aura Audit AI - Azure ML Training"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Azure Subscription
    AZURE_SUBSCRIPTION_ID: str = Field(..., env="AZURE_SUBSCRIPTION_ID")
    AZURE_RESOURCE_GROUP: str = Field(default="rg-aura-ml-prod", env="AZURE_RESOURCE_GROUP")
    AZURE_LOCATION: str = Field(default="eastus", env="AZURE_LOCATION")

    # Azure Machine Learning
    AZUREML_WORKSPACE_NAME: str = Field(default="aura-ml-workspace", env="AZUREML_WORKSPACE_NAME")
    AZUREML_COMPUTE_NAME: str = Field(default="cpu-cluster", env="AZUREML_COMPUTE_NAME")
    AZUREML_GPU_COMPUTE_NAME: str = Field(default="gpu-cluster", env="AZUREML_GPU_COMPUTE_NAME")
    AZUREML_EXPERIMENT_NAME: str = Field(default="audit-model-training", env="AZUREML_EXPERIMENT_NAME")

    # Azure OpenAI Service
    AZURE_OPENAI_ENDPOINT: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str = Field(..., env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(default="gpt-4-turbo", env="AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = Field(default="text-embedding-3-large", env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    # Azure AI Document Intelligence (Form Recognizer)
    AZURE_FORM_RECOGNIZER_ENDPOINT: str = Field(..., env="AZURE_FORM_RECOGNIZER_ENDPOINT")
    AZURE_FORM_RECOGNIZER_KEY: str = Field(..., env="AZURE_FORM_RECOGNIZER_KEY")

    # Azure Cognitive Search
    AZURE_SEARCH_ENDPOINT: str = Field(..., env="AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY: str = Field(..., env="AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX_NAME: str = Field(default="audit-knowledge-base", env="AZURE_SEARCH_INDEX_NAME")

    # Azure Storage
    AZURE_STORAGE_ACCOUNT_NAME: str = Field(..., env="AZURE_STORAGE_ACCOUNT_NAME")
    AZURE_STORAGE_ACCOUNT_KEY: str = Field(..., env="AZURE_STORAGE_ACCOUNT_KEY")
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = Field(None, env="AZURE_STORAGE_CONNECTION_STRING")
    AZURE_BLOB_CONTAINER_EDGAR: str = Field(default="edgar-filings", env="AZURE_BLOB_CONTAINER_EDGAR")
    AZURE_BLOB_CONTAINER_TRAINING: str = Field(default="training-data", env="AZURE_BLOB_CONTAINER_TRAINING")
    AZURE_BLOB_CONTAINER_MODELS: str = Field(default="models", env="AZURE_BLOB_CONTAINER_MODELS")

    # Azure Key Vault
    AZURE_KEY_VAULT_NAME: str = Field(..., env="AZURE_KEY_VAULT_NAME")
    AZURE_KEY_VAULT_URL: Optional[str] = None

    # Azure PostgreSQL
    AZURE_POSTGRES_HOST: str = Field(..., env="AZURE_POSTGRES_HOST")
    AZURE_POSTGRES_PORT: int = Field(default=5432, env="AZURE_POSTGRES_PORT")
    AZURE_POSTGRES_DATABASE: str = Field(default="aura_ml_training", env="AZURE_POSTGRES_DATABASE")
    AZURE_POSTGRES_USER: str = Field(..., env="AZURE_POSTGRES_USER")
    AZURE_POSTGRES_PASSWORD: str = Field(..., env="AZURE_POSTGRES_PASSWORD")
    AZURE_POSTGRES_SSL_MODE: str = Field(default="require", env="AZURE_POSTGRES_SSL_MODE")

    # Database URL (constructed)
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.AZURE_POSTGRES_USER}:{self.AZURE_POSTGRES_PASSWORD}@{self.AZURE_POSTGRES_HOST}:{self.AZURE_POSTGRES_PORT}/{self.AZURE_POSTGRES_DATABASE}?sslmode={self.AZURE_POSTGRES_SSL_MODE}"

    # Azure Databricks (optional)
    AZURE_DATABRICKS_WORKSPACE_URL: Optional[str] = Field(None, env="AZURE_DATABRICKS_WORKSPACE_URL")
    AZURE_DATABRICKS_TOKEN: Optional[str] = Field(None, env="AZURE_DATABRICKS_TOKEN")

    # Azure Synapse Analytics (optional)
    AZURE_SYNAPSE_WORKSPACE_NAME: Optional[str] = Field(None, env="AZURE_SYNAPSE_WORKSPACE_NAME")
    AZURE_SYNAPSE_SQL_ENDPOINT: Optional[str] = Field(None, env="AZURE_SYNAPSE_SQL_ENDPOINT")

    # Training Configuration
    TRAINING_BATCH_SIZE: int = Field(default=32, env="TRAINING_BATCH_SIZE")
    TRAINING_EPOCHS: int = Field(default=10, env="TRAINING_EPOCHS")
    TRAINING_LEARNING_RATE: float = Field(default=2e-5, env="TRAINING_LEARNING_RATE")
    TRAINING_VALIDATION_SPLIT: float = Field(default=0.2, env="TRAINING_VALIDATION_SPLIT")
    TRAINING_TEST_SPLIT: float = Field(default=0.1, env="TRAINING_TEST_SPLIT")
    TRAINING_RANDOM_SEED: int = Field(default=42, env="TRAINING_RANDOM_SEED")

    # Model Performance Targets
    TARGET_AUDIT_OPINION_ACCURACY: float = Field(default=0.995, env="TARGET_AUDIT_OPINION_ACCURACY")
    TARGET_DISCLOSURE_COMPLIANCE: float = Field(default=0.95, env="TARGET_DISCLOSURE_COMPLIANCE")
    TARGET_WORKPAPER_COMPLETENESS: float = Field(default=0.98, env="TARGET_WORKPAPER_COMPLETENESS")
    TARGET_MATERIALITY_ALIGNMENT: float = Field(default=0.99, env="TARGET_MATERIALITY_ALIGNMENT")
    TARGET_FRAUD_PRECISION: float = Field(default=0.97, env="TARGET_FRAUD_PRECISION")
    TARGET_FRAUD_RECALL: float = Field(default=0.95, env="TARGET_FRAUD_RECALL")

    # Data Collection
    EDGAR_SCRAPER_START_DATE: str = Field(default="2015-01-01", env="EDGAR_SCRAPER_START_DATE")
    EDGAR_SCRAPER_RATE_LIMIT: float = Field(default=0.11, env="EDGAR_SCRAPER_RATE_LIMIT")  # 10 req/sec max
    EDGAR_SCRAPER_MAX_COMPANIES: int = Field(default=10000, env="EDGAR_SCRAPER_MAX_COMPANIES")

    # Knowledge Base
    KNOWLEDGE_BASE_CHUNK_SIZE: int = Field(default=500, env="KNOWLEDGE_BASE_CHUNK_SIZE")
    KNOWLEDGE_BASE_CHUNK_OVERLAP: int = Field(default=50, env="KNOWLEDGE_BASE_CHUNK_OVERLAP")
    KNOWLEDGE_BASE_EMBEDDING_BATCH_SIZE: int = Field(default=100, env="KNOWLEDGE_BASE_EMBEDDING_BATCH_SIZE")

    # MLOps
    MLFLOW_TRACKING_URI: Optional[str] = Field(None, env="MLFLOW_TRACKING_URI")
    MLFLOW_EXPERIMENT_NAME: str = Field(default="audit-models", env="MLFLOW_EXPERIMENT_NAME")
    MODEL_REGISTRY_NAME: str = Field(default="AuditModels", env="MODEL_REGISTRY_NAME")

    # Monitoring
    ENABLE_AZURE_MONITOR: bool = Field(default=True, env="ENABLE_AZURE_MONITOR")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Security
    ENABLE_ENCRYPTION_AT_REST: bool = Field(default=True, env="ENABLE_ENCRYPTION_AT_REST")
    ENABLE_NETWORK_ISOLATION: bool = Field(default=True, env="ENABLE_NETWORK_ISOLATION")

    # Paths
    DATA_DIR: Path = Path("./data")
    MODELS_DIR: Path = Path("./models")
    LOGS_DIR: Path = Path("./logs")

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Construct Key Vault URL if not provided
        if not self.AZURE_KEY_VAULT_URL:
            self.AZURE_KEY_VAULT_URL = f"https://{self.AZURE_KEY_VAULT_NAME}.vault.azure.net/"

        # Construct Storage Connection String if not provided
        if not self.AZURE_STORAGE_CONNECTION_STRING:
            self.AZURE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName={self.AZURE_STORAGE_ACCOUNT_NAME};AccountKey={self.AZURE_STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"

        # Create directories
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
