"""User model with typed SQLAlchemy mappings."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from uuid import UUID as UUIDType


def _get_enum_values(enum_class: type[enum.Enum]) -> list[str]:
    """Get string values from an enum class for SQLAlchemy Enum column."""
    return [e.value for e in enum_class]


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp for SQL defaults."""

    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    """User role enumeration."""

    CITIZEN = "citizen"
    MODERATOR = "moderator"
    MLA = "mla"
    DEPARTMENT_OFFICER = "department_officer"
    AUDITOR = "auditor"
    ADMIN = "admin"
    
    # Ward Officer - handles complaints at ward level before assigning to departments
    WARD_OFFICER = "ward_officer"
    
    # Panchayat Raj roles
    PDO = "pdo"                              # Panchayat Development Officer (Gram Panchayat)
    VILLAGE_ACCOUNTANT = "village_accountant"  # VA - Village Accountant (Gram Panchayat)
    TALUK_PANCHAYAT_OFFICER = "taluk_panchayat_officer"  # Taluk Panchayat Officer
    ZILLA_PANCHAYAT_OFFICER = "zilla_panchayat_officer"  # Zilla Panchayat Officer
    GP_PRESIDENT = "gp_president"            # Gram Panchayat President (elected)
    TP_PRESIDENT = "tp_president"            # Taluk Panchayat President (elected)
    ZP_PRESIDENT = "zp_president"            # Zilla Panchayat President (elected)


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, values_callable=_get_enum_values),
        default=UserRole.CITIZEN,
        nullable=False,
    )
    locale_pref: Mapped[str] = mapped_column(String(5), default="kn")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Geographic assignment
    constituency_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=True)
    
    # Ward assignment (for ward officers)
    ward_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("wards.id"), nullable=True)
    
    # Panchayat assignment (for Panchayat Raj officials)
    gram_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("gram_panchayats.id"), nullable=True)
    taluk_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("taluk_panchayats.id"), nullable=True)
    zilla_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("zilla_panchayats.id"), nullable=True)
    
    # Department assignment (for department officers)
    department_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    complaints = relationship("Complaint", back_populates="user", foreign_keys="Complaint.user_id")
    constituency = relationship("Constituency", back_populates="users")
    department = relationship("Department", foreign_keys="User.department_id")
    news_posts = relationship("News", foreign_keys="News.mla_id")
    
    # Citizen engagement relationships
    feedback_submissions = relationship("CitizenFeedback", foreign_keys="CitizenFeedback.citizen_id", back_populates="citizen")
    assigned_feedback = relationship("CitizenFeedback", foreign_keys="CitizenFeedback.assigned_to", back_populates="assigned_user")
    hosted_conferences = relationship("VideoConference", back_populates="host")
    broadcasts = relationship("ScheduledBroadcast", foreign_keys="ScheduledBroadcast.sender_id", back_populates="sender")
    
    # Votebank engagement relationships
    farmer_profile = relationship("FarmerProfile", back_populates="farmer", uselist=False)
    business_profile = relationship("BusinessProfile", back_populates="owner", uselist=False)
    youth_profile = relationship("YouthProfile", back_populates="youth", uselist=False)
    organized_programs = relationship("YouthProgram", back_populates="organizer")
    conducted_trainings = relationship("TrainingProgram", back_populates="trainer")
    mentorship_connections = relationship("MentorshipConnection", back_populates="mentor")
    career_guidance = relationship("CareerRequest", back_populates="mentor")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.name} ({self.phone})>"
