"""Complaint schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import date, datetime
from uuid import UUID


class ComplaintCreate(BaseModel):
    """Schema for creating a complaint"""
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    category: Optional[str] = None
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    ward_id: Optional[UUID] = None
    constituency_id: Optional[UUID] = None
    location_description: Optional[str] = None
    voice_transcript: Optional[str] = None
    priority: Optional[str] = Field(
        default="medium",
        pattern=r"^(low|medium|high|urgent)$"
    )
    # Panchayat assignment (for rural complaints)
    gram_panchayat_id: Optional[UUID] = None
    # Department assignment (optional - citizen can select specific department)
    dept_id: Optional[UUID] = None
    citizen_selected_dept: Optional[bool] = False


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
    constituency_id: UUID
    title: str
    description: str
    category: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    ward_id: Optional[UUID]
    location_description: Optional[str]
    dept_id: Optional[UUID]
    assigned_to: Optional[UUID]
    status: str
    priority: str
    voice_transcript: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Ensure response includes constituency id as returned by ORM
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    # Citizen rating and feedback
    citizen_rating: Optional[int] = None
    citizen_feedback: Optional[str] = None
    rating_submitted_at: Optional[datetime] = None
    
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


class StatusCount(BaseModel):
    """Rollup for complaint statuses."""

    status: str
    count: int


class PriorityCount(BaseModel):
    """Rollup for complaint priorities."""

    priority: str
    count: int


class DepartmentBacklog(BaseModel):
    """Open complaint summary for a department."""

    department_id: UUID
    department_name: str
    open_complaints: int
    avg_resolution_hours: Optional[float] = None
    sla_breach_rate: Optional[float] = None


class ComplaintTrendPoint(BaseModel):
    """New and resolved complaints for a single day."""

    date: date
    new: int
    resolved: int


class ComplaintAdvancedAnalytics(BaseModel):
    """Aggregate analytics for complaints dashboard."""

    status_totals: List[StatusCount]
    priority_totals: List[PriorityCount]
    department_backlog: List[DepartmentBacklog]
    resolution_metrics: Dict[str, Optional[float]]
    recent_trend: List[ComplaintTrendPoint]
