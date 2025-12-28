from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File as FastAPIFile, BackgroundTasks
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import secrets
import os
import tempfile
from app.services.video import video_service

from app.database import get_db
from app.models.file import File as FileModel
from app.models.user import User
from app.schemas.file import FileResponse, FilePublicResponse, FileUpdate
from app.api.deps import get_current_user, get_current_user_optional
from app.services.storage import get_storage_backend_async
from app.utils.rate_limit import get_real_ip
from app.utils.security import generate_random_string
from app.services import settings as settings_service
from app.services import security as security_service

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = FastAPIFile(...),
    password: Optional[str] = None,
    expire_at: Optional[datetime] = None,
    download_limit: Optional[int] = None,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file for sharing.
    """
    ip = get_real_ip(request)
    user_id = user.id if user else None
    
    # Check permissions and bans
    is_banned, ban_reason = await security_service.is_banned(ip, user_id, db)
    if is_banned:
        raise HTTPException(status_code=403, detail=f"Upload banned: {ban_reason}")
        
    if not user and not await settings_service.is_guest_upload_enabled():
        raise HTTPException(status_code=403, detail="Guest upload disabled")

    # Determine upload type (video vs generic file)
    mime_type = file.content_type or "application/octet-stream"
    limit_type = 'file'
    if mime_type.startswith("video/"):
        limit_type = 'video'

    # Rate limiting 
    is_vip = False
    if user and user.vip_expire_at and user.vip_expire_at > datetime.utcnow():
        is_vip = True
        
    is_allowed, _, _ = await security_service.check_rate_limit_multi(
        ip, user_id, is_user=bool(user), is_vip=is_vip, limit_type=limit_type
    )
    if not is_allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Calculate max size logic (separate file limits)
    # Calculate max size logic
    if limit_type == 'video':
        if is_vip:
            max_size = await settings_service.get_max_video_upload_size_vip()
        elif user:
            max_size = await settings_service.get_max_video_upload_size_user()
            if expire_at is None:
                from datetime import timedelta
                expire_at = datetime.utcnow() + timedelta(days=30)
        else:
            max_size = await settings_service.get_max_video_upload_size_guest()
            from datetime import timedelta
            expire_at = datetime.utcnow() + timedelta(days=1)
    else:
        # Generic File Limits
        if is_vip:
            max_size = await settings_service.get_max_file_upload_size_vip()
        elif user:
            max_size = await settings_service.get_max_file_upload_size_user()
            if expire_at is None:
                from datetime import timedelta
                expire_at = datetime.utcnow() + timedelta(days=30)
        else:
            max_size = await settings_service.get_max_file_upload_size_guest()
            from datetime import timedelta
            expire_at = datetime.utcnow() + timedelta(days=1)
        
    # Validate extension
    if limit_type == 'video':
        allowed_extensions = await settings_service.get_video_allowed_extensions()
    else:
        allowed_extensions = await settings_service.get_file_allowed_extensions()
        
    original_filename = file.filename or "unnamed_file"
    ext = original_filename.split(".")[-1].lower() if "." in original_filename else "bin"
    
    if allowed_extensions and ext not in allowed_extensions:
         raise HTTPException(status_code=400, detail=f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}")
        
    # Read file content
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail=f"File too large (limit: {max_size} bytes)")
        
    # Generate unique ID and code
    filename = secrets.token_hex(4) # 8 chars
    unique_code = secrets.token_urlsafe(5) # ~7 chars
    
    # Save to storage
    # We use a separate folder 'files' to check against image uploads
    # Date path is still good for organization
    from app.utils.date_path import get_date_path
    date_path = await get_date_path()
    full_path_prefix = f"files/{date_path}"
    
    final_full_filename = f"{filename}.{ext}"

    storage = await get_storage_backend_async()
    try:
        file_path = await storage.save(content, final_full_filename, full_path_prefix)
    except Exception as e:
        # Log error
        raise HTTPException(status_code=500, detail="Storage saving failed")

    # Video Thumbnail Generation
    thumbnail_path = None
    mime_type = file.content_type or "application/octet-stream"
    
    if mime_type.startswith("video/"):
        try:
            # Create temp video file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_vid:
                tmp_vid.write(content)
                tmp_vid_path = tmp_vid.name
            
            # Create temp thumb file path
            tmp_thumb_path = tmp_vid_path + ".jpg"
            
            # Generate thumbnail
            if video_service.generate_thumbnail(tmp_vid_path, tmp_thumb_path):
                # Upload thumbnail
                with open(tmp_thumb_path, "rb") as f:
                    thumb_content = f.read()
                    thumb_filename = f"{filename}_thumb.jpg"
                    thumbnail_path = await storage.save(thumb_content, thumb_filename, full_path_prefix)
            
            # Clean up
            if os.path.exists(tmp_vid_path):
                os.remove(tmp_vid_path)
            if os.path.exists(tmp_thumb_path):
                os.remove(tmp_thumb_path)
                
        except Exception as e:
            # Log warning but don't fail upload
            print(f"Thumbnail generation failed: {e}")

    # DB Entry
    new_file = FileModel(
        filename=filename,
        original_filename=original_filename,
        extension=ext,
        mime_type=mime_type,
        file_size=len(content),
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
    
    return new_file

@router.get("", response_model=List[FileResponse])
async def list_my_files(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    uncategorized: bool = False,
    type: Optional[str] = None
):
    """List current user's uploaded files."""
    query = select(FileModel).where(FileModel.user_id == user.id)
    
    # Type filter
    if type == "video":
        query = query.where(FileModel.mime_type.like("video/%"))
    elif type == "image":
        query = query.where(FileModel.mime_type.like("image/%"))
    elif type == "audio":
        query = query.where(FileModel.mime_type.like("audio/%"))
    elif type == "other":
        query = query.where(
            ~FileModel.mime_type.like("video/%"),
            ~FileModel.mime_type.like("image/%"),
            ~FileModel.mime_type.like("audio/%")
        )

    # Search filter
    if search:
        from sqlalchemy import or_
        search_term = f"%{search}%"
        query = query.where(
            or_(
                FileModel.original_filename.ilike(search_term),
                FileModel.unique_code.ilike(search_term)
            )
        )
    elif uncategorized:
        query = query.where(FileModel.collection_id.is_(None))
        
    query = query.order_by(FileModel.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/s/{code}", response_model=FilePublicResponse)
async def get_public_file_info(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get public file info by sharing code."""
    query = select(FileModel).where(FileModel.unique_code == code)
    result = await db.execute(query)
    file_obj = result.scalar_one_or_none()
    
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Check expiration
    if file_obj.expire_at and file_obj.expire_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="File link expired")
        
    # Check download limit
    if file_obj.download_limit is not None and file_obj.download_count >= file_obj.download_limit:
        raise HTTPException(status_code=410, detail="Download limit reached")
        
    return file_obj

@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    data: FileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update file details (e.g. add to collection)."""
    query = select(FileModel).where(FileModel.id == file_id, FileModel.user_id == user.id)
    result = await db.execute(query)
    file_obj = result.scalar_one_or_none()
    
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Update fields if set
    if data.collection_id is not None:
        # Verify collection exists and belongs to user
        from app.models.file_collection import FileCollection
        col_result = await db.execute(
            select(FileCollection).where(FileCollection.id == data.collection_id, FileCollection.user_id == user.id)
        )
        if not col_result.scalar_one_or_none():
             raise HTTPException(status_code=404, detail="Collection not found")
        file_obj.collection_id = data.collection_id
        
    if data.access_password is not None:
        file_obj.access_password = data.access_password
        
    if data.expire_at is not None:
        file_obj.expire_at = data.expire_at
        
    if data.download_limit is not None:
        file_obj.download_limit = data.download_limit

    await db.commit()
    await db.refresh(file_obj)
    return file_obj

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file."""
    query = select(FileModel).where(FileModel.id == file_id, FileModel.user_id == user.id)
    result = await db.execute(query)
    file_obj = result.scalar_one_or_none()
    
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Delete from storage (Background task preferred but synchronous for now for simplicity of logic)
    # or just delete from DB and let garbage collector handle it later?
    # Better to try deleting now.
    storage = await get_storage_backend_async()
    try:
        # We need the full path logic from storage backend usually
        # For simplicity, let's assume storage backend can handle the relative path stored in file_path
        await storage.delete(file_obj.file_path) 
    except Exception:
        pass # Log warning
        
    await db.delete(file_obj)
    await db.commit()
    return {"success": True}

@router.get("/d/{code}")
async def download_file(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Download a file (public). Increments download counter."""
    from fastapi.responses import FileResponse, RedirectResponse
    # Use select for update to lock row for counter increment
    query = select(FileModel).where(FileModel.unique_code == code)
    result = await db.execute(query)
    file_obj = result.scalar_one_or_none()
    
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Check checks
    if file_obj.expire_at and file_obj.expire_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="File link expired")
        
    if file_obj.download_limit is not None and file_obj.download_count >= file_obj.download_limit:
        raise HTTPException(status_code=410, detail="Download limit reached")

    # Increment counter
    # Note: For high concurrency, this update might need better locking or atomic update
    # simple increment for now
    file_obj.download_count += 1
    await db.commit()
    
    # Return file
    # If using cloud storage, redirect to signed URL
    if file_obj.storage_type != "local" and file_obj.storage_url:
        return RedirectResponse(url=file_obj.storage_url)
        
    # Local storage
    # file_path in DB is relative e.g. "files/2025/12/28/abc.pdf"
    # We need full path
    settings = settings_service.get_settings()
    full_path = os.path.join(settings.upload_path, file_obj.file_path)
    
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File missing on disk")
        
    return FileResponse(
        full_path, 
        filename=file_obj.original_filename,
        media_type=file_obj.mime_type
    )
