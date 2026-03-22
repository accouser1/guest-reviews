"""Database Session Management"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from app.core.config import settings
from app.core.logging import logger
from app.models.base import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables if needed)"""
    try:
        # Import all models to ensure they are registered
        from app.models import (
            User, Hotel, HotelBranch, HotelSettings, Integration,
            Guest, Booking, Review, RiskScore, Deposit, Transaction, Notification
        )
        
        async with engine.begin() as conn:
            # Create tables (in production, use Alembic migrations instead)
            # await conn.run_sync(Base.metadata.create_all)
            pass
            
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
