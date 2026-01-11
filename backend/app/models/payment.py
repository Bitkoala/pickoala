from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment Provider Info
    provider = Column(String(20), default="stripe")  # stripe, alipay
    
    # Stripe specific
    stripe_session_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Alipay specific
    out_trade_no = Column(String(64), unique=True, index=True, nullable=True)
    qr_code = Column(String(500), nullable=True)
    plan_type = Column(String(20), default="month", nullable=True) # month, quarter, year, forever
    
    amount = Column(Integer, nullable=False)  # Amount in cents (Stripe) or Yuan (Alipay? converting to cents standard)
    currency = Column(String(10), default="cny")
    status = Column(Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x]), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    user = relationship("User", back_populates="transactions")
