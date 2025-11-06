"""Configuration settings for LLM Service"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Service configuration"""

    # Service info
    SERVICE_NAME: str = "llm"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_TTL: int = 3600  # 1 hour cache TTL

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 4096

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384  # all-MiniLM-L6-v2 produces 384-dim vectors
    EMBEDDING_BATCH_SIZE: int = 32

    # RAG Configuration
    RAG_TOP_K: int = 5  # Number of documents to retrieve
    RAG_SIMILARITY_THRESHOLD: float = 0.7  # Minimum similarity score
    RAG_CHUNK_SIZE: int = 512  # Characters per chunk
    RAG_CHUNK_OVERLAP: int = 50  # Overlap between chunks

    # LLM Generation
    MAX_RETRIES: int = 3
    TIMEOUT: int = 60  # seconds
    STREAM_ENABLED: bool = True

    # Knowledge Base
    KB_AUTO_UPDATE: bool = True
    KB_UPDATE_INTERVAL: int = 3600  # seconds

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
