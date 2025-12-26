"""
Smart Auto-Ingestion for Production Deployment

This script automatically runs data ingestion on first deployment,
but SKIPS if data already exists (prevents duplicates).
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.config import get_settings  # noqa: E402
from app.scripts.ingest_data import main as ingest_main  # noqa: E402
from app.services.vector_service import VectorService  # noqa: E402
from app.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)


def check_database_has_data() -> bool:
    """
    Check if database already has ingested data

    Returns:
        True if data exists, False if empty
    """
    try:
        vector_service = VectorService()

        # Try a simple search
        results = vector_service.similarity_search(
            query="baggage allowance",  # Common query
            k=1,
        )

        if results and len(results) > 0:
            logger.info(f"✅ Database has data ({len(results)} documents found)")
            return True
        else:
            logger.info("📭 Database appears empty")
            return False

    except Exception as e:
        logger.warning(f"⚠️ Could not check database: {e}")
        # If we can't check, assume empty and try to ingest
        return False


async def smart_auto_ingest():
    """
    Smart auto-ingestion that prevents duplicates

    - Checks if running in production
    - Checks if database already has data
    - Only ingests if database is empty
    """
    try:
        settings = get_settings()

        # Only run in production
        if settings.ENVIRONMENT != "production":
            logger.info("ℹ️ Not in production environment, skipping auto-ingestion")
            return

        logger.info("🔍 Checking if data ingestion is needed...")

        # Check if database already has data (not async)
        has_data = check_database_has_data()

        if has_data:
            logger.info("✅ Database already populated - skipping ingestion")
            logger.info("ℹ️ This prevents duplicate data on redeployments")
            return

        # Database is empty - run ingestion
        logger.info("🚀 Database is empty - starting automatic data ingestion...")
        logger.info("📦 This will take ~1-2 minutes...")

        await ingest_main()

        logger.info("✅ Auto-ingestion completed successfully!")
        logger.info("📊 Your RAG system is now ready to use")

    except Exception as e:
        logger.error(f"❌ Auto-ingestion failed: {e}", exc_info=True)
        logger.warning("⚠️ Application will continue, but RAG may not work")
        logger.warning("💡 You can manually run: poetry run python -m app.scripts.ingest_data")


if __name__ == "__main__":
    # Can be run standalone for testing
    asyncio.run(smart_auto_ingest())
