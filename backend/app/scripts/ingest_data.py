"""
Data Ingestion Script

Run this script to populate the vector database with the Air India policies.
Usage: poetry run python -m app.scripts.ingest_data
"""

import asyncio
import os
import sys

# Windows asyncio event loop fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.services.vector_service import VectorService
from app.utils.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def main():
    logger.info("Starting data ingestion...")

    # Path to policies
    # Assuming script is run from backend root, so data/policies is correct relative path
    # or use absolute path calculation
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    policies_dir = os.path.join(base_dir, "data", "policies")

    if not os.path.exists(policies_dir):
        logger.error(f"Policies directory not found at: {policies_dir}")
        return

    try:
        service = VectorService()
        # ingestion in langchan-postgres might be sync or async depending on implementation
        # PGVector.add_documents is typically sync in recent versions or handles async internally via run_in_executor
        # We'll run it directly.
        service.ingest_data(policies_dir)
        logger.info("Data ingestion finished successfully.")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    main()
