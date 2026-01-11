
import asyncio
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models.image import Image
from sqlalchemy import update

async def fix():
    print("Starting AI analysis status cleanup...")
    async with AsyncSessionLocal() as session:
        # Update all 'pending' statuses to NULL
        stmt = update(Image).where(Image.ai_analysis_status == 'pending').values(ai_analysis_status=None)
        await session.execute(stmt)
        await session.commit()
        print("Cleanup complete: All existing 'pending' AI statuses have been reset.")

if __name__ == "__main__":
    asyncio.run(fix())
