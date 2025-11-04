"""Department model with typed SQLAlchemy mappings."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from uuid import UUID as UUIDType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Department(Base):
    """Government department model."""

    __tablename__ = "departments"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)

    constituency_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False)
    
    # Link to department type (State-level category)
    department_type_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("department_types.id"), nullable=True, index=True
    )
    
    # Department head officer
    head_officer_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )

    # JURISDICTION: Department belongs to one of these levels (mutually exclusive)
    # This ensures Puttur PWD != Mangalore PWD
    gram_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("gram_panchayats.id"), nullable=True, index=True
    )
    taluk_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("taluk_panchayats.id"), nullable=True, index=True
    )
    zilla_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("zilla_panchayats.id"), nullable=True, index=True
    )
    city_corporation_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True, index=True  # Will link to city_corporations table
    )
    
    contact_phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    office_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    constituency = relationship("Constituency", back_populates="departments")
    department_type = relationship("DepartmentType", back_populates="departments")
    budgets = relationship("DepartmentBudget", back_populates="department")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Department {self.code}: {self.name}>"
