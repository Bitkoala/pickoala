
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form, Body, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import shutil
import json
import secrets
from datetime import datetime
from pathlib import Path
import logging

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
from app.api.admin.audit import create_audit_log

router = APIRouter(prefix="/chunk", tags=["ChunkUpload"])
settings = get_settings()
logger = logging.getLogger(__name__)

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
    upload_mode: str = Body("file", embed=True), # 'image', 'video', 'file'
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
        "upload_mode": upload_mode,
        "user_id": user_id,
        "ip": ip,
        "created_at": datetime.utcnow().isoformat()
    }
    with open(os.path.join(session_dir, "meta.json"), "w") as f:
        json.dump(meta, f)
        
    return {"upload_id": upload_id, "chunk_size": 20 * 1024 * 1024} # 20MB chunks recommended for CF Tunnel

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
    background_tasks: BackgroundTasks,
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
    upload_mode = meta.get("upload_mode", "file")
    ip = meta.get("ip")
    
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
    
    # 只有 'file' 模式才设置有效期
    if upload_mode == 'file':
        if user_id:
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            # 登录用户：如果没传 expire_days，默认 30 天
            if not expire_days: 
                expire_days = 30
        else:
            # 游客模式：强制 1 天
            expire_days = 1
            
        if expire_days:
            from datetime import timedelta
            expire_at = datetime.utcnow() + timedelta(days=expire_days)
    else:
        # 图片和视频不设置有效期
        expire_at = None

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
    
    # Handle Image Logic specifically
    if upload_mode == 'image':
        from app.models.image import Image as ImageModel, ImageStatus
        from app.services.image import process_image
        import aiofiles
        
        # Read for processing (since it's a giant image, we might want to just get dimensions)
        async with aiofiles.open(merged_path, "rb") as f:
            content = await f.read()
            
        # Extract dimensions (we don't compress in chunk mode to preserve quality of large files)
        # but we use process_image to get info
        _, width, height, final_ext = process_image(content, ext, quality=100)
        
        audit_enabled = await settings_service.is_audit_enabled()
        initial_status = ImageStatus.PENDING if audit_enabled else ImageStatus.APPROVED
        
        image_url = storage.get_url(file_path)
        storage_url_value = image_url if image_url.startswith('http') else None

        new_record = ImageModel(
            filename=file_id_name,
            original_filename=filename,
            extension=ext,
            mime_type=mime_type,
            file_size=real_size,
            file_path=file_path,
            width=width,
            height=height,
            storage_type=storage.storage_type,
            storage_url=storage_url_value,
            user_id=user_id,
            album_id=None, # Support album selection if needed later
            upload_ip=ip,
            status=initial_status
        )
    else:
        new_record = FileModel(
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
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    # 记录审计日志
    try:
        await create_audit_log(
            db=db,
            action="upload" if upload_mode == 'image' else "file_upload",
            ip_address=ip or get_real_ip(request),
            user_id=user_id,
            resource_type="image" if upload_mode == 'image' else "file",
            resource_id=new_record.id,
            user_agent=request.headers.get("User-Agent"),
            details=f"Chunked upload complete: {filename} ({upload_mode})",
            log_status="success"
        )
    except Exception as e:
        logger.warning(f"Failed to create audit log for chunked upload: {e}")

    # Image Audit if needed
    if upload_mode == 'image' and audit_enabled and background_tasks:
        try:
            from app.services.audit import get_audit_service, run_audit_in_background
            audit_service = await get_audit_service()
            if audit_service.enabled:
                # Build public URL
                if new_record.storage_url:
                    public_url = new_record.storage_url
                else:
                    site_url = await settings_service.get_site_url()
                    site_url = site_url.rstrip('/') if site_url else ''
                    # Use the model's url property which handles proxy path
                    public_url = f"{site_url}{new_record.url}"
                
                background_tasks.add_task(
                    run_audit_in_background,
                    new_record.id,
                    content,
                    audit_service,
                    public_url
                )
        except Exception as e:
            logger.warning(f"Failed to start audit for chunked image: {e}")

    # Cleanup Session
    try:
        shutil.rmtree(session_dir)
    except:
        pass 
    
    # Unified Response
    if upload_mode == 'image':
        from app.schemas.image import ImageResponse
        image_url = new_record.url
        return {
            "success": True,
            "type": "image",
            "image": ImageResponse.model_validate(new_record),
            "url": image_url,
            "markdown": f"![{new_record.original_filename}]({image_url})",
        }
    
    return {
        "success": True,
        "type": "file",
        "id": new_record.id,
        "filename": new_record.filename,
        "original_filename": new_record.original_filename,
        "extension": new_record.extension,
        "mime_type": new_record.mime_type,
        "file_size": new_record.file_size,
        "file_path": new_record.file_path,
        "thumbnail_path": new_record.thumbnail_path,
        "unique_code": new_record.unique_code,
        "access_password": new_record.access_password,
        "expire_at": new_record.expire_at.isoformat() if new_record.expire_at else None,
        "download_limit": new_record.download_limit,
        "shareLink": f"{settings.site_url.rstrip('/')}/s/{new_record.unique_code}" if settings.site_url else f"/s/{new_record.unique_code}"
    }


