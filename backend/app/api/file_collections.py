from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.file_collection import FileCollection
from app.models.file import File
from app.schemas.file_collection import FileCollectionCreate, FileCollectionUpdate, FileCollectionResponse, FileCollectionListResponse
from app.api.deps import get_current_user
from app.services.storage import get_storage_backend_async

router = APIRouter(prefix="/file-collections", tags=["File Collections"])


@router.get("", response_model=FileCollectionListResponse)
async def get_my_collections(
    type: str = "file",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's file collections."""
    result = await db.execute(
        select(FileCollection)
        .where(
            FileCollection.user_id == user.id,
            FileCollection.type == type
        )
        .options(selectinload(FileCollection.files))
        .order_by(FileCollection.created_at.desc())
    )
    collections = result.scalars().all()
    
    return FileCollectionListResponse(
        items=[FileCollectionResponse.model_validate(c) for c in collections],
        total=len(collections),
    )


@router.post("", response_model=FileCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    data: FileCollectionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new file collection."""
    # Check if collection name already exists for this user AND type
    result = await db.execute(
        select(FileCollection).where(
            FileCollection.user_id == user.id, 
            FileCollection.name == data.name,
            FileCollection.type == data.type
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection with this name already exists"
        )
    
    collection = FileCollection(
        name=data.name,
        description=data.description,
        is_public=data.is_public,
        type=data.type,
        user_id=user.id,
    )
    
    db.add(collection)
    await db.commit()
    
    # Reload with files relationship for file_count property
    result = await db.execute(
        select(FileCollection)
        .where(FileCollection.id == collection.id)
        .options(selectinload(FileCollection.files))
    )
    collection = result.scalar_one()
    
    return FileCollectionResponse.model_validate(collection)


@router.get("/{collection_id}", response_model=FileCollectionResponse)
async def get_collection(
    collection_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get collection details."""
    result = await db.execute(
        select(FileCollection)
        .where(FileCollection.id == collection_id, FileCollection.user_id == user.id)
        .options(selectinload(FileCollection.files))
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    return FileCollectionResponse.model_validate(collection)


@router.put("/{collection_id}", response_model=FileCollectionResponse)
async def update_collection(
    collection_id: int,
    data: FileCollectionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update collection."""
    result = await db.execute(
        select(FileCollection)
        .where(FileCollection.id == collection_id, FileCollection.user_id == user.id)
        .options(selectinload(FileCollection.files))
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check if new name conflicts
    if data.name and data.name != collection.name:
        name_check = await db.execute(
            select(FileCollection).where(
                FileCollection.user_id == user.id, 
                FileCollection.name == data.name,
                FileCollection.type == collection.type,
                FileCollection.id != collection_id
            )
        )
        if name_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Collection with this name already exists"
            )
        collection.name = data.name
    
    if data.description is not None:
        collection.description = data.description
    
    if data.is_public is not None:
        collection.is_public = data.is_public
    
    await db.commit()
    
    # Reload
    result = await db.execute(
        select(FileCollection)
        .where(FileCollection.id == collection_id)
        .options(selectinload(FileCollection.files))
    )
    collection = result.scalar_one()
    
    return FileCollectionResponse.model_validate(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: int,
    delete_files: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete collection.
    If delete_files is True, also delete all files in the collection.
    Otherwise, files are moved out of the collection (collection_id set to NULL).
    """
    result = await db.execute(
        select(FileCollection)
        .where(FileCollection.id == collection_id, FileCollection.user_id == user.id)
        .options(selectinload(FileCollection.files))
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    if delete_files:
        storage = await get_storage_backend_async()
        for file in collection.files:
            # Assuming file.file_path is sufficient (similar to Album logic)
            # But File model uses /uploads/files/... prefix in URL logic.
            # Storage backend usually expects relative path.
            # file.file_path is stored as "dir/filename.ext" or just filename
            await storage.delete(f"files/{file.file_path}" if not file.file_path.startswith("files/") else file.file_path)
            await db.delete(file)
    else:
        for file in collection.files:
            file.collection_id = None
    
    await db.delete(collection)
    await db.commit()


@router.get("/{collection_id}/files")
async def get_collection_files(
    collection_id: int,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get files in a collection."""
    # Verify ownership
    result = await db.execute(
        select(FileCollection).where(FileCollection.id == collection_id, FileCollection.user_id == user.id)
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Build query
    query = select(File).where(File.collection_id == collection_id)
    
    # Sorting
    sort_column = File.created_at
    if sort_by == "file_size":
        sort_column = File.file_size
    
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    files_result = await db.execute(query)
    files = files_result.scalars().all()
    
    # We don't have a FileResponse schema yet that is generic enough or we use the one from files.py?
    # Let's import FileResponse from app.schemas.file (need to check if it exists or define a local one/new one)
    # Checking existing schemas first.
    from app.schemas.file import FileResponse
    
    return {
        "items": [FileResponse.model_validate(f) for f in files],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
