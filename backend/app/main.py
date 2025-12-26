from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.middleware.logging import RequestLoggingMiddleware
from app.utils.logger import setup_logging

# Setup logging
setup_logging()

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
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
    from app.scripts.auto_ingest import smart_auto_ingest
    from app.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("🚀 Application starting up...")

    # Run smart auto-ingestion (only if DB is empty)
    await smart_auto_ingest()

    logger.info("✅ Application startup complete")


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/")
async def root():
    return {"message": "Welcome to Airline AI Assistant API"}
