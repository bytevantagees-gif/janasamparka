"""
Workflow-related schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class WorkApproval(BaseModel):
    """Schema for work approval"""
    comments: Optional[str] = Field(None, description="Approval comments")
    
    class Config:
        json_schema_extra = {
            "example": {
                "comments": "Work completed satisfactorily, complaint resolved"
            }
        }


class WorkRejection(BaseModel):
    """Schema for work rejection"""
    reason: str = Field(..., description="Reason for rejection", min_length=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Work not completed as per requirements. Please redo."
            }
        }


class WorkflowStatusResponse(BaseModel):
    """Schema for workflow status information"""
    current_status: str
    allowed_transitions: list[str]
    requires_approval: bool
    can_reopen: bool
    is_terminal: bool
