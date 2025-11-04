"""Complaint, Media, and StatusLog models with typed annotations."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from uuid import UUID as UUIDType

if TYPE_CHECKING:
    from app.models.satisfaction_intervention import SatisfactionIntervention


def _get_enum_values(enum_class: type[enum.Enum]) -> list[str]:
    """Get string values from an enum class for SQLAlchemy Enum column."""
    return [e.value for e in enum_class]


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp for SQL defaults."""

    return datetime.now(timezone.utc)


class ComplaintStatus(str, enum.Enum):
    """Complaint status enumeration."""

    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class ComplaintPriority(str, enum.Enum):
    """Complaint priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Complaint(Base):
    """Complaint/Grievance model."""

    __tablename__ = "complaints"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Multi-tenant: Each complaint belongs to one constituency
    constituency_id: Mapped[UUIDType] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True
    )
    
    # Panchayat assignment (for rural complaints - can be assigned to any level)
    gram_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("gram_panchayats.id"), nullable=True, index=True
    )
    taluk_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("taluk_panchayats.id"), nullable=True, index=True
    )
    zilla_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("zilla_panchayats.id"), nullable=True, index=True
    )

    # User who filed the complaint
    user_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Complaint details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Location
    lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=10, scale=7), nullable=True)
    lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=10, scale=7), nullable=True)
    ward_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("wards.id"), nullable=True)
    location_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Assignment and status
    dept_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    suggested_dept_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    citizen_selected_dept: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    assigned_to: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # NEW FLOW: Ward officer who handles complaint before assigning to department
    ward_officer_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    
    # Assignment type: 'ward' (initial), 'department' (after ward assigns)
    # Legacy: 'gram_panchayat', 'taluk_panchayat', 'zilla_panchayat' (kept for backward compatibility)
    assignment_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus, native_enum=False, values_callable=_get_enum_values),
        default=ComplaintStatus.SUBMITTED,
        nullable=False,
    )
    priority: Mapped[ComplaintPriority] = mapped_column(
        Enum(ComplaintPriority, native_enum=False, values_callable=_get_enum_values),
        default=ComplaintPriority.MEDIUM,
        nullable=False,
    )
    priority_score: Mapped[Optional[float]] = mapped_column(Numeric(precision=5, scale=2), nullable=True)
    affected_population_estimate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_complaint_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Voice transcript (if submitted via voice)
    voice_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Work completion approval (Phase 2)
    work_approved: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    approval_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejected_by: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Citizen rating and feedback (Phase 5.5)
    citizen_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    citizen_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating_submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Internal notes for officials (Phase 5.5)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_are_internal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes_updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Public notes (visible to citizens) - meaningful updates from ward/department officers
    public_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="complaints", foreign_keys=[user_id])
    constituency = relationship("Constituency")
    department = relationship("Department", foreign_keys=[dept_id])
    suggested_department = relationship("Department", foreign_keys=[suggested_dept_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    ward_officer = relationship("User", foreign_keys=[ward_officer_id])
    satisfaction_interventions: Mapped[list["SatisfactionIntervention"]] = relationship(
        "SatisfactionIntervention", back_populates="complaint", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Complaint {self.id}: {self.title[:50]}>"


class MediaType(str, enum.Enum):
    """Media type enumeration."""

    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class Media(Base):
    """Media attachments for complaints."""

    __tablename__ = "media"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False)

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType, native_enum=False, validate_strings=True))
    file_size: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # Optional: geo-tag for before/after photos
    lat: Mapped[Optional[float]] = mapped_column(Numeric(precision=10, scale=7), nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Numeric(precision=10, scale=7), nullable=True)

    # For department: mark as 'before' or 'after' proof
    proof_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    photo_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    uploaded_by: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Media {self.media_type}: {self.url}>"


class StatusLog(Base):
    """Status change history for complaints."""

    __tablename__ = "status_logs"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False)

    old_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)

    changed_by: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<StatusLog {self.old_status} → {self.new_status}>"
