from abc import ABC, abstractmethod
from typing import Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    async def save(self, content: bytes, filename: str, date_path: Optional[str] = None) -> str:
        """
        Save file to storage.
        
        Args:
            content: File content as bytes
            filename: The filename with extension (e.g., "abc123.png")
            date_path: Optional date path prefix (e.g., "2025/12/14")
                      If provided, file will be stored in date-based folder structure.
        
        Returns:
            The full file_path for database storage (e.g., "2025/12/14/abc123.png")
            or just filename if no date_path provided (backward compatibility).
        """
        pass

    async def save_from_path(self, local_path: str, filename: str, date_path: Optional[str] = None) -> str:
        """
        Save file from local path to storage (Efficient for large files).
        Default implementation reads file into memory and calls save(), 
        subclasses should override this for streaming/multipart upload.
        """
        import aiofiles
        async with aiofiles.open(local_path, 'rb') as f:
            content = await f.read()
        return await self.save(content, filename, date_path)

    
    @abstractmethod
    async def delete(self, filename: str) -> bool:
        """
        Delete file from storage.
        Returns True if successful.
        """
        pass
    
    @abstractmethod
    async def exists(self, filename: str) -> bool:
        """Check if file exists in storage."""
        pass
    
    @abstractmethod
    def get_url(self, filename: str, is_internal: bool = False) -> str:
        """Get the URL for a file. If is_internal=True, return real cloud URL."""
        pass
    
    @property
    @abstractmethod
    def storage_type(self) -> str:
        """Return the storage type identifier."""
        pass
