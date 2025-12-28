from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class FileCollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = False
    type: str = "file"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Collection name must be between 1 and 100 characters")
        return v.strip()


class FileCollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Collection name must be between 1 and 100 characters")
        return v.strip()


class FileCollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    description: Optional[str] = None
    is_public: bool
    type: str
    file_count: int
    file_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileCollectionListResponse(BaseModel):
    items: List[FileCollectionResponse]
    total: int
