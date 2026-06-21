from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.schemas import SignupRequest, MagicLinkVerifyRequest, UserResponse
from app.models import User
from app.database import get_db
from app.services.email_service import send_magic_link_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Send magic link to email."""
    user = db.query(User).filter(User.email == request.email).first()

    token = secrets.token_urlsafe(32)

    if not user:
        user = User(
            email=request.email,
            magic_link_token=token,
            magic_link_expires_at=datetime.utcnow() + timedelta(hours=24),
            is_verified=False
        )
        db.add(user)
    else:
        user.magic_link_token = token
        user.magic_link_expires_at = datetime.utcnow() + timedelta(hours=24)

    db.commit()

    send_magic_link_email(user.email, token)

    return {"message": "Magic link sent", "email": user.email}


@router.post("/verify-magic-link")
def verify_magic_link(request: MagicLinkVerifyRequest, db: Session = Depends(get_db)):
    """Verify magic link token."""
    user = db.query(User).filter(User.email == request.email).first()

    if not user or user.magic_link_token != request.token:
        raise HTTPException(status_code=400, detail="Invalid token")

    if not user.magic_link_expires_at or datetime.utcnow() > user.magic_link_expires_at:
        raise HTTPException(status_code=400, detail="Token expired")

    user.is_verified = True
    user.magic_link_token = None
    db.commit()
    db.refresh(user)

    # TODO: generate a real JWT token (Phase 2)
    access_token = "placeholder_jwt_token"

    return {
        "access_token": access_token,
        "user": UserResponse.model_validate(user)
    }
