
import asyncio
import os
import sys

# Add current dir to path to find app
sys.path.append(os.getcwd())

from app.config import get_settings
from app.database import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.image import Image
from app.models.user import User

async def check_db():
    settings = get_settings()
    # Host-side execution override
    db_url = settings.database_url.replace("172.17.0.1", "localhost")
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Get last 10 images
            result = await session.execute(
                select(Image).order_by(Image.id.desc()).limit(10)
            )
            images = result.scalars().all()
            
            print("\n" + "="*80)
            print(f"{'ID':<5} | {'Filename':<10} | {'User ID':<8} | {'Album ID':<8} | {'Status':<10} | {'Created At'}")
            print("-" * 80)
            
            for img in images:
                print(f"{img.id:<5} | {img.filename:<10} | {str(img.user_id):<8} | {str(img.album_id):<8} | {img.status:<10} | {img.created_at}")
            
            print("="*80 + "\n")
            
            # Check for a specific user if images have user_id
            if images:
                u_id = images[0].user_id
                if u_id:
                    u_result = await session.execute(select(User).where(User.id == u_id))
                    user = u_result.scalar_one_or_none()
                    if user:
                        print(f"Latest image belongs to user: {user.username} (ID: {user.id})")
        except Exception as e:
            print(f"Error during DB query: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_db())
