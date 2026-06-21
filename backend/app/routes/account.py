from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.models import User, Subscription
from app.database import get_db
from app.schemas import UserResponse, SubscriptionResponse

router = APIRouter(prefix="/account", tags=["account"])


class ProfileUpdateRequest(BaseModel):
    profile_name: Optional[str] = None
    handicap: Optional[int] = None
    height_cm: Optional[int] = None
    preferred_skill_level: Optional[str] = None
    phone_os: Optional[str] = None


@router.get("/{user_id}", response_model=UserResponse)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    """Get a user's profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_profile(user_id: str, request: ProfileUpdateRequest, db: Session = Depends(get_db)):
    """Update a user's profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}/subscription", response_model=SubscriptionResponse)
def get_subscription(user_id: str, db: Session = Depends(get_db)):
    """Get a user's subscription (defaults to free if none exists)."""
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        return SubscriptionResponse(tier="free", expires_at=None, auto_renew=False, payment_method="")
    return sub
