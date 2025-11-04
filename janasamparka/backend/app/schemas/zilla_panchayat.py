"""
Zilla Panchayat Schemas for API requests/responses
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ZillaPanchayatBase(BaseModel):
    """Base schema for Zilla Panchayat"""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    district: str = Field(..., min_length=1, max_length=100)
    state: str = Field(default="Karnataka", max_length=50)
    
    total_taluk_panchayats: Optional[int] = Field(default=0, ge=0)
    total_gram_panchayats: Optional[int] = Field(default=0, ge=0)
    total_population: Optional[int] = Field(default=0, ge=0)
    
    president_name: Optional[str] = Field(None, max_length=255)
    chief_executive_officer_name: Optional[str] = Field(None, max_length=255)
    
    office_phone: Optional[str] = Field(None, max_length=15)
    office_email: Optional[str] = Field(None, max_length=255)
    office_address: Optional[str] = None
    
    is_active: bool = True
    description: Optional[str] = None


class ZillaPanchayatCreate(ZillaPanchayatBase):
    """Schema for creating a Zilla Panchayat"""
    pass


class ZillaPanchayatUpdate(BaseModel):
    """Schema for updating a Zilla Panchayat"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    total_taluk_panchayats: Optional[int] = Field(None, ge=0)
    total_gram_panchayats: Optional[int] = Field(None, ge=0)
    total_population: Optional[int] = Field(None, ge=0)
    
    president_name: Optional[str] = Field(None, max_length=255)
    chief_executive_officer_name: Optional[str] = Field(None, max_length=255)
    
    office_phone: Optional[str] = Field(None, max_length=15)
    office_email: Optional[str] = Field(None, max_length=255)
    office_address: Optional[str] = None
    
    is_active: Optional[bool] = None
    description: Optional[str] = None


class ZillaPanchayatResponse(ZillaPanchayatBase):
    """Schema for Zilla Panchayat API response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ZillaPanchayatWithHierarchy(ZillaPanchayatResponse):
    """Schema for Zilla Panchayat with complete hierarchy"""
    # Counts
    taluk_panchayats_count: Optional[int] = 0
    gram_panchayats_count: Optional[int] = 0
    
    # Statistics
    total_users: Optional[int] = 0
    total_submissions: Optional[int] = 0
    pending_submissions: Optional[int] = 0


class PanchayatHierarchy(BaseModel):
    """Complete Panchayat hierarchy for a constituency"""
    constituency_id: UUID
    constituency_name: str
    mla_name: Optional[str] = None
    
    zilla_panchayat: Optional[ZillaPanchayatResponse] = None
    taluk_panchayats: list[dict] = []  # TalukPanchayatResponse with gram_panchayats
    total_gram_panchayats: int = 0
