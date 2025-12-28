from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class ActivationCodeStatus(str, enum.Enum):
    UNUSED = "unused"
    USED = "used"

class ActivationCodeType(str, enum.Enum):
    VIP = "vip"

class ActivationCode(Base):
    __tablename__ = "activation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(
        SQLEnum(ActivationCodeType, values_callable=lambda x: [e.value for e in x]),
        default=ActivationCodeType.VIP,
        nullable=False
    )
    # Duration in days usually, but lets just call it value or duration
    # For VIP, it's duration in days.
    duration_days = Column(Integer, nullable=False)
    
    status = Column(
        SQLEnum(ActivationCodeStatus, values_callable=lambda x: [e.value for e in x]),
        default=ActivationCodeStatus.UNUSED,
        nullable=False
    )
    
    created_at = Column(DateTime, server_default=func.now())
    used_at = Column(DateTime, nullable=True)
    
    used_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    used_by_user = relationship("User", backref="used_activation_codes")

    def __repr__(self):
        return f"<ActivationCode(code={self.code}, status={self.status})>"
