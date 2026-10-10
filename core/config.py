from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")

    groq_api_key:str
    groq_base_url:str = "https://api.groq.com/openai/v1"
    
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 384
    chat_model: str = "openai/gpt-oss-20b"


    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents_local"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql://app:app@localhost:5433/app"

    chat_history_limit: int = 10
    session_ttl_seconds: int = 3600

settings = Settings()