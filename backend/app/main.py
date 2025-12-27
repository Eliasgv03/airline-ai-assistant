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

# Global state for tracking model loading
_model_loading_status = {"started": False, "completed": False, "error": None}


def _preload_vector_service():
    """
    Pre-load the VectorService (embedding model) in a background thread.
    This allows the server to start immediately and handle health checks
    while the model loads in the background.
    """
    from app.utils.logger import get_logger

    logger = get_logger(__name__)

    global _model_loading_status
    _model_loading_status["started"] = True

    try:
        logger.info("🔄 Background thread: Starting VectorService pre-load...")
        from app.services.vector_service import get_vector_service

        get_vector_service()
        _model_loading_status["completed"] = True
        logger.info("✅ Background thread: VectorService pre-loaded successfully!")
    except Exception as e:
        _model_loading_status["error"] = str(e)
        logger.error(f"❌ Background thread: Failed to pre-load VectorService: {e}")


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    import threading

    from app.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("🚀 Application starting up...")

    # Start pre-loading the embedding model in a background thread
    # This allows the server to bind to the port immediately (passing health checks)
    # while the model loads asynchronously
    preload_thread = threading.Thread(target=_preload_vector_service, daemon=True)
    preload_thread.start()
    logger.info("🔄 VectorService pre-load started in background thread")

    logger.info("✅ Application startup complete - server ready to receive requests")


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/ready")
async def readiness_check():
    """
    Readiness endpoint that checks if the embedding model is loaded.
    Returns 503 if still loading, 200 if ready.
    """
    from fastapi.responses import JSONResponse

    if _model_loading_status["error"]:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Model loading failed",
                "error": _model_loading_status["error"],
            },
        )

    if not _model_loading_status["completed"]:
        return JSONResponse(
            status_code=503,
            content={
                "status": "loading",
                "message": "Embedding model is still loading. Please wait...",
                "started": _model_loading_status["started"],
            },
        )

    return {"status": "ready", "message": "All services ready", "model_loaded": True}


@app.get("/")
async def root():
    return {"message": "Welcome to Airline AI Assistant API"}
