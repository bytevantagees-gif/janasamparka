"""Schemas for panchayat escalation operations."""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class EscalationRequest(BaseModel):
    """Request to escalate complaint to higher panchayat level"""
    note: Optional[str] = Field(None, max_length=500, description="Reason for escalation")


class TransferRequest(BaseModel):
    """Request to transfer complaint to department"""
    dept_id: UUID = Field(..., description="Department ID to transfer to")
    note: Optional[str] = Field(None, max_length=500, description="Reason for transfer")


class ReassignRequest(BaseModel):
    """Request to reassign complaint to lower panchayat level"""
    gram_panchayat_id: UUID = Field(..., description="Gram Panchayat ID to reassign to")
    note: Optional[str] = Field(None, max_length=500, description="Reason for reassignment")


class EscalationResponse(BaseModel):
    """Response for escalation/transfer operations"""
    success: bool
    message: str
    complaint_id: UUID
    old_assignment_type: Optional[str] = None
    new_assignment_type: str
