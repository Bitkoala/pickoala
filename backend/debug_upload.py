import sys
import os
import asyncio
from sqlalchemy import select, desc
from app.database import AsyncSessionLocal
from app.models.image import Image
from app.config import get_settings

async def check_uploads():
    settings = get_settings()
    print(f"=== Configuration ===")
    print(f"Upload Path (configured): {settings.upload_path}")
    abs_upload_path = os.path.abspath(settings.upload_path)
    print(f"Upload Path (absolute):   {abs_upload_path}")
    print(f"Exists: {os.path.exists(abs_upload_path)}")
    print(f"=====================\n")

    async with AsyncSessionLocal() as db:
        # Get last 5 images
        result = await db.execute(
            select(Image).order_by(desc(Image.created_at)).limit(5)
        )
        images = result.scalars().all()

        if not images:
            print("No images found in database.")
            return

        print(f"Found {len(images)} recent images in database:\n")
        
        for img in images:
            print(f"ID: {img.id}")
            print(f"Filename: {img.filename}")
            print(f"Original: {img.original_filename}")
            print(f"File Path (DB): {img.file_path}")
            print(f"Status: {img.status}")
            
            # Construct full path
            full_path = os.path.normpath(os.path.join(settings.upload_path, img.file_path))
            exists = os.path.isfile(full_path)
            
            print(f"Full Path: {full_path}")
            print(f"File Exists: {'YES' if exists else 'NO'}")
            if not exists:
                # Try to list directory to see what's there
                dir_path = os.path.dirname(full_path)
                print(f"  Directory: {dir_path}")
                if os.path.exists(dir_path):
                    print(f"  Dir Exists: YES")
                    try:
                        files = os.listdir(dir_path)
                        print(f"  Files in dir: {files}")
                    except Exception as e:
                        print(f"  Error listing dir: {e}")
                else:
                    print(f"  Dir Exists: NO")
            
            print("-" * 30)

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Run async function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_uploads())
