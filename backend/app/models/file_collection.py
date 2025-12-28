from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FileCollection(Base):
    __tablename__ = "file_collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Collection Type (file, video)
    type = Column(String(20), default="file", index=True)

    # Privacy
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="file_collections")
    files = relationship("File", back_populates="collection", lazy="select")

    @property
    def file_count(self) -> int:
        return len(self.files)

    def __repr__(self):
        return f"<FileCollection(id={self.id}, name={self.name})>"
