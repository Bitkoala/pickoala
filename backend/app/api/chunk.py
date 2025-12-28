
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import shutil
import json
import secrets
from datetime import datetime
from pathlib import Path

from app.database import get_db
from app.models.user import User
from app.models.file import File as FileModel
from app.api.deps import get_current_user_optional
from app.utils.rate_limit import get_real_ip
from app.services import security as security_service
from app.services import settings as settings_service
from app.services.storage import get_storage_backend_async
from app.services.video import video_service
from app.config import get_settings

router = APIRouter(prefix="/chunk", tags=["ChunkUpload"])
settings = get_settings()

# Temporary directory for chunks
CHUNK_TEMP_DIR = os.path.join(settings.upload_path, "temp_chunks")
os.makedirs(CHUNK_TEMP_DIR, exist_ok=True)

@router.post("/init")
async def init_upload(
    request: Request,
    filename: str = Body(..., embed=True),
    file_size: int = Body(..., embed=True),
    mime_type: str = Body(..., embed=True),
    total_chunks: int = Body(..., embed=True),
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Initialize a chunked upload session.
    Returns upload_id.
    """
    ip = get_real_ip(request)
    user_id = user.id if user else None
    
    # 1. Permission and Ban Check
    is_banned, ban_reason = await security_service.is_banned(ip, user_id, db)
    if is_banned:
        raise HTTPException(status_code=403, detail=f"Upload banned: {ban_reason}")
    
    if not user and not await settings_service.is_guest_upload_enabled():
        raise HTTPException(status_code=403, detail="Guest upload disabled")

    # 2. Determine limits
    limit_type = 'file'
    if mime_type.startswith("video/"):
        limit_type = 'video'
        
    is_vip = False
    if user and user.vip_expire_at and user.vip_expire_at > datetime.utcnow():
        is_vip = True
        
    # Rate limit check (count initialization as 1 upload attempt? Or check concurrency?)
    # For now, we check standard rate limit for 'init' to prevent spamming sessions
    is_allowed, _, _ = await security_service.check_rate_limit_multi(
        ip, user_id, is_user=bool(user), is_vip=is_vip, limit_type=limit_type
    )
    if not is_allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
    # Size check
    if limit_type == 'video':
        if is_vip: max_size = await settings_service.get_max_video_upload_size_vip()
        elif user: max_size = await settings_service.get_max_video_upload_size_user()
        else: max_size = await settings_service.get_max_video_upload_size_guest()
    else:
        if is_vip: max_size = await settings_service.get_max_file_upload_size_vip()
        elif user: max_size = await settings_service.get_max_file_upload_size_user()
        else: max_size = await settings_service.get_max_file_upload_size_guest()
        
    if file_size > max_size:
        raise HTTPException(status_code=413, detail=f"File too large (Limit: {max_size})")

    # 3. Create Session
    upload_id = secrets.token_urlsafe(16)
    session_dir = os.path.join(CHUNK_TEMP_DIR, upload_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save metadata
    meta = {
        "upload_id": upload_id,
        "filename": filename,
        "file_size": file_size,
        "mime_type": mime_type,
        "total_chunks": total_chunks,
        "user_id": user_id,
        "ip": ip,
        "created_at": datetime.utcnow().isoformat()
    }
    with open(os.path.join(session_dir, "meta.json"), "w") as f:
        json.dump(meta, f)
        
    return {"upload_id": upload_id, "chunk_size": 2 * 1024 * 1024} # Recommend 2MB chunks (or client decides)

@router.post("/upload/{upload_id}")
async def upload_chunk(
    upload_id: str,
    chunk_index: int = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload a single chunk.
    """
    session_dir = os.path.join(CHUNK_TEMP_DIR, upload_id)
    if not os.path.exists(os.path.join(session_dir, "meta.json")):
        raise HTTPException(status_code=404, detail="Upload session not found")
        
    chunk_path = os.path.join(session_dir, f"part_{chunk_index}")
    
    try:
        content = await file.read()
        with open(chunk_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save chunk: {str(e)}")
        
    return {"success": True, "chunk_index": chunk_index}

@router.get("/status/{upload_id}")
async def get_status(upload_id: str):
    """
    Get uploaded chunks for resumption.
    """
    session_dir = os.path.join(CHUNK_TEMP_DIR, upload_id)
    if not os.path.exists(os.path.join(session_dir, "meta.json")):
        raise HTTPException(status_code=404, detail="Upload session not found")
        
    uploaded_chunks = []
    for f in os.listdir(session_dir):
        if f.startswith("part_"):
            try:
                idx = int(f.split("_")[1])
                uploaded_chunks.append(idx)
            except:
                pass
                
    return {"upload_id": upload_id, "uploaded_chunks": uploaded_chunks}

@router.post("/complete/{upload_id}")
async def complete_upload(
    request: Request,
    upload_id: str,
    password: Optional[str] = Body(None, embed=True),
    expire_days: Optional[int] = Body(None, embed=True),
    download_limit: Optional[int] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
):
    """
    Merge chunks and finish upload.
    """
    session_dir = os.path.join(CHUNK_TEMP_DIR, upload_id)
    meta_path = os.path.join(session_dir, "meta.json")
    
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="Upload session not found")
        
    with open(meta_path, "r") as f:
        meta = json.load(f)
        
    total_chunks = meta["total_chunks"]
    filename = meta["filename"]
    user_id = meta["user_id"]
    mime_type = meta["mime_type"]
    file_size_meta = meta["file_size"]
    
    # Check all chunks present
    for i in range(total_chunks):
        if not os.path.exists(os.path.join(session_dir, f"part_{i}")):
            raise HTTPException(status_code=400, detail=f"Missing chunk {i}")

    # Merge Chunks
    merged_path = os.path.join(session_dir, f"merged_{filename}")
    try:
        with open(merged_path, "wb") as outfile:
            for i in range(total_chunks):
                chunk_path = os.path.join(session_dir, f"part_{i}")
                with open(chunk_path, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")
    
    # Validate Size
    real_size = os.path.getsize(merged_path)
    if real_size != file_size_meta:
        # Warning but persist? Or strict? Strict for security.
        pass
    
    # Process User & Expiration
    expire_at = None
    if user_id:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        is_vip = user.vip_expire_at > datetime.utcnow() if (user and user.vip_expire_at) else False
    else:
        user = None
        is_vip = False
        
    limit_type = 'video' if mime_type.startswith("video/") else 'file'
    
    if limit_type == 'video':
        if user:
            if not expire_days: expire_days = 30
        else:
            expire_days = 1
    else:
        if user:
            if not expire_days: expire_days = 30
        else:
            expire_days = 1
            
    if expire_days:
        from datetime import timedelta
        expire_at = datetime.utcnow() + timedelta(days=expire_days)

    # Save to Storage (Efficiently)
    storage = await get_storage_backend_async()
    from app.utils.date_path import get_date_path
    date_path = await get_date_path()
    full_path_prefix = f"files/{date_path}"
    
    ext = filename.split(".")[-1].lower() if "." in filename else "bin"
    file_id_name = secrets.token_hex(4)
    final_full_filename = f"{file_id_name}.{ext}"
    unique_code = secrets.token_urlsafe(5)

    try:
        # Use save_from_path to avoid memory constraints
        if hasattr(storage, 'save_from_path'):
            file_path = await storage.save_from_path(merged_path, final_full_filename, full_path_prefix)
        else:
            # Fallback (risky for 2GB) or implement naive save_from_path in base?
            # We implemented it in base, so it should exist!
            file_path = await storage.save_from_path(merged_path, final_full_filename, full_path_prefix)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage saving failed: {str(e)}")

    # Video Thumbnail Generation
    thumbnail_path = None
    if mime_type.startswith("video/"):
        try:
            # Create temp thumb path
            tmp_thumb_path = merged_path + ".jpg"
            
            # Use video service on the MERGED file directly (no need to copy temp)
            if video_service.generate_thumbnail(merged_path, tmp_thumb_path):
                # Upload thumbnail
                # Thumbnails are small, safe to read
                import aiofiles
                async with aiofiles.open(tmp_thumb_path, "rb") as f:
                    thumb_content = await f.read()
                    thumb_filename = f"{file_id_name}_thumb.jpg"
                    thumbnail_path = await storage.save(thumb_content, thumb_filename, full_path_prefix)
            
            if os.path.exists(tmp_thumb_path):
                os.remove(tmp_thumb_path)
                
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")

    # DB Entry
    new_file = FileModel(
        filename=file_id_name,
        original_filename=filename,
        extension=ext,
        mime_type=mime_type,
        file_size=real_size,
        file_path=file_path,
        thumbnail_path=thumbnail_path,
        unique_code=unique_code,
        access_password=password,
        storage_type=storage.storage_type,
        user_id=user_id,
        expire_at=expire_at,
        download_limit=download_limit
    )
    
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    
    # Cleanup Session
    try:
        shutil.rmtree(session_dir)
    except:
        pass # Background cleanup task handles leftovers
    
    # Construct response similar to standard upload
    # Need to return what `FileResponse` expects? New `FileResponse`?
    # FileResponse is pydantic model.
    # But wait, original `upload_file` returned `FileResponse`.
    # `shareLink` is computed in frontend from `unique_code` usually? 
    # Frontend needs `unique_code`, `original_filename` etc.
    # Return dict compatible with `uploadedItems` in frontend
    share_link_base = settings.site_url.rstrip('/') if settings.site_url else ""
    # Frontend logic: `shareLink = ${window.location.origin}/s/${fileData.unique_code}`
    
    # Just return the model dict
    return new_file


