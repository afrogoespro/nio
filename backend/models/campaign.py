from sqlalchemy import Column, String, JSON, Integer, DateTime, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone
import uuid
import enum


class Base(DeclarativeBase):
    pass


class CampaignStatus(str, enum.Enum):
    onboarding = "onboarding"
    active = "active"
    paused = "paused"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    business_description = Column(Text, nullable=False)
    target_description = Column(Text, nullable=False)
    goal = Column(Text, nullable=False)
    tone = Column(String, nullable=False)
    icp = Column(JSON, nullable=True)  # derived by Claude
    status = Column(SAEnum(CampaignStatus, name="campaign_status", create_type=False), default=CampaignStatus.onboarding)
    sends_per_hour = Column(Integer, default=4)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_run_at = Column(DateTime(timezone=True), nullable=True)
