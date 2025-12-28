"""
File Cleanup Service
Handles physical deletion of expired files.
"""
import logging
import asyncio
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.file import File
from app.services.storage import get_storage_backend_async

logger = logging.getLogger(__name__)

async def cleanup_expired_files(batch_size: int = 100):
    """
    Physically delete files that have expired.
    Running in batches to avoid locking the database for too long.
    """
    logger.info("Starting expired files cleanup...")
    total_deleted = 0
    
    try:
        while True:
            async with AsyncSessionLocal() as db:
                # Find expired files
                # expire_at < now
                now = datetime.utcnow()
                result = await db.execute(
                    select(File).where(
                        File.expire_at < now
                    ).limit(batch_size)
                )
                files = result.scalars().all()
                
                if not files:
                    break
                
                logger.info(f"Found {len(files)} expired files to clean up")
                storage = await get_storage_backend_async()
                
                ids_to_delete = []
                
                for file in files:
                    try:
                        # logical deletion from storage
                        # Note: storage.delete might require full path or relative path depending on implementation
                        # In `files.py`: 
                        # await storage.delete(file_obj.file_path)
                        # Let's check `files.py` usually passes `file_path` which is relative path stored in DB
                        # But LocalStorage.delete expects full path?
                        # Let's double check LocalStorage implementation in `storage/local.py` or assume standard interface.
                        # `files.py` line 181: await storage.delete(file_obj.file_path)
                        # So we assume that works.
                        
                        await storage.delete(file.file_path)
                        ids_to_delete.append(file.id)
                    except Exception as e:
                        logger.error(f"Failed to delete file from storage: {file.file_path} (ID: {file.id}): {e}")
                        # If storage deletion fails, should we delete from DB?
                        # Maybe yes, to stop loop? Or maybe keep it to retry?
                        # If we don't delete from DB, this loop will pick it up forever.
                        # For now, let's delete from DB even if storage fails, to clean up metadata.
                        # Or maybe we should mark it as error?
                        # Risk: Orphaned files on disk. Admin can clean up manually.
                        ids_to_delete.append(file.id)
                
                if ids_to_delete:
                    # Batch delete from DB
                    # Delete objects using DB session
                    # We have `files` objects attached to session? 
                    # Yes, session is open.
                    
                    for file in files:
                        if file.id in ids_to_delete:
                            await db.delete(file)
                    
                    await db.commit()
                    count = len(ids_to_delete)
                    total_deleted += count
                    logger.info(f"Deleted {count} expired files from database")
                
                # Small pause to yield control if multiple batches
                await asyncio.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Error during expired files cleanup: {e}")
        
    logger.info(f"Expired files cleanup completed. Total deleted: {total_deleted}")
    return total_deleted
