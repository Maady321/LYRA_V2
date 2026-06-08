import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from backend.core.config import settings

logger = logging.getLogger("PostgresEngine")

# Configuration (ideally fetched from settings)
POSTGRES_URL = getattr(settings, "POSTGRES_URL", "postgresql+asyncpg://lyra:lyra_password@localhost:5432/lyra_aios")

# Create Async Engine
engine = create_async_engine(
    POSTGRES_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600
)

# Async Session Factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

async def init_postgres_db() -> None:
    """Initialize database tables"""
    logger.info("Initializing Postgres database tables...")
    try:
        # Import models here to ensure they are registered with Base
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Postgres database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing Postgres database: {e}")
        raise e

async def get_pg_session():
    """Dependency generator for database sessions in FastAPI routes"""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise e
        finally:
            await session.close()
