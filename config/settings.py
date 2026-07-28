import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    # APP
    PROJECT_NAME: str = "Enterprise AI Research & Knowledge Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "enterprise_super_secret_jwt_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # DATABASE
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_research.db"

    # REDIS
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # QDRANT VECTOR STORE
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "enterprise_knowledge_chunks"
    QDRANT_IN_MEMORY: bool = True

    # EMBEDDINGS & RAG
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    DEFAULT_TOP_K: int = 5
    RE_RANK_ENABLED: bool = True

    # LLM PROVIDERS
    DEFAULT_LLM_PROVIDER: str = "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-large-latest"

    # TENSORFLOW DOCUMENT CLASSIFIER
    TF_MODEL_DIR: str = "./data/models/document_classifier"
    AUTO_CLASSIFY_ON_UPLOAD: bool = True

    # RATE LIMITING
    RATE_LIMIT_PER_MINUTE: int = 100

    # STORAGE
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    @property
    def UPLOAD_PATH(self) -> str:
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        return self.UPLOAD_DIR

    @property
    def TF_MODEL_PATH(self) -> str:
        os.makedirs(self.TF_MODEL_DIR, exist_ok=True)
        return self.TF_MODEL_DIR


settings = Settings()
