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
    # Note: Wildcards like "https://*.onrender.com" don't work with FastAPI CORS
    # For production, you can either:
    # 1. Add specific Render URLs here
    # 2. Use BACKEND_CORS_ORIGINS=["*"] for development (not recommended for production)
    # 3. Use a custom CORS middleware that validates origins dynamically
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:3000",
        "https://airline-ai-assistant-1.onrender.com",
        # Add your specific Render frontend URL here when deploying
        # Example: "https://airline-ai-assistant-frontend.onrender.com",
    ]

    # ========================================
    # LLM Configuration
    # ========================================

    # Google Gemini API
    GOOGLE_API_KEY: str | None = None

    # Gemini Model Pool (December 2025 - Accurate Quotas)
    # Reference: User-provided data from Google AI Studio
    GEMINI_MODEL_POOL: list[str] = [
        "gemini-2.5-flash-lite",  # ~1,000 RPD - Best free tier (preview)
        "gemini-2.5-flash",  # ~20-250 RPD - Most used, recently reduced
        "gemini-2.0-flash",  # ~20-50 RPD - Experimental, low quota
    ]

    # Legacy Gemini Models (kept for reference, not in active pool)
    GEMINI_LEGACY_MODELS: list[str] = [
        "gemini-1.5-flash",  # Deprecated December 2025
        "gemini-1.5-flash-8b",  # Deprecated December 2025
        "gemini-1.5-pro",  # Deprecated December 2025
    ]

    # Primary Gemini model
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # Groq API (Alternative LLM Provider)
    GROQ_API_KEY: str | None = None

    # Groq Model Pool (High throughput, generous free tier)
    # Reference: https://console.groq.com/docs/models
    GROQ_MODEL_POOL: list[str] = [
        "llama-3.3-70b-versatile",  # Best overall, 70B params
        "llama-3.1-70b-versatile",  # Stable, good performance
        "mixtral-8x7b-32768",  # Fast, 32k context
        "llama-3.1-8b-instant",  # Fastest, instant responses
    ]

    # Primary Groq model
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # LLM Provider Selection
    LLM_PROVIDER: str = "gemini"  # Options: "gemini" or "groq"

    # ========================================
    # LangSmith Tracing Configuration
    # ========================================

    # Enable/disable tracing (LangSmith uses LANGSMITH_TRACING)
    LANGSMITH_TRACING: bool = False

    # LangSmith API key
    LANGSMITH_API_KEY: str | None = None

    # Project name in LangSmith
    LANGSMITH_PROJECT: str = "airline-ai-assistant"

    # LangSmith endpoint
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"

    @property
    def is_tracing_enabled(self) -> bool:
        """Check if LangSmith tracing is properly configured"""
        return (
            self.LANGSMITH_TRACING
            and self.LANGSMITH_API_KEY is not None
            and len(self.LANGSMITH_API_KEY) > 0
        )

    # Database (PostgreSQL with pgvector)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/airline_ai"

    # Vector Store Configuration
    VECTOR_STORE_COLLECTION_NAME: str = "air_india_policies"
    EMBEDDING_DIMENSION: int = 384

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings():
    settings = Settings()

    # Map LangSmith config to LangChain env vars for library compatibility
    if settings.is_tracing_enabled:
        import os

        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY or ""
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT

    return settings
