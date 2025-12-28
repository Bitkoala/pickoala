import asyncio
import os
import sys

# Add current directory to path so we can import app
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def update_schema():
    print("Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Checking if column 'type' exists in 'file_collections'...")
        try:
            print("Attempting to add 'type' column to 'file_collections'...")
            # We attempt to add the column. If it exists, this might fail depending on DB.
            # For MySQL/PostgreSQL, usually fails if exists.
            # SQLite supports ADD COLUMN.
            await conn.execute(text("ALTER TABLE file_collections ADD COLUMN type VARCHAR(20) DEFAULT 'file'"))
            await conn.execute(text("CREATE INDEX ix_file_collections_type ON file_collections (type)"))
            print("Column 'type' added successfully.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")
            
    print("Done.")

if __name__ == "__main__":
    asyncio.run(update_schema())
