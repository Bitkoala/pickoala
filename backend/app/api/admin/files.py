from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, or_
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.file import File
from app.api.deps import get_admin_user
from app.services.storage import get_storage_backend_async
from app.api.admin.audit import create_audit_log
from app.utils.rate_limit import get_real_ip

router = APIRouter(prefix="/files")


class AdminFileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    extension: str
    mime_type: str
    file_size: int
    file_path: str
    thumbnail_path: Optional[str] = None
    
    # Sharing
    unique_code: str
    access_password: Optional[str] = None
    
    # Limits
    download_count: int
    download_limit: Optional[int]
    expire_at: Optional[datetime]
    
    storage_type: str
    created_at: datetime
    
    # User info
    user_id: Optional[int]
    username: Optional[str] = None

    class Config:
        from_attributes = True


class AdminFileListResponse(BaseModel):
    items: List[AdminFileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("", response_model=AdminFileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = Query(None, description="'video' or 'other'"),
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all files with filtering."""
    query = select(File, User.username).outerjoin(User, File.user_id == User.id)
    
    if file_type == 'video':
        query = query.where(File.mime_type.like("video/%"))
    elif file_type == 'other':
        query = query.where(File.mime_type.notlike("video/%"))
    
    if user_id:
        query = query.where(File.user_id == user_id)
    
    if search:
        query = query.where(
            File.filename.ilike(f"%{search}%") | 
            File.original_filename.ilike(f"%{search}%") |
            File.unique_code.ilike(f"%{search}%")
        )
    
    # Count total
    count_query = select(func.count()).select_from(File)
    if file_type == 'video':
        count_query = count_query.where(File.mime_type.like("video/%"))
    elif file_type == 'other':
        count_query = count_query.where(File.mime_type.notlike("video/%"))
    
    if user_id:
        count_query = count_query.where(File.user_id == user_id)
    if search:
        count_query = count_query.where(
            File.filename.ilike(f"%{search}%") | 
            File.original_filename.ilike(f"%{search}%") |
            File.unique_code.ilike(f"%{search}%")
        )
        
    total = (await db.execute(count_query)).scalar()
    
    # Paginate
    query = query.order_by(File.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    rows = result.all()
    
    items = []
    for file_obj, username in rows:
        item = AdminFileResponse.model_validate(file_obj)
        item.username = username
        items.append(item)
    
    return AdminFileListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    request: Request,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a file."""
    result = await db.execute(select(File).where(File.id == file_id))
    file_obj = result.scalar_one_or_none()
    
    if not file_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete from storage
    storage = await get_storage_backend_async()
    
    # 1. Delete main file
    if file_obj.file_path:
        await storage.delete(file_obj.file_path)
        
    # 2. Delete thumbnail if exists
    if file_obj.thumbnail_path:
        await storage.delete(file_obj.thumbnail_path)
    
    # Delete from database
    await db.delete(file_obj)
    await db.commit()
    
    # Audit log
    ip = get_real_ip(request)
    await create_audit_log(
        db=db,
        action="admin_delete",
        ip_address=ip,
        user_id=admin.id,
        resource_type="file",
        resource_id=file_id,
        user_agent=request.headers.get("User-Agent"),
        details=f"Admin deleted file: {file_obj.original_filename}",
        log_status="success"
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete_files(
    request: Request,
    file_ids: List[int] = Query(...),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple files."""
    result = await db.execute(select(File).where(File.id.in_(file_ids)))
    files = result.scalars().all()
    
    if not files:
        return

    storage = await get_storage_backend_async()
    
    for file_obj in files:
        if file_obj.file_path:
            await storage.delete(file_obj.file_path)
        if file_obj.thumbnail_path:
            await storage.delete(file_obj.thumbnail_path)
    
    # Delete from database
    await db.execute(delete(File).where(File.id.in_([f.id for f in files])))
    await db.commit()

    # Audit log (summary)
    ip = get_real_ip(request)
    await create_audit_log(
        db=db,
        action="admin_batch_delete",
        ip_address=ip,
        user_id=admin.id,
        resource_type="file",
        resource_id=0, 
        user_agent=request.headers.get("User-Agent"),
        details=f"Admin batch deleted {len(files)} files",
        log_status="success"
    )
