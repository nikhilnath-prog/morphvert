"""
Database connection and session management.

Handles SQLAlchemy engine creation, session factory,
and database utilities for async operations.
"""

from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings


# Create async engine
try:
    # Build engine kwargs conditionally based on pool class
    engine_kwargs = {
        "echo": settings.DATABASE_ECHO,
    }
    
    # Different connection args for SQLite vs PostgreSQL
    if settings.DATABASE_URL.startswith("sqlite"):
        # SQLite connection args
        engine_kwargs["connect_args"] = {"timeout": 10, "check_same_thread": False}
        # SQLite uses NullPool
        engine_kwargs["poolclass"] = NullPool
        db_url = settings.DATABASE_URL
    else:
        # PostgreSQL connection args
        engine_kwargs["connect_args"] = {"timeout": 10, "command_timeout": 10}
        
        if settings.ENVIRONMENT == "production":
            engine_kwargs["poolclass"] = QueuePool
            engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
            engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        else:
            # Development uses NullPool (no connection pooling)
            engine_kwargs["poolclass"] = NullPool
        
        # Convert PostgreSQL URL to asyncpg dialect
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(db_url, **engine_kwargs)
except ImportError:
    # If asyncpg is not installed, create a placeholder
    # This allows the app to start even without the DB driver
    engine = None


# Create async session factory
if engine is not None:
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
else:
    SessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session in routes.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    if SessionLocal is None:
        raise RuntimeError("Database engine not initialized. Install asyncpg or configure database.")
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    Drops and recreates all tables defined in Base metadata.
    Use Alembic for migrations in production.
    """
    if engine is None:
        raise RuntimeError("Database engine not initialized. Install asyncpg or configure database.")
    from app.models.base import Base
    
    async with engine.begin() as conn:
        # Drop all existing tables to ensure clean slate
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables from models
        await conn.run_sync(Base.metadata.create_all)


async def ensure_anonymous_upload_schema() -> None:
    """Make the files table compatible with anonymous uploads."""
    if engine is None:
        return

    if not settings.DATABASE_URL.startswith("postgresql"):
        return

    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE files ALTER COLUMN user_id DROP NOT NULL"))
        await conn.execute(text("ALTER TABLE conversions ALTER COLUMN user_id DROP NOT NULL"))


async def close_db() -> None:
    """Close database connection."""
    if engine is not None:
        await engine.dispose()
