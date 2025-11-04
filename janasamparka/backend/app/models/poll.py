"""
Poll, PollOption, and Vote models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Poll(Base):
    """Poll model for collecting citizen feedback"""
    __tablename__ = "polls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Multi-tenant: Each poll belongs to one constituency
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Ward-specific or constituency-wide
    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id"))
    
    # Creator (usually MLA office or admin)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Poll duration
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Poll {self.title[:50]}>"


class PollOption(Base):
    """Poll options/choices"""
    __tablename__ = "poll_options"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    poll_id = Column(UUID(as_uuid=True), ForeignKey("polls.id"), nullable=False)
    
    option_text = Column(String(500), nullable=False)
    vote_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PollOption {self.option_text[:30]} ({self.vote_count} votes)>"


class Vote(Base):
    """User votes for polls"""
    __tablename__ = "votes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    poll_id = Column(UUID(as_uuid=True), ForeignKey("polls.id"), nullable=False)
    option_id = Column(UUID(as_uuid=True), ForeignKey("poll_options.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    voted_at = Column(DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per poll
    __table_args__ = (
        UniqueConstraint('poll_id', 'user_id', name='uq_poll_user_vote'),
    )
    
    def __repr__(self):
        return f"<Vote poll={self.poll_id} user={self.user_id}>"
