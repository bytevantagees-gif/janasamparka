"""
Citizen ratings and feedback router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.auth import require_auth
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.rating import CitizenRatingSubmit, CitizenRatingResponse, RatingSummary

router = APIRouter()


@router.post("/{complaint_id}/rate", response_model=CitizenRatingResponse)
async def submit_rating(
    complaint_id: UUID,
    rating_data: CitizenRatingSubmit,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Submit citizen rating and feedback for a completed complaint
    
    Rules:
    - Only the original complainant can rate
    - Complaint must be in 'closed' status
    - Can only rate once
    - Rating must be 1-5 stars
    """
    # Get the complaint
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check if user is the original complainant
    if complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the original complainant can rate this complaint"
        )
    
    # Check if complaint is closed
    if complaint.status != "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate complaints that have been closed"
        )
    
    # Check if already rated
    if complaint.citizen_rating is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this complaint"
        )
    
    # Save rating
    complaint.citizen_rating = rating_data.rating
    complaint.citizen_feedback = rating_data.feedback
    complaint.rating_submitted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(complaint)
    
    return CitizenRatingResponse(
        citizen_rating=complaint.citizen_rating,
        citizen_feedback=complaint.citizen_feedback,
        rating_submitted_at=complaint.rating_submitted_at,
        can_rate=False,
        rating_message="Thank you for your feedback!"
    )


@router.get("/{complaint_id}/rating", response_model=CitizenRatingResponse)
async def get_complaint_rating(
    complaint_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get rating status for a complaint
    Shows if rating exists and if user can rate
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Determine if user can rate
    can_rate = False
    rating_message = None
    
    if complaint.user_id != current_user.id:
        rating_message = "Only the original complainant can rate"
    elif complaint.status != "closed":
        rating_message = f"Complaint must be closed before rating (current status: {complaint.status})"
    elif complaint.citizen_rating is not None:
        rating_message = "You have already rated this complaint"
    else:
        can_rate = True
        rating_message = "You can rate this complaint"
    
    return CitizenRatingResponse(
        citizen_rating=complaint.citizen_rating,
        citizen_feedback=complaint.citizen_feedback,
        rating_submitted_at=complaint.rating_submitted_at,
        can_rate=can_rate,
        rating_message=rating_message
    )


@router.put("/{complaint_id}/rating", response_model=CitizenRatingResponse)
async def update_rating(
    complaint_id: UUID,
    rating_data: CitizenRatingSubmit,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Update an existing rating (within 24 hours of submission)
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check if user is the original complainant
    if complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the original complainant can update the rating"
        )
    
    # Check if rating exists
    if complaint.citizen_rating is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No rating exists to update. Please submit a rating first."
        )
    
    # Check if within 24 hours
    if complaint.rating_submitted_at:
        hours_since_rating = (datetime.utcnow() - complaint.rating_submitted_at).total_seconds() / 3600
        if hours_since_rating > 24:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating can only be updated within 24 hours of submission"
            )
    
    # Update rating
    complaint.citizen_rating = rating_data.rating
    complaint.citizen_feedback = rating_data.feedback
    
    db.commit()
    db.refresh(complaint)
    
    return CitizenRatingResponse(
        citizen_rating=complaint.citizen_rating,
        citizen_feedback=complaint.citizen_feedback,
        rating_submitted_at=complaint.rating_submitted_at,
        can_rate=False,
        rating_message="Rating updated successfully"
    )


@router.get("/summary", response_model=RatingSummary)
async def get_ratings_summary(
    constituency_id: Optional[UUID] = None,
    department_id: Optional[UUID] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get summary of all ratings
    Filters by constituency for non-admin users
    """
    query = db.query(Complaint).filter(
        Complaint.citizen_rating.isnot(None)
    )
    
    # Apply constituency filter for non-admins
    if current_user.role != "admin":
        query = query.filter(Complaint.constituency_id == current_user.constituency_id)
    elif constituency_id:
        query = query.filter(Complaint.constituency_id == constituency_id)
    
    # Filter by department if specified
    if department_id:
        query = query.filter(Complaint.dept_id == department_id)
    
    # Get all rated complaints
    rated_complaints = query.all()
    
    if not rated_complaints:
        return RatingSummary(
            total_ratings=0,
            average_rating=0.0,
            rating_distribution={},
            satisfaction_rate=0.0
        )
    
    # Calculate metrics
    total_ratings = len(rated_complaints)
    ratings = [c.citizen_rating for c in rated_complaints]
    average_rating = sum(ratings) / total_ratings
    
    # Rating distribution
    rating_distribution = {str(i): 0 for i in range(1, 6)}
    for rating in ratings:
        rating_distribution[str(rating)] = rating_distribution.get(str(rating), 0) + 1
    
    # Satisfaction rate (4-5 stars)
    satisfied = sum(1 for r in ratings if r >= 4)
    satisfaction_rate = (satisfied / total_ratings) * 100
    
    return RatingSummary(
        total_ratings=total_ratings,
        average_rating=round(average_rating, 2),
        rating_distribution=rating_distribution,
        satisfaction_rate=round(satisfaction_rate, 2)
    )
