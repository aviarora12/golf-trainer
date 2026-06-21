from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    profile_name = Column(String(255))
    handicap = Column(Integer)
    height_cm = Column(Integer)
    preferred_skill_level = Column(String(50), default="intermediate")  # beginner|intermediate|advanced
    phone_os = Column(String(50))  # iOS|Android
    magic_link_token = Column(String(255))
    magic_link_expires_at = Column(DateTime)
    is_verified = Column(Boolean, default=False)

    swings = relationship("Swing", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Swing(Base):
    __tablename__ = "swings"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_s3_url = Column(String(500))
    video_duration_sec = Column(Float)
    upload_date = Column(DateTime, default=datetime.utcnow, index=True)
    analysis_status = Column(String(50), default="processing", index=True)  # processing|complete|failed
    analysis_json = Column(JSON)  # Stores computed angles, flags, etc.
    report_pdf_url = Column(String(500))
    skill_level_estimate = Column(String(50))
    error_message = Column(Text)
    processed_at = Column(DateTime)

    user = relationship("User", back_populates="swings")
    analysis = relationship("SwingAnalysis", back_populates="swing", uselist=False, cascade="all, delete-orphan")


class SwingAnalysis(Base):
    __tablename__ = "swing_analysis"

    swing_id = Column(PG_UUID(as_uuid=True), ForeignKey("swings.id", ondelete="CASCADE"), primary_key=True)
    spine_angle_setup_deg = Column(Float)
    spine_angle_impact_deg = Column(Float)
    hip_turn_top_deg = Column(Float)
    shoulder_turn_top_deg = Column(Float)
    x_factor_deg = Column(Float)
    shaft_lean_impact_deg = Column(Float)
    weight_forward_pct = Column(Integer)
    lag_angle_estimate_deg = Column(Float)
    # Flag booleans
    early_extension_flag = Column(Boolean, default=False)
    reverse_pivot_flag = Column(Boolean, default=False)
    sway_flag = Column(Boolean, default=False)
    over_the_top_flag = Column(Boolean, default=False)
    casting_flag = Column(Boolean, default=False)
    chicken_wing_flag = Column(Boolean, default=False)
    flagged_issues = Column(JSON)  # [{issue, severity: green|yellow|red, description, drills: []}]
    estimated_club_speed_mph = Column(Integer)
    detected_camera_angle = Column(String(50))  # down-the-line|face-on|unknown
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    swing = relationship("Swing", back_populates="analysis")


class Drill(Base):
    __tablename__ = "drills"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), index=True)  # mobility|setup|swing|lag|rhythm
    issue_tags = Column(JSON)  # ["Early Extension", "Reverse Pivot"]
    description = Column(Text)
    video_url = Column(String(500))
    difficulty = Column(String(50))  # beginner|intermediate|advanced
    reps_sets = Column(String(100))  # "10 x 3" or "5 min"
    key_feeling = Column(Text)
    handicap_min = Column(Integer)
    handicap_max = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    tier = Column(String(50), default="free")  # free|premium|pro
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True)
    auto_renew = Column(Boolean, default=False)
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    payment_method = Column(String(50))  # stripe|apple|google
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="subscription")
