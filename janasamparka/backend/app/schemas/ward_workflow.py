"""Schemas for ward-centric complaint workflow."""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class WardAssignToDepartmentRequest(BaseModel):
    """Request from ward officer to assign complaint to department"""
    dept_id: UUID = Field(..., description="Department ID to assign to")
    public_note: str = Field(..., min_length=10, max_length=500, 
                            description="Public note explaining the assignment (visible to citizen)")


class AddPublicNoteRequest(BaseModel):
    """Add a public note visible to citizens"""
    note: str = Field(..., min_length=10, max_length=500, 
                     description="Meaningful update about progress")


class AddInternalNoteRequest(BaseModel):
    """Add an internal note only visible to officers"""
    note: str = Field(..., min_length=5, max_length=500, 
                     description="Internal coordination note")


class WardAssignmentResponse(BaseModel):
    """Response for ward assignment operation"""
    success: bool
    message: str
    complaint_id: UUID
    assigned_department: str
    ward_officer_name: str
