import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Hardcoded for development environment or read from env
DATABASE_URL = "mysql+aiomysql://imgbed:your_password@localhost:3306/imgbed"

async def update_schema():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        engine = create_async_engine(DATABASE_URL)
        
        async with engine.begin() as conn:
            print("Checking if column 'type' exists in 'file_collections'...")
            try:
                print("Attempting to add 'type' column to 'file_collections'...")
                await conn.execute(text("ALTER TABLE file_collections ADD COLUMN type VARCHAR(20) DEFAULT 'file'"))
                # await conn.execute(text("CREATE INDEX ix_file_collections_type ON file_collections (type)"))
                print("Column 'type' added successfully.")
            except Exception as e:
                print(f"Column might already exist or error: {e}")
                
            try:
                print("Attempting to add index 'ix_file_collections_type'...")
                await conn.execute(text("CREATE INDEX ix_file_collections_type ON file_collections (type)"))
                print("Index added successfully.")
            except Exception as e:
                print(f"Index might already exist or error: {e}")

        print("Done.")
    except Exception as e:
         print(f"Connection failed: {e}")
         print("Please ensure your database is running and credentials in script match.")

if __name__ == "__main__":
    asyncio.run(update_schema())
