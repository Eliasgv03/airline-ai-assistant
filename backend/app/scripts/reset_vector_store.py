"""
Reset Vector Store

Utility script to drop existing langchain-pg tables and re-create them.
Useful when changing embedding dimensions.
Usage: poetry run python -m app.scripts.reset_vector_store
"""

import asyncio

from sqlalchemy import text

from app.db.database import engine
from app.utils.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


async def reset_db():
    logger.info("Resetting vector store tables...")
    async with engine.begin() as conn:
        # Tables used by langchain-postgres
        await conn.execute(text("DROP TABLE IF EXISTS langchain_pg_embedding CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS langchain_pg_collection CASCADE;"))
        logger.info("Dropped existing tables.")

        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        logger.info("Ensured 'vector' extension is enabled.")


if __name__ == "__main__":
    import asyncio
    import sys

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(reset_db())
    print("Reset complete.")
