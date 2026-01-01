from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.middleware.logging import RequestLoggingMiddleware
from app.utils.logger import setup_logging

# Setup logging
setup_logging()

settings = get_settings()

# OpenAPI documentation
DESCRIPTION = """
# 🛫 Air India Virtual Assistant API

An AI-powered chatbot inspired by Air India's **"Maharaja"** assistant.
Built for the AI Champions technical exercise.

## Features

* **💬 Conversational AI** - Natural multi-turn conversations with context memory
* **✈️ Flight Search** - Real-time flight information via Amadeus API
* **📚 RAG System** - Policy documents indexed in PostgreSQL + pgvector
* **🌍 Multilingual** - Supports English, Hindi, Spanish, Portuguese, French
* **🎭 Maharaja Persona** - Authentic Air India brand experience

## Architecture

- **LLM**: Google Gemini 2.5 Flash (with Groq fallback)
- **Embeddings**: Google text-embedding-004
- **Vector Store**: PostgreSQL + pgvector
- **Framework**: LangChain for orchestration

## Benchmark Results

- **Pass Rate**: 89.5% (17/19 tests)
- **Avg Latency**: 4.7s
- **Avg Accuracy**: 93.4%
"""

app = FastAPI(
    title="Air India Assistant API",
    description=DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AI Champions Technical Exercise",
        "url": "https://github.com/Eliasgv03/airline-ai-assistant",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "chat",
            "description": "Conversational AI endpoints for the Maharaja assistant",
        },
        {
            "name": "flights",
            "description": "Flight search and details via Amadeus API",
        },
        {
            "name": "health",
            "description": "Health and readiness checks",
        },
    ],
)

# CORS Middleware
# For production, we allow Render domains dynamically
# In development, we use the specific origins from config
# In production, if only default localhost origins are present, allow all origins
# This handles the case where BACKEND_CORS_ORIGINS wasn't explicitly configured for production
if settings.ENVIRONMENT == "production":
    # Check if all origins are localhost (default values)
    default_origins = {
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:3000",
    }
    configured_origins = set(settings.BACKEND_CORS_ORIGINS)
    # If only default localhost origins (or empty), allow all in production
    if not configured_origins or configured_origins.issubset(default_origins):
        cors_origins = ["*"]
    else:
        cors_origins = settings.BACKEND_CORS_ORIGINS.copy()
else:
    cors_origins = settings.BACKEND_CORS_ORIGINS.copy()

# Cannot use allow_credentials=True with allow_origins=["*"]
allow_creds = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware (for debugging)
app.add_middleware(RequestLoggingMiddleware)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    from app.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("🚀 Application starting up...")

    # NOTE: With Google Embeddings API, no background model loading is needed
    # The API is instant and ready to use immediately

    logger.info("✅ Application startup complete - server ready to receive requests")


@app.get("/health", tags=["health"], summary="Health check")
async def health_check():
    """Basic health check endpoint for load balancers and monitoring."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/ready", tags=["health"], summary="Readiness check")
async def readiness_check():
    """
    Readiness endpoint for Kubernetes/container orchestration.
    With Google Embeddings API, the service is always ready immediately.
    """
    return {"status": "ready", "message": "All services ready"}


@app.get("/", tags=["health"], summary="API root", include_in_schema=False)
async def root():
    """Welcome message and API info."""
    return {
        "message": "Welcome to Air India Assistant API",
        "docs": "/docs",
        "version": settings.VERSION,
    }
