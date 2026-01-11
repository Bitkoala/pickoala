from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, UserStatus
import re


# Reserved usernames that are not allowed
RESERVED_USERNAMES = {
    'root', 'admin', 'administrator', 'system', 'sysadmin', 
    'support', 'help', 'service', 'guest', 'visitor',
    'test', 'tester', 'demo', 'dev',
    'null', 'undefined', 'none', 'empty',
    'api', 'bot', 'crawler', 'spider', 'mailer', 'daemon',
    'superuser', 'operator', 'manager',
    'picpanda', 'pickoala', 'official', 'master'
}


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        
        # Check reserved usernames
        if v.lower() in RESERVED_USERNAMES:
            raise ValueError("This username is reserved and cannot be used")
            
        # Check for reserved patterns (e.g. starts with admin_)
        if v.lower().startswith(('admin', 'system', 'root')):
            raise ValueError("Username cannot start with reserved keywords")
            
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    status: UserStatus
    email_verified: bool
    vip_expire_at: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    # Watermark Settings
    watermark_enabled: bool = False
    watermark_type: str = "text"
    watermark_text: Optional[str] = None
    watermark_image_path: Optional[str] = None
    watermark_opacity: int = 50
    watermark_position: str = "bottom-right"

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    vip_expire_at: Optional[datetime] = None
    
    # Watermark Settings
    watermark_enabled: Optional[bool] = None
    watermark_type: Optional[str] = None
    watermark_text: Optional[str] = None
    watermark_image_path: Optional[str] = None
    watermark_opacity: Optional[int] = None
    watermark_position: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
            
        # Check reserved usernames
        if v.lower() in RESERVED_USERNAMES:
            raise ValueError("This username is reserved and cannot be used")
            
        # Check forbidden prefixes
        if v.lower().startswith(('admin', 'system', 'root')):
            raise ValueError("Username cannot start with reserved keywords")
            
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
