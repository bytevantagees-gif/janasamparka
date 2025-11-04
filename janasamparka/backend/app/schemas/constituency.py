"""
Constituency schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ConstituencyBase(BaseModel):
    """Base constituency schema"""
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=3, max_length=50)
    district: str = Field(..., min_length=2, max_length=255)
    state: str = Field(default="Karnataka", max_length=100)
    mla_name: Optional[str] = Field(None, max_length=255)
    mla_party: Optional[str] = Field(None, max_length=100)
    mla_contact_phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    mla_contact_email: Optional[str] = None
    total_wards: Optional[int] = Field(default=0, ge=0)
    assembly_number: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    taluks: Optional[list[str]] = Field(default=None, description="List of taluks covered by this constituency (e.g., ['Puttur', 'Kadaba'])")


class ConstituencyCreate(ConstituencyBase):
    """Schema for creating a constituency"""
    pass


class ConstituencyUpdate(BaseModel):
    """Schema for updating a constituency"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    mla_name: Optional[str] = Field(None, max_length=255)
    mla_party: Optional[str] = Field(None, max_length=100)
    mla_contact_phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    mla_contact_email: Optional[str] = None
    total_wards: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    subscription_tier: Optional[str] = Field(None, pattern=r'^(basic|premium|enterprise)$')
    description: Optional[str] = None
    taluks: Optional[list[str]] = Field(None, description="List of taluks covered by this constituency")


class ConstituencyResponse(ConstituencyBase):
    """Schema for constituency response"""
    id: UUID
    total_population: int
    is_active: bool
    subscription_tier: str
    logo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConstituencyStatsResponse(ConstituencyResponse):
    """Schema for constituency with statistics"""
    statistics: dict[str, int]  # total_users, total_complaints, total_wards, etc.


class ConstituencyListResponse(BaseModel):
    """Schema for paginated constituency list"""
    total: int
    constituencies: list[ConstituencyResponse]
