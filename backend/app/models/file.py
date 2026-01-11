from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    
    # File info
    filename = Column(String(8), unique=True, index=True, nullable=False)  # Random ID for internal use
    original_filename = Column(String(255), nullable=False)
    extension = Column(String(20), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # In bytes
    file_path = Column(String(500), nullable=False)  # Storage path
    thumbnail_path = Column(String(500), nullable=True)  # Video thumbnail path
    
    # Sharing info
    unique_code = Column(String(20), unique=True, index=True, nullable=False)  # Public sharing code (e.g. 6 chars)
    access_password = Column(String(100), nullable=True)  # Optional password protection
    
    # Storage info
    storage_type = Column(String(20), default="local")
    storage_url = Column(String(500), nullable=True)

    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    collection_id = Column(Integer, ForeignKey("file_collections.id"), nullable=True)
    
    # Limits & Expiration
    download_count = Column(Integer, default=0)
    download_limit = Column(Integer, nullable=True)  # Null means unlimited
    expire_at = Column(DateTime, nullable=True)  # Null means never expire (or subject to global policy)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="files")
    collection = relationship("FileCollection", back_populates="files")

    @property
    def full_filename(self) -> str:
        if self.extension:
            return f"{self.filename}.{self.extension}"
        return self.filename

    @property
    def url(self) -> str:
        """Get storage URL."""
        if self.storage_url:
            return self.storage_url
        return f"/uploads/{self.file_path}"
        
    @property
    def thumbnail_url(self) -> str:
        """Get thumbnail storage URL."""
        if not self.thumbnail_path:
            return None
        # If storage_url ends with something matching file_path, we can replace?
        # Simpler: if local, return path. If remote...
        # For simplicity, assume same base URL structure if remote.
        if self.storage_url:
            # Try to replace file_path with thumbnail_path in storage_url
            # storage_url: https://.../files/2025/.../abc.mp4
            # thumbnail_path: files/2025/.../abc_thumb.jpg
            # This is tricky without knowing base.
            # BUT, we saved thumbnail using same storage backend.
            # Typically user access is via application proxy for local, or direct for cloud.
            pass 
        # For now, let's return None or implement proper logic later if needed for cloud.
        # For LOCAL, we just need the path.
        if self.storage_type == 'local':
             return f"/uploads/{self.thumbnail_path}"
        # For cloud, we might not have a direct URL property stored. 
        # We stored `file_path`.
        return None # Cloud thumbnail URL logic TBD
    
    def __repr__(self):
        return f"<File(id={self.id}, code={self.unique_code})>"
