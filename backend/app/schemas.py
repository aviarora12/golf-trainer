from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Auth
class SignupRequest(BaseModel):
    email: EmailStr

class MagicLinkVerifyRequest(BaseModel):
    email: EmailStr
    token: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    profile_name: Optional[str]
    handicap: Optional[int]
    preferred_skill_level: str

    class Config:
        from_attributes = True

# Swings
class SwingResponse(BaseModel):
    id: UUID
    user_id: UUID
    upload_date: datetime
    analysis_status: str
    skill_level_estimate: Optional[str]

    class Config:
        from_attributes = True

class SwingAnalysisResponse(BaseModel):
    swing_id: UUID
    spine_angle_setup_deg: Optional[float]
    spine_angle_impact_deg: Optional[float]
    hip_turn_top_deg: Optional[float]
    shoulder_turn_top_deg: Optional[float]
    x_factor_deg: Optional[float]
    shaft_lean_impact_deg: Optional[float]
    early_extension_flag: bool
    reverse_pivot_flag: bool
    sway_flag: bool
    over_the_top_flag: bool
    casting_flag: bool
    chicken_wing_flag: bool
    flagged_issues: List[dict]
    estimated_club_speed_mph: Optional[int]
    detected_camera_angle: str
    confidence_score: float

    class Config:
        from_attributes = True

# Drills
class DrillResponse(BaseModel):
    id: UUID
    name: str
    category: str
    description: str
    video_url: str
    difficulty: str
    reps_sets: str
    issue_tags: List[str]

    class Config:
        from_attributes = True

# Subscription
class SubscriptionResponse(BaseModel):
    tier: str
    expires_at: Optional[datetime]
    auto_renew: bool
    payment_method: str

    class Config:
        from_attributes = True
