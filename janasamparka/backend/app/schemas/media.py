"""Media schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MediaCreate(BaseModel):
    """Schema for attaching an existing media asset to a complaint."""

    url: str
    media_type: str = Field(..., description="photo, video, audio, or document")
    caption: Optional[str] = None
    proof_type: Optional[str] = None
    photo_type: Optional[str] = None
    file_size: Optional[float] = Field(None, ge=0)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)


class MediaResponse(BaseModel):
    """Schema returned for media entries."""

    id: UUID
    complaint_id: UUID
    url: str
    media_type: str
    caption: Optional[str] = None
    proof_type: Optional[str] = None
    photo_type: Optional[str] = None
    file_size: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    uploaded_at: datetime
    uploaded_by: Optional[UUID] = None

    class Config:
        from_attributes = True
