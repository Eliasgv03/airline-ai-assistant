"""
Database Configuration

This module handles the database connection and session management.
It uses SQLAlchemy with asyncpg for asynchronous database access.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

settings = get_settings()

# Ensure we use the async driver
# Convert postgres:// to postgresql+asyncpg:// if needed
# But typically settings.DATABASE_URL should be set correctly for async
# If using standard Render/URL, it might be 'postgres://...', which SQLAlchemy requires to be 'postgresql://'
# For async, we usually want system-level handling or explicit driver
# We'll expect DATABASE_URL to be compatible or patch it here.

db_url = settings.DATABASE_URL
if "localhost" in db_url:
    db_url = db_url.replace("localhost", "127.0.0.1")

# Force psycopg driver for Windows compatibility (asyncpg conflicts with SelectorLoop)
if "postgresql+asyncpg://" in db_url:
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
elif "postgresql://" in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
elif "postgres://" in db_url:
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Handle disconnected connections
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting an async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
