from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:3000",
        "https://*.onrender.com",
    ]

    # LLM (Gemini / Google Generative AI)
    GOOGLE_API_KEY: str | None = None

    # Model pool with fallback (ordered by preference)
    # As of December 2025: Gemini 1.5 deprecated, use 2.5/3.0 series
    GEMINI_MODEL_POOL: list[str] = [
        "gemini-2.5-flash-lite",  # Fallback 1: High throughput
        "gemini-2.5-flash",  # Fallback 2: Good but low free tier quota (20 RPD)
        "gemini-2.0-flash",  # Fallback 3: Older but stable
    ]

    # Primary model (first in pool)
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Database (PostgreSQL with pgvector)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/airline_ai"

    # Vector Store Configuration
    VECTOR_STORE_COLLECTION_NAME: str = "air_india_policies"
    EMBEDDING_DIMENSION: int = 384

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings():
    return Settings()
