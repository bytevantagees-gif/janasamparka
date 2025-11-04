"""Constituency model for multi-tenant support with typed mappings."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from uuid import UUID as UUIDType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Constituency(Base):
    """Tenant model representing an MLA constituency."""

    __tablename__ = "constituencies"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relationships
    users = relationship("User", back_populates="constituency")
    complaints = relationship("Complaint", back_populates="constituency")
    departments = relationship("Department", back_populates="constituency")
    wards = relationship("Ward", back_populates="constituency")
    news = relationship("News", back_populates="constituency")
    schedules = relationship("MLASchedule", back_populates="constituency")

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(100), default="Karnataka")

    mla_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mla_party: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mla_contact_phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    mla_contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    total_population: Mapped[int] = mapped_column(Integer, default=0)
    total_wards: Mapped[int] = mapped_column(Integer, default=0)
    assembly_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Multi-taluk support: One constituency can cover multiple taluks
    # Example: Puttur constituency covers ["Puttur", "Kadaba"]
    taluks: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subscription_tier: Mapped[str] = mapped_column(String(50), default="basic")

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Constituency {self.code}: {self.name}>"
