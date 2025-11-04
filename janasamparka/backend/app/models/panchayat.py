"""Panchayat models for 3-tier Panchayat Raj system."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
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


class PanchayatType(str, enum.Enum):
    """Panchayat type enumeration for 3-tier system."""

    GRAM = "gram"              # Village Panchayat (lowest tier)
    TALUK = "taluk"            # Taluk/Block Panchayat (middle tier)
    ZILLA = "zilla"            # District Panchayat (highest tier)


class GramPanchayat(Base):
    """
    Gram Panchayat (Village Panchayat) - Lowest tier.
    Serves a village or group of villages.
    """

    __tablename__ = "gram_panchayats"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Hierarchy
    taluk_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("taluk_panchayats.id"), nullable=True
    )
    constituency_id: Mapped[UUIDType] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True
    )

    # Location
    taluk_name: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="Karnataka")

    # Demographics
    population: Mapped[int] = mapped_column(Integer, default=0)
    households: Mapped[int] = mapped_column(Integer, default=0)
    villages_covered: Mapped[int] = mapped_column(Integer, default=1)

    # Administration
    president_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vice_president_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    secretary_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Contact
    office_phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    office_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    office_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    taluk_panchayat: Mapped[Optional["TalukPanchayat"]] = relationship(
        "TalukPanchayat", back_populates="gram_panchayats", foreign_keys=[taluk_panchayat_id]
    )
    constituency = relationship(
        "Constituency", foreign_keys=[constituency_id]
    )

    def __repr__(self) -> str:
        return f"<GramPanchayat {self.code}: {self.name}>"


class TalukPanchayat(Base):
    """
    Taluk Panchayat (Block/Mandal Panchayat) - Middle tier.
    Coordinates multiple Gram Panchayats within a taluk.
    """

    __tablename__ = "taluk_panchayats"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Hierarchy
    zilla_panchayat_id: Mapped[Optional[UUIDType]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("zilla_panchayats.id"), nullable=True
    )
    constituency_id: Mapped[UUIDType] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True
    )

    # Location
    taluk_name: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="Karnataka")

    # Demographics
    total_gram_panchayats: Mapped[int] = mapped_column(Integer, default=0)
    total_population: Mapped[int] = mapped_column(Integer, default=0)

    # Administration
    president_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    executive_officer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Contact
    office_phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    office_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    office_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    zilla_panchayat: Mapped[Optional["ZillaPanchayat"]] = relationship(
        "ZillaPanchayat", back_populates="taluk_panchayats", foreign_keys=[zilla_panchayat_id]
    )
    constituency = relationship(
        "Constituency", foreign_keys=[constituency_id]
    )
    gram_panchayats = relationship(
        "GramPanchayat", back_populates="taluk_panchayat"
    )

    def __repr__(self) -> str:
        return f"<TalukPanchayat {self.code}: {self.name}>"


class ZillaPanchayat(Base):
    """
    Zilla Panchayat (District Panchayat) - Highest tier.
    Oversees all Taluk Panchayats in a district.
    """

    __tablename__ = "zilla_panchayats"

    id: Mapped[UUIDType] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Location
    district: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    state: Mapped[str] = mapped_column(String(50), default="Karnataka")

    # Demographics
    total_taluk_panchayats: Mapped[int] = mapped_column(Integer, default=0)
    total_gram_panchayats: Mapped[int] = mapped_column(Integer, default=0)
    total_population: Mapped[int] = mapped_column(Integer, default=0)

    # Administration
    president_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    chief_executive_officer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Contact
    office_phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    office_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    office_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    taluk_panchayats = relationship(
        "TalukPanchayat", back_populates="zilla_panchayat"
    )

    def __repr__(self) -> str:
        return f"<ZillaPanchayat {self.code}: {self.name}>"
