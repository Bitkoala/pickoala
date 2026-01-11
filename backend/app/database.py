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
                
                # Auto-migration: Add oauth_id to users table if not exists (previously casdoor_id)
                try:
                    from sqlalchemy import text
                    # Try to rename if casdoor_id exists
                    try:
                        await conn.execute(text("ALTER TABLE users CHANGE COLUMN casdoor_id oauth_id VARCHAR(255)"))
                        logger.info("Database migration: Renamed casdoor_id to oauth_id")
                    except Exception:
                        # Rename failed, maybe column doesn't exist or already renamed
                        await conn.execute(text("ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255) UNIQUE"))
                        await conn.execute(text("CREATE INDEX ix_users_oauth_id ON users (oauth_id)"))
                        logger.info("Database migration: Added oauth_id to users table")
                except Exception:
                    # oauth_id likely exists
                    pass

                # Auto-migration: Add watermark settings to users table if not exists
                watermark_columns = [
                    ("watermark_enabled", "BOOLEAN DEFAULT FALSE"),
                    ("watermark_type", "VARCHAR(20) DEFAULT 'text'"),
                    ("watermark_text", "VARCHAR(100)"),
                    ("watermark_image_path", "VARCHAR(500)"),
                    ("watermark_opacity", "INTEGER DEFAULT 50"),
                    ("watermark_position", "VARCHAR(20) DEFAULT 'bottom-right'")
                ]
                for col_name, col_def in watermark_columns:
                    try:
                        await conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"))
                        logger.info(f"Database migration: Added {col_name} to users table")
                    except Exception:
                        # Column likely exists or other error
                        pass

                # Auto-migration: Add AI columns to images table if not exists
                ai_columns = [
                    ("ai_tags", "TEXT"),  # Use TEXT for JSON content
                    ("ai_description", "TEXT"),
                    ("ai_analysis_status", "VARCHAR(20)")  # Removed DEFAULT 'pending'
                ]
                for col_name, col_def in ai_columns:
                    try:
                        await conn.execute(text(f"ALTER TABLE images ADD COLUMN {col_name} {col_def}"))
                        logger.info(f"Database migration: Added {col_name} to images table")
                    except Exception:
                        # Column likely exists
                        pass
                
                # Cleanup: If any images are stuck in 'pending' from previous faulty migration, reset them
                try:
                    await conn.execute(text("UPDATE images SET ai_analysis_status = NULL WHERE ai_analysis_status = 'pending' AND ai_tags IS NULL"))
                    await conn.commit()
                except Exception:
                    pass
            logger.info("Database initialized successfully.")
            
            # Pre-load settings cache to avoid nested sessions and pool exhaustion during first requests
            try:
                from app.services.settings import load_settings_to_cache
                await load_settings_to_cache()
                logger.info("Settings cache warmed up.")
            except Exception as e:
                logger.warning(f"Failed to warm up settings cache: {e}")
                
            return
        except Exception as e:
            if i == retries - 1:
                logger.error(f"Failed to initialize database after {retries} attempts: {e}")
                raise e
            logger.warning(f"Database not ready yet, retrying in 2s... ({i+1}/{retries})")
            await asyncio.sleep(2)
