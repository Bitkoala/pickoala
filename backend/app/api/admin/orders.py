from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User
from app.models.payment import PaymentTransaction, PaymentStatus
from sqlalchemy.orm import selectinload

router = APIRouter()

class OrderUserSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    id: int
    out_trade_no: Optional[str]
    stripe_session_id: Optional[str]
    amount: float
    currency: str
    status: str
    provider: str
    plan_type: Optional[str]
    created_at: datetime
    user: OrderUserSchema

    class Config:
        from_attributes = True

class OrdersListResponse(BaseModel):
    items: List[OrderSchema]
    total: int
    page: int
    size: int

@router.get("/orders", response_model=OrdersListResponse)
async def get_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get paginated list of orders (payment transactions).
    """
    query = select(PaymentTransaction).options(selectinload(PaymentTransaction.user)).join(User)

    # Filters
    if status and status != 'all':
        query = query.where(PaymentTransaction.status == status)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                PaymentTransaction.out_trade_no.ilike(search_term),
                PaymentTransaction.stripe_session_id.ilike(search_term)
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Pagination
    query = query.order_by(desc(PaymentTransaction.created_at))
    query = query.offset((page - 1) * size).limit(size)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Process amounts (cents/raw to display) if needed, but simplistic mapping here
    # Assuming amount in DB is accurate (e.g. 99.99 or 9999). 
    # Current logic stores as is.

    return {
        "items": orders,
        "total": total,
        "page": page,
        "size": size
    }
