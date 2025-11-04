"""Case Notes and Department Routing models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from uuid import UUID as UUIDType


def _get_enum_values(enum_class: type[enum.Enum]) -> list[str]:
    """Get string values from an enum class for SQLAlchemy Enum column."""
    return [e.value for e in enum_class]


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp for SQL defaults."""
    return datetime.now(timezone.utc)


class NoteType(str, enum.Enum):
    """Case note type enumeration."""
    
    GENERAL = "general"
    STATUS_UPDATE = "status_update"
    DEPARTMENT_ROUTING = "department_routing"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    WORK_UPDATE = "work_update"


class CaseNote(Base):
    """Case notes for complaints - tracks all communication and updates."""
    
    __tablename__ = "case_notes"
    
    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False, index=True)
    
    # Note details
    note: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[NoteType] = mapped_column(
        Enum(NoteType, native_enum=False, values_callable=_get_enum_values),
        default=NoteType.GENERAL,
        nullable=False,
    )
    
    # Author
    created_by: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Visibility - can be internal (staff only) or public (visible to citizen)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Resets idle timer for case aging
    resets_idle_timer: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<CaseNote {self.id}: {self.note_type}>"


class RoutingReason(str, enum.Enum):
    """Reason for department routing."""
    
    INCORRECT_DEPARTMENT = "incorrect_department"
    BETTER_SUITED = "better_suited"
    SPECIALIZED_TEAM = "specialized_team"
    JURISDICTION = "jurisdiction"
    OTHER = "other"


class DepartmentRouting(Base):
    """Track department routing history for complaints."""
    
    __tablename__ = "department_routing"
    
    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False, index=True)
    
    # Routing details
    from_dept_id: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    to_dept_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    
    reason: Mapped[RoutingReason] = mapped_column(
        Enum(RoutingReason, native_enum=False, values_callable=_get_enum_values),
        nullable=False,
    )
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Who routed it
    routed_by: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    routed_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, index=True)
    
    # Was this routing accepted by the new department?
    accepted: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    accepted_by: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<DepartmentRouting {self.from_dept_id} → {self.to_dept_id}>"


class EscalationReason(str, enum.Enum):
    """Reason for escalating to MLA."""
    
    INCORRECTLY_CLOSED = "incorrectly_closed"
    WRONGLY_ROUTED = "wrongly_routed"
    NO_PROGRESS_UPDATE = "no_progress_update"
    DELAYED_RESOLUTION = "delayed_resolution"
    POOR_QUALITY_WORK = "poor_quality_work"
    UNRESPONSIVE = "unresponsive"
    OTHER = "other"


class ComplaintEscalation(Base):
    """Escalations to MLA by citizens."""
    
    __tablename__ = "complaint_escalations"
    
    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False, index=True)
    
    # Escalation details
    reason: Mapped[EscalationReason] = mapped_column(
        Enum(EscalationReason, native_enum=False, values_callable=_get_enum_values),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Who escalated (should be the complaint creator)
    escalated_by: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Resolution
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[Optional[UUIDType]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<ComplaintEscalation {self.id}: {self.reason}>"
