"""
Satisfaction Intervention Model
Tracks moderator interventions with unhappy citizens
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from datetime import datetime
from uuid import uuid4

from app.core.database import Base


class SatisfactionIntervention(Base):
    """Model for tracking moderator interventions with unhappy citizens"""
    
    __tablename__ = "satisfaction_interventions"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign Keys
    complaint_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    citizen_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    moderator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    
    # Intervention Details
    intervention_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="Type: call, visit, follow-up")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Moderator notes about intervention plan")
    
    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="When intervention is scheduled")
    
    # Completion
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="When intervention was completed")
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Outcome: resolved, escalated, pending")
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Notes after completing intervention")
    citizen_now_happy: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, comment="Whether citizen is satisfied after intervention")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="satisfaction_interventions")
    citizen: Mapped["User"] = relationship("User", foreign_keys=[citizen_id], backref="citizen_interventions")
    moderator: Mapped["User"] = relationship("User", foreign_keys=[moderator_id], backref="moderator_interventions")
    
    def __repr__(self) -> str:
        return f"<SatisfactionIntervention(id={self.id}, type={self.intervention_type}, outcome={self.outcome})>"
