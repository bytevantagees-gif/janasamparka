"""Pydantic schemas for Case Notes, Department Routing, and Escalations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ===== Case Notes =====

class CaseNoteCreate(BaseModel):
    """Schema for creating a case note."""
    
    note: str = Field(..., min_length=1, max_length=5000, description="Note content")
    note_type: str = Field(default="general", description="Type of note")
    is_public: bool = Field(default=False, description="Visible to citizen")
    resets_idle_timer: bool = Field(default=True, description="Resets idle timer for case aging")


class CaseNoteResponse(BaseModel):
    """Schema for case note response."""
    
    id: UUID
    complaint_id: UUID
    note: str
    note_type: str
    created_by: UUID
    creator_name: Optional[str] = None
    is_public: bool
    resets_idle_timer: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Department Routing =====

class DepartmentRoutingCreate(BaseModel):
    """Schema for routing a complaint to a department."""
    
    to_dept_id: UUID = Field(..., description="Target department ID")
    reason: str = Field(..., description="Reason for routing")
    comments: Optional[str] = Field(None, max_length=1000, description="Additional comments")


class DepartmentRoutingAccept(BaseModel):
    """Schema for accepting a routed complaint."""
    
    accepted: bool = Field(..., description="Accept or reject the routing")
    comments: Optional[str] = Field(None, max_length=1000, description="Comments on decision")


class DepartmentRoutingResponse(BaseModel):
    """Schema for department routing response."""
    
    id: UUID
    complaint_id: UUID
    from_dept_id: Optional[UUID]
    from_dept_name: Optional[str] = None
    to_dept_id: UUID
    to_dept_name: Optional[str] = None
    reason: str
    comments: Optional[str]
    routed_by: UUID
    routed_by_name: Optional[str] = None
    routed_at: datetime
    accepted: Optional[bool]
    accepted_by: Optional[UUID]
    accepted_by_name: Optional[str] = None
    accepted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ===== Complaint Escalations =====

class ComplaintEscalationCreate(BaseModel):
    """Schema for escalating a complaint to MLA."""
    
    reason: str = Field(..., description="Reason for escalation")
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed description")


class ComplaintEscalationResolve(BaseModel):
    """Schema for resolving an escalation."""
    
    resolution_notes: str = Field(..., min_length=10, max_length=2000, description="Resolution notes")


class ComplaintEscalationResponse(BaseModel):
    """Schema for escalation response."""
    
    id: UUID
    complaint_id: UUID
    reason: str
    description: str
    escalated_by: UUID
    escalated_by_name: Optional[str] = None
    resolved: bool
    resolution_notes: Optional[str]
    resolved_by: Optional[UUID]
    resolved_by_name: Optional[str] = None
    resolved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Department Suggestions =====

class DepartmentSuggestion(BaseModel):
    """Schema for department suggestion."""
    
    dept_id: UUID
    dept_name: str
    dept_code: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    reason: str = Field(..., description="Why this department was suggested")


class DepartmentSuggestionRequest(BaseModel):
    """Schema for requesting department suggestions."""
    
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=10, max_length=5000)
    category: Optional[str] = None
    location_description: Optional[str] = None


class DepartmentSuggestionResponse(BaseModel):
    """Schema for department suggestion response."""
    
    suggestions: list[DepartmentSuggestion] = Field(..., description="List of suggested departments")
    constituency_id: UUID = Field(..., description="Constituency for which suggestions are made")
