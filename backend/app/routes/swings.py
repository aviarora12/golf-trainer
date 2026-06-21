from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import uuid4

from app.models import Swing, User
from app.database import get_db
from app.services.s3_service import s3_service
from app.tasks.celery_tasks import process_swing_video
from app.schemas import SwingResponse, SwingAnalysisResponse

router = APIRouter(prefix="/swings", tags=["swings"])


@router.post("/upload")
def upload_swing(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a video for analysis."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Upload to S3
    s3_key = f"swings/{user_id}/{uuid4()}.mp4"
    s3_url = s3_service.upload_file(file.file, s3_key)

    # Create Swing record
    swing = Swing(
        user_id=user_id,
        video_s3_url=s3_url,
        analysis_status="processing"
    )
    db.add(swing)
    db.commit()
    db.refresh(swing)

    # Trigger async analysis
    process_swing_video.delay(str(swing.id), s3_url)

    return {
        "swing_id": str(swing.id),
        "status": "processing",
        "message": "Analyzing your swing..."
    }


@router.get("/user/all", response_model=List[SwingResponse])
def list_user_swings(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """List swings for a user (most recent first)."""
    query = db.query(Swing)
    if user_id:
        query = query.filter(Swing.user_id == user_id)
    return query.order_by(Swing.upload_date.desc()).limit(100).all()


@router.get("/{swing_id}/status")
def get_swing_status(swing_id: str, db: Session = Depends(get_db)):
    """Get analysis progress."""
    swing = db.query(Swing).filter(Swing.id == swing_id).first()
    if not swing:
        raise HTTPException(status_code=404, detail="Swing not found")

    return {
        "swing_id": str(swing.id),
        "status": swing.analysis_status,
        "progress": 100 if swing.analysis_status == "complete" else 50
    }


@router.get("/{swing_id}/report", response_model=SwingAnalysisResponse)
def get_swing_report(swing_id: str, db: Session = Depends(get_db)):
    """Get completed analysis report."""
    swing = db.query(Swing).filter(Swing.id == swing_id).first()
    if not swing:
        raise HTTPException(status_code=404, detail="Swing not found")

    if swing.analysis_status != "complete":
        raise HTTPException(status_code=202, detail="Still processing")

    return swing.analysis
