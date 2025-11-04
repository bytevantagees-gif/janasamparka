"""
Interventions router - CRUD endpoints for satisfaction interventions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.user import User, UserRole
from app.models.satisfaction_intervention import SatisfactionIntervention
from app.models.complaint import Complaint
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas
class InterventionCreate(BaseModel):
    complaint_id: UUID
    citizen_id: UUID
    intervention_type: str  # call, visit, follow-up
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class InterventionUpdate(BaseModel):
    intervention_type: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    outcome: Optional[str] = None  # resolved, escalated, pending
    completion_notes: Optional[str] = None
    citizen_now_happy: Optional[bool] = None


class InterventionComplete(BaseModel):
    outcome: str  # resolved, escalated, pending
    completion_notes: str
    citizen_now_happy: bool


@router.post("")
async def create_intervention(
    intervention: InterventionCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Create a new satisfaction intervention.
    Only moderators, admins, and MLAs can create interventions.
    """
    # Role check
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.MLA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators, admins, and MLAs can create interventions"
        )
    
    # Validate intervention_type
    valid_types = ["call", "visit", "follow-up"]
    if intervention.intervention_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid intervention_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create intervention
    db_intervention = SatisfactionIntervention(
        complaint_id=intervention.complaint_id,
        citizen_id=intervention.citizen_id,
        moderator_id=current_user.id,
        intervention_type=intervention.intervention_type,
        notes=intervention.notes,
        scheduled_at=intervention.scheduled_at
    )
    
    db.add(db_intervention)
    db.commit()
    db.refresh(db_intervention)
    
    return {
        "id": str(db_intervention.id),
        "complaint_id": str(db_intervention.complaint_id),
        "citizen_id": str(db_intervention.citizen_id),
        "moderator_id": str(db_intervention.moderator_id),
        "intervention_type": db_intervention.intervention_type,
        "notes": db_intervention.notes,
        "scheduled_at": db_intervention.scheduled_at.isoformat() if db_intervention.scheduled_at else None,
        "created_at": db_intervention.created_at.isoformat(),
        "status": "scheduled"
    }


@router.get("")
async def get_interventions(
    moderator_id: Optional[UUID] = None,
    citizen_id: Optional[UUID] = None,
    complaint_id: Optional[UUID] = None,
    outcome: Optional[str] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get list of interventions with optional filters.
    Non-admin users only see interventions from their own constituency
    """
    # Role check
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.MLA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators, admins, and MLAs can view interventions"
        )
    
    query = db.query(SatisfactionIntervention).join(Complaint, SatisfactionIntervention.complaint_id == Complaint.id)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    # Apply filters
    if moderator_id:
        query = query.filter(SatisfactionIntervention.moderator_id == moderator_id)
    if citizen_id:
        query = query.filter(SatisfactionIntervention.citizen_id == citizen_id)
    if complaint_id:
        query = query.filter(SatisfactionIntervention.complaint_id == complaint_id)
    if outcome:
        query = query.filter(SatisfactionIntervention.outcome == outcome)
    
    interventions = query.order_by(SatisfactionIntervention.scheduled_at.desc()).all()
    
    return [
        {
            "id": str(i.id),
            "complaint_id": str(i.complaint_id),
            "citizen_id": str(i.citizen_id),
            "moderator_id": str(i.moderator_id),
            "intervention_type": i.intervention_type,
            "notes": i.notes,
            "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
            "completed_at": i.completed_at.isoformat() if i.completed_at else None,
            "outcome": i.outcome,
            "completion_notes": i.completion_notes,
            "citizen_now_happy": i.citizen_now_happy,
            "created_at": i.created_at.isoformat(),
            "updated_at": i.updated_at.isoformat()
        }
        for i in interventions
    ]


@router.patch("/{intervention_id}")
async def update_intervention(
    intervention_id: UUID,
    intervention_update: InterventionUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Update an existing intervention.
    """
    # Role check
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.MLA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators, admins, and MLAs can update interventions"
        )
    
    # Get intervention
    intervention = db.query(SatisfactionIntervention).filter(
        SatisfactionIntervention.id == intervention_id
    ).first()
    
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
    
    # Only the moderator who created it or admin/mla can update
    if intervention.moderator_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.MLA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own interventions"
        )
    
    # Update fields
    if intervention_update.intervention_type:
        valid_types = ["call", "visit", "follow-up"]
        if intervention_update.intervention_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid intervention_type. Must be one of: {', '.join(valid_types)}"
            )
        intervention.intervention_type = intervention_update.intervention_type
    
    if intervention_update.notes is not None:
        intervention.notes = intervention_update.notes
    if intervention_update.scheduled_at is not None:
        intervention.scheduled_at = intervention_update.scheduled_at
    if intervention_update.outcome is not None:
        intervention.outcome = intervention_update.outcome
    if intervention_update.completion_notes is not None:
        intervention.completion_notes = intervention_update.completion_notes
    if intervention_update.citizen_now_happy is not None:
        intervention.citizen_now_happy = intervention_update.citizen_now_happy
    
    intervention.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(intervention)
    
    return {
        "id": str(intervention.id),
        "complaint_id": str(intervention.complaint_id),
        "citizen_id": str(intervention.citizen_id),
        "moderator_id": str(intervention.moderator_id),
        "intervention_type": intervention.intervention_type,
        "notes": intervention.notes,
        "scheduled_at": intervention.scheduled_at.isoformat() if intervention.scheduled_at else None,
        "completed_at": intervention.completed_at.isoformat() if intervention.completed_at else None,
        "outcome": intervention.outcome,
        "completion_notes": intervention.completion_notes,
        "citizen_now_happy": intervention.citizen_now_happy,
        "created_at": intervention.created_at.isoformat(),
        "updated_at": intervention.updated_at.isoformat()
    }


@router.post("/{intervention_id}/complete")
async def complete_intervention(
    intervention_id: UUID,
    completion: InterventionComplete,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Mark an intervention as completed with outcome.
    """
    # Role check
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.MLA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators, admins, and MLAs can complete interventions"
        )
    
    # Get intervention
    intervention = db.query(SatisfactionIntervention).filter(
        SatisfactionIntervention.id == intervention_id
    ).first()
    
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
    
    # Only the moderator who created it or admin/mla can complete
    if intervention.moderator_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.MLA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own interventions"
        )
    
    # Validate outcome
    valid_outcomes = ["resolved", "escalated", "pending"]
    if completion.outcome not in valid_outcomes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid outcome. Must be one of: {', '.join(valid_outcomes)}"
        )
    
    # Mark as completed
    intervention.completed_at = datetime.utcnow()
    intervention.outcome = completion.outcome
    intervention.completion_notes = completion.completion_notes
    intervention.citizen_now_happy = completion.citizen_now_happy
    intervention.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(intervention)
    
    return {
        "id": str(intervention.id),
        "complaint_id": str(intervention.complaint_id),
        "citizen_id": str(intervention.citizen_id),
        "moderator_id": str(intervention.moderator_id),
        "intervention_type": intervention.intervention_type,
        "notes": intervention.notes,
        "scheduled_at": intervention.scheduled_at.isoformat() if intervention.scheduled_at else None,
        "completed_at": intervention.completed_at.isoformat(),
        "outcome": intervention.outcome,
        "completion_notes": intervention.completion_notes,
        "citizen_now_happy": intervention.citizen_now_happy,
        "created_at": intervention.created_at.isoformat(),
        "updated_at": intervention.updated_at.isoformat(),
        "status": "completed"
    }
