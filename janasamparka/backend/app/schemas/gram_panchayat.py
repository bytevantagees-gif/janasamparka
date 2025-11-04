"""
Gram Panchayat Schemas for API requests/responses
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class GramPanchayatBase(BaseModel):
    """Base schema for Gram Panchayat"""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    taluk_name: str = Field(..., min_length=1, max_length=100)
    district: str = Field(..., min_length=1, max_length=100)
    state: str = Field(default="Karnataka", max_length=50)
    
    population: Optional[int] = Field(default=0, ge=0)
    households: Optional[int] = Field(default=0, ge=0)
    villages_covered: Optional[int] = Field(default=1, ge=1)
    
    president_name: Optional[str] = Field(None, max_length=255)
    vice_president_name: Optional[str] = Field(None, max_length=255)
    secretary_name: Optional[str] = Field(None, max_length=255)
    
    office_phone: Optional[str] = Field(None, max_length=15)
    office_email: Optional[str] = Field(None, max_length=255)
    office_address: Optional[str] = None
    
    is_active: bool = True
    description: Optional[str] = None


class GramPanchayatCreate(GramPanchayatBase):
    """Schema for creating a Gram Panchayat"""
    taluk_panchayat_id: UUID
    constituency_id: UUID


class GramPanchayatUpdate(BaseModel):
    """Schema for updating a Gram Panchayat"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    population: Optional[int] = Field(None, ge=0)
    households: Optional[int] = Field(None, ge=0)
    villages_covered: Optional[int] = Field(None, ge=1)
    
    president_name: Optional[str] = Field(None, max_length=255)
    vice_president_name: Optional[str] = Field(None, max_length=255)
    secretary_name: Optional[str] = Field(None, max_length=255)
    
    office_phone: Optional[str] = Field(None, max_length=15)
    office_email: Optional[str] = Field(None, max_length=255)
    office_address: Optional[str] = None
    
    is_active: Optional[bool] = None
    description: Optional[str] = None


class GramPanchayatResponse(GramPanchayatBase):
    """Schema for Gram Panchayat API response"""
    id: UUID
    taluk_panchayat_id: Optional[UUID] = None
    constituency_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GramPanchayatWithHierarchy(GramPanchayatResponse):
    """Schema for Gram Panchayat with hierarchy information"""
    taluk_panchayat_name: Optional[str] = None
    zilla_panchayat_name: Optional[str] = None
    constituency_name: Optional[str] = None
    mla_name: Optional[str] = None
    
    # Statistics
    total_users: Optional[int] = 0
    total_submissions: Optional[int] = 0
    pending_submissions: Optional[int] = 0
