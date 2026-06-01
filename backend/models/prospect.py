from sqlalchemy import Column, String, JSON, DateTime, Enum as SAEnum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from .campaign import Base
import uuid
import enum


class ProspectStatus(str, enum.Enum):
    queued = "queued"
    researched = "researched"
    message_ready = "message_ready"
    sent = "sent"
    replied = "replied"
    lead = "lead"
    unsubscribed = "unsubscribed"


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    title = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    apollo_id = Column(String, nullable=True)
    research = Column(JSON, nullable=True)       # triggers found: posts, events, etc.
    generated_message = Column(Text, nullable=True)
    status = Column(SAEnum(ProspectStatus, name="prospect_status", create_type=False), default=ProspectStatus.queued)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
