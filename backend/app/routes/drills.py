from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models import Drill
from app.database import get_db
from app.schemas import DrillResponse

router = APIRouter(prefix="/drills", tags=["drills"])


@router.get("", response_model=List[DrillResponse])
def list_drills(
    category: Optional[str] = None,
    issue_tag: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List drills, optionally filtered by category or issue tag."""
    query = db.query(Drill)
    if category:
        query = query.filter(Drill.category == category)
    drills = query.all()

    if issue_tag:
        drills = [d for d in drills if d.issue_tags and issue_tag in d.issue_tags]

    return drills


@router.get("/{drill_id}", response_model=DrillResponse)
def get_drill(drill_id: str, db: Session = Depends(get_db)):
    """Get a single drill by id."""
    from fastapi import HTTPException

    drill = db.query(Drill).filter(Drill.id == drill_id).first()
    if not drill:
        raise HTTPException(status_code=404, detail="Drill not found")
    return drill
