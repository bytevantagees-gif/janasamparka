"""
Ward schemas for request/response validation
"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class WardBase(BaseModel):
    name: str
    ward_number: int
    taluk: str
    constituency_id: UUID
    population: int
    ward_type: Optional[str] = None
    gram_panchayat_id: Optional[UUID] = None
    taluk_panchayat_id: Optional[UUID] = None
    city_corporation_id: Optional[UUID] = None


class WardCreate(WardBase):
    pass


class WardUpdate(BaseModel):
    name: Optional[str] = None
    ward_number: Optional[int] = None
    taluk: Optional[str] = None
    population: Optional[int] = None
    ward_type: Optional[str] = None
    gram_panchayat_id: Optional[UUID] = None
    taluk_panchayat_id: Optional[UUID] = None
    city_corporation_id: Optional[UUID] = None


class WardResponse(WardBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
