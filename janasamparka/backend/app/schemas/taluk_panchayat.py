"""
Taluk Panchayat Schemas for API requests/responses
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TalukPanchayatBase(BaseModel):
    """Base schema for Taluk Panchayat"""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    taluk_name: str = Field(..., min_length=1, max_length=100)
    district: str = Field(..., min_length=1, max_length=100)
    state: str = Field(default="Karnataka", max_length=50)
    
    total_gram_panchayats: Optional[int] = Field(default=0, ge=0)
    total_population: Optional[int] = Field(default=0, ge=0)
    
    president_name: Optional[str] = Field(None, max_length=255)
    executive_officer_name: Optional[str] = Field(None, max_length=255)
    
    office_phone: Optional[str] = Field(None, max_length=15)
    office_email: Optional[str] = Field(None, max_length=255)
    office_address: Optional[str] = None
    
    is_active: bool = True
    description: Optional[str] = None


class TalukPanchayatCreate(TalukPanchayatBase):
    """Schema for creating a Taluk Panchayat"""
    zilla_panchayat_id: UUID
    constituency_id: UUID


class TalukPanchayatUpdate(BaseModel):
    """Schema for updating a Taluk Panchayat"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    total_gram_panchayats: Optional[int] = Field(None, ge=0)
    total_population: Optional[int] = Field(None, ge=0)
    
    president_name: Optional[str] = Field(None, max_length=255)
    executive_officer_name: Optional[str] = Field(None, max_length=255)
    
    office_phone: Optional[str] = Field(None, max_length=15)
    office_email: Optional[str] = Field(None, max_length=255)
    office_address: Optional[str] = None
    
    is_active: Optional[bool] = None
    description: Optional[str] = None


class TalukPanchayatResponse(TalukPanchayatBase):
    """Schema for Taluk Panchayat API response"""
    id: UUID
    zilla_panchayat_id: Optional[UUID] = None
    constituency_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TalukPanchayatWithHierarchy(TalukPanchayatResponse):
    """Schema for Taluk Panchayat with hierarchy information"""
    zilla_panchayat_name: Optional[str] = None
    constituency_name: Optional[str] = None
    mla_name: Optional[str] = None
    
    # Gram Panchayats count
    gram_panchayats_count: Optional[int] = 0
    
    # Statistics
    total_users: Optional[int] = 0
    total_submissions: Optional[int] = 0
    pending_submissions: Optional[int] = 0
