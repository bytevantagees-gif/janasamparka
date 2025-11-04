"""
Complaint schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ComplaintCreate(BaseModel):
    """Schema for creating a complaint"""
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    category: Optional[str] = None
    lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    lng: Optional[Decimal] = Field(None, ge=-180, le=180)
    location_description: Optional[str] = None
    voice_transcript: Optional[str] = None


class ComplaintUpdate(BaseModel):
    """Schema for updating a complaint"""
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    priority: Optional[str] = None


class ComplaintAssign(BaseModel):
    """Schema for assigning a complaint"""
    dept_id: UUID
    assigned_to: Optional[UUID] = None
    note: Optional[str] = None


class ComplaintStatusUpdate(BaseModel):
    """Schema for updating complaint status"""
    status: str = Field(..., pattern=r'^(submitted|assigned|in_progress|resolved|closed|rejected)$')
    note: Optional[str] = None


class MediaResponse(BaseModel):
    """Schema for media response"""
    id: UUID
    url: str
    media_type: str
    proof_type: Optional[str] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class StatusLogResponse(BaseModel):
    """Schema for status log response"""
    id: UUID
    old_status: Optional[str]
    new_status: str
    note: Optional[str]
    timestamp: datetime
    changed_by: UUID
    
    class Config:
        from_attributes = True


class ComplaintResponse(BaseModel):
    """Schema for complaint response"""
    id: UUID
    user_id: UUID
    title: str
    description: str
    category: Optional[str]
    lat: Optional[Decimal]
    lng: Optional[Decimal]
    ward_id: Optional[UUID]
    location_description: Optional[str]
    dept_id: Optional[UUID]
    assigned_to: Optional[UUID]
    status: str
    priority: str
    voice_transcript: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ComplaintDetailResponse(ComplaintResponse):
    """Schema for detailed complaint response with media and logs"""
    media: List[MediaResponse] = []
    status_logs: List[StatusLogResponse] = []


class ComplaintListResponse(BaseModel):
    """Schema for paginated complaint list"""
    total: int
    page: int
    page_size: int
    complaints: List[ComplaintResponse]
