from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    original_filename: str
    file_size: int
    mime_type: str

class FileCreate(FileBase):
    pass

class FileUpdate(BaseModel):
    access_password: Optional[str] = None
    download_limit: Optional[int] = None
    expire_at: Optional[datetime] = None
    collection_id: Optional[int] = None

class FileResponse(FileBase):
    id: int
    unique_code: str
    download_count: int
    download_limit: Optional[int]
    expire_at: Optional[datetime]
    created_at: datetime
    collection_id: Optional[int] = None
    url: Optional[str] = None # Direct download URL
    thumbnail_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class FilePublicResponse(BaseModel):
    """Minimal info for public download page"""
    unique_code: str
    original_filename: str
    file_size: int
    expire_at: Optional[datetime]
    created_at: datetime
    download_count: int # Maybe hide this for privacy? Keeping for now logic
    has_password: bool = False
    thumbnail_path: Optional[str] = None
    mime_type: Optional[str] = None
    
    class Config:
        from_attributes = True
