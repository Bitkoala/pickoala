from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, desc
from app.database import get_db
from app.api.deps import get_admin_user
from app.models.activation_code import ActivationCode, ActivationCodeStatus, ActivationCodeType
from app.models.user import User
from pydantic import BaseModel
from typing import List, Optional
import random
import string
import secrets
from datetime import datetime

router = APIRouter(prefix="/activation", tags=["Admin Activation Codes"])

class GenerateRequest(BaseModel):
    count: int = 1
    duration_days: int = 30
    prefix: str = "VIP"

class ActivationCodeResponse(BaseModel):
    id: int
    code: str
    type: str # VIP
    duration_days: int
    status: str
    created_at: datetime
    used_at: Optional[datetime]
    used_by_user_id: Optional[int]
    used_by_username: Optional[str] = None

    class Config:
        from_attributes = True

def generate_code_string(prefix: str) -> str:
    # Format: PREFIX-XXXX-XXXX-XXXX
    # 3 groups of 4 random chars
    def get_random_string(length):
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    parts = [get_random_string(4) for _ in range(3)]
    suffix = '-'.join(parts)
    if prefix:
        return f"{prefix}-{suffix}"
    return suffix

@router.post("/generate", response_model=List[ActivationCodeResponse])
async def generate_codes(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    if req.count < 1 or req.count > 100:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 100")
    if req.duration_days < 1:
        raise HTTPException(status_code=400, detail="Duration must be positive")

    new_codes = []
    for _ in range(req.count):
        # Retry logic for collisions
        for _ in range(3):
            code_str = generate_code_string(req.prefix)
            # Check exist
            exists = await db.scalar(select(ActivationCode).where(ActivationCode.code == code_str))
            if not exists:
                new_code = ActivationCode(
                    code=code_str,
                    type=ActivationCodeType.VIP,
                    duration_days=req.duration_days,
                    status=ActivationCodeStatus.UNUSED
                )
                db.add(new_code)
                new_codes.append(new_code)
                break
    
    await db.commit()
    for c in new_codes:
        await db.refresh(c)
    return new_codes

@router.get("/list", response_model=dict)
async def list_codes(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    query = select(ActivationCode).options(selectinload(ActivationCode.used_by_user))
    
    if status:
        query = query.where(ActivationCode.status == status)
        
    # Get total
    # Not efficient for huge tables but okay here
    # Use nested await
    result = await db.scalars(query)
    all_items = result.all()
    total = len(all_items)
    
    # Pagination via slicing locally since we fetched all for total (not great for perf but simple fix)
    # OR better: make a separate count query
    # For now let's do the simple fix for the crash first
    
    # Re-query for pagination to be "correct" with SQL or just slice the list?
    # SQLAlchemy scalars() result is consumable.
    # Let's fix loop proper:
    
    query = query.order_by(desc(ActivationCode.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    total_result = await db.scalars(select(ActivationCode)) 
    # That only gets total of ALL, not filtered.
    
    # Correct Async way:
    # 1. Count
    # 2. Paginate
    
    # Simple Count
    # We can't easily do count(*) on query without subquery in new sqlalchemy.
    # Let's just fetch all IDs for count if filtered
    
    if status:
       count_q = select(ActivationCode.id).where(ActivationCode.status == status)
       total = len((await db.scalars(count_q)).all())
    else:
       count_q = select(ActivationCode.id)
       total = len((await db.scalars(count_q)).all())

    # Fetch Page
    codes = (await db.scalars(query)).all()
    
    # Enhance with username if used
    result_list = []
    for c in codes:
        item = ActivationCodeResponse.model_validate(c)
        if c.used_by_user:
            item.used_by_username = c.used_by_user.username
        result_list.append(item)
        
    return {
        "items": result_list,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.delete("/{id}")
async def delete_code(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    code = await db.get(ActivationCode, id)
    if not code:
        raise HTTPException(status_code=404, detail="Code not found")
    
    await db.delete(code)
    await db.commit()
    return {"message": "Deleted"}
