"""
Database Initialization Script

This script initializes the database by:
1. Creating the 'vector' extension if it doesn't exist.
2. Creating the necessary tables (including embeddings).

Usage:
    poetry run python -m app.db.init_db
"""

import asyncio

from app.db.database import engine
from app.utils.logger import get_logger, setup_logging
from sqlalchemy import text

# Ensure models are imported so Base.metadata knows about them
# We will create the vector model in a moment, but for now we want to setup the extension
# from app.models.vector_store import Embedding  # We will create this next

setup_logging()
logger = get_logger(__name__)


async def init_db():
    """Initialize the database schema."""
    logger.info("Initializing database...")

    async with engine.begin() as conn:
        # 1. Enable pgvector extension
        logger.info("Creating 'vector' extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # 2. Create tables
        # Currently we don't have declared models for Base.metadata, but this framework is ready
        # logger.info("Creating tables...")
        # await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialization completed successfully.")


def main():
    import sys

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(init_db())


if __name__ == "__main__":
    main()
