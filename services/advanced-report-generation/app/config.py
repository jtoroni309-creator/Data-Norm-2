"""
Configuration for Advanced Report Generation Service

Centralized settings using Pydantic for validation
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Service configuration"""

    # Service
    SERVICE_NAME: str = "advanced-report-generation"
    SERVICE_PORT: int = 8019

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4-turbo"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-large"

    # Azure Cognitive Search (for RAG)
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_API_KEY: Optional[str] = None
    AZURE_SEARCH_INDEX_NAME: str = "audit-workpapers-index"

    # Report Generation
    CONSTITUTIONAL_AI_ENABLED: bool = True
    MULTI_AGENT_ENABLED: bool = True
    SELF_CONSISTENCY_SAMPLES: int = 5
    RAG_TOP_K: int = 10
    RAG_RERANK_TOP_K: int = 3

    # Model Parameters
    OPINION_AGENT_TEMPERATURE: float = 0.05  # Very conservative
    BASIS_AGENT_TEMPERATURE: float = 0.1
    FINDINGS_AGENT_TEMPERATURE: float = 0.15
    DISCLOSURE_AGENT_TEMPERATURE: float = 0.1
    COMPLIANCE_AGENT_TEMPERATURE: float = 0.0  # Deterministic
    EDITOR_AGENT_TEMPERATURE: float = 0.1

    # Compliance Validation
    COMPLIANCE_RULES_PATH: str = "/app/rules/compliance_rules.json"
    NEURAL_COMPLIANCE_ENABLED: bool = True
    MIN_COMPLIANCE_SCORE: float = 0.95  # 95% minimum
    BLOCK_ON_CRITICAL_VIOLATIONS: bool = True

    # Performance
    MAX_TOKENS_PER_SECTION: int = 2000
    REQUEST_TIMEOUT_SECONDS: int = 180
    ENABLE_CACHING: bool = True
    CACHE_TTL_SECONDS: int = 3600

    # Monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Security
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_ORIGINS: list = ["*"]

    # Knowledge Graph
    REGULATORY_STANDARDS_PATH: str = "/app/data/regulatory_standards.json"
    KNOWLEDGE_GRAPH_CACHE_PATH: str = "/app/cache/knowledge_graph.pkl"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
