from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Airline AI Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "https://*.onrender.com"]

    # LLM (Gemini / Google Generative AI)
    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Database (PostgreSQL with pgvector)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/airline_ai"
    
    # Vector Store Configuration
    VECTOR_STORE_COLLECTION_NAME: str = "air_india_policies"
    EMBEDDING_DIMENSION: int = 768

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

@lru_cache()
def get_settings():
    return Settings()
