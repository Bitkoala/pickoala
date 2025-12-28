from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# MySQL async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


import logging
import asyncio

logger = logging.getLogger(__name__)

async def init_db():
    retries = 30  # Increase to 60s total wait time
    for i in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # Auto-migration: Add collection_id to files table if not exists
                try:
                    from sqlalchemy import text
                    await conn.execute(text("ALTER TABLE files ADD COLUMN collection_id INTEGER REFERENCES file_collections(id)"))
                except Exception:
                    # Column likely exists
                    pass
            logger.info("Database initialized successfully.")
            return
        except Exception as e:
            if i == retries - 1:
                logger.error(f"Failed to initialize database after {retries} attempts: {e}")
                raise e
            logger.warning(f"Database not ready yet, retrying in 2s... ({i+1}/{retries})")
            await asyncio.sleep(2)
