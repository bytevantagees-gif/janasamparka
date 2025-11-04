"""Ward model with PostGIS support and typed mappings."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from geoalchemy2 import Geometry  # type: ignore[import]
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import Any
from uuid import UUID as UUIDType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Ward(Base):
    """Ward model with geographic boundaries and panchayat/corporation linking."""

    __tablename__ = "wards"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ward_number: Mapped[int] = mapped_column(Integer, nullable=False)
    taluk: Mapped[str] = mapped_column(String(255), nullable=False)

    constituency_id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False)
    
    # Ward type: 'gram_panchayat', 'taluk_panchayat', 'city_corporation', 'municipality'
    ward_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    
    # Link to parent administrative body (only one should be set)
    gram_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("gram_panchayats.id"), nullable=True, index=True
    )
    taluk_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("taluk_panchayats.id"), nullable=True, index=True
    )
    city_corporation_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )

    geom: Mapped[Optional[Any]] = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)  # type: ignore[arg-type]

    population: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    constituency = relationship("Constituency", back_populates="wards")
    budgets = relationship("WardBudget", back_populates="ward")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Ward {self.ward_number}: {self.name} ({self.ward_type})>"

