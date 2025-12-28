from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.api.deps import get_current_user
from app.models.activation_code import ActivationCode, ActivationCodeStatus
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/activation", tags=["Activation"])

class RedeemRequest(BaseModel):
    code: str

@router.post("/redeem")
async def redeem_code(
    req: RedeemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Find Code
    code = db.scalar(
        select(ActivationCode).where(ActivationCode.code == req.code)
    )
    
    if not code:
        raise HTTPException(status_code=404, detail="Invalid activation code")
        
    if code.status != ActivationCodeStatus.UNUSED:
        raise HTTPException(status_code=400, detail="Code already used")
        
    # 2. Redeem
    now = datetime.now()
    code.status = ActivationCodeStatus.USED
    code.used_at = now
    code.used_by_user_id = current_user.id
    
    # 3. Add to User
    # Default duration in code is days
    days = code.duration_days
    
    if current_user.vip_expire_at and current_user.vip_expire_at > now:
        # Extend
        current_user.vip_expire_at += timedelta(days=days)
    else:
        # New
        current_user.vip_expire_at = now + timedelta(days=days)
        
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Activation successful",
        "vip_expire_at": current_user.vip_expire_at
    }
