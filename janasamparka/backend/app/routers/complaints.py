"""
Complaints router - CRUD operations for complaints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.complaint import Complaint, ComplaintStatus, StatusLog
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
    ComplaintAssign,
    ComplaintStatusUpdate
)

router = APIRouter()


@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new complaint
    TODO: Add authentication to get user_id from token
    """
    # For now, using a placeholder user_id (will be replaced with auth)
    # In production, get user_id from authenticated user
    
    new_complaint = Complaint(
        user_id="00000000-0000-0000-0000-000000000000",  # Placeholder
        title=complaint.title,
        description=complaint.description,
        category=complaint.category,
        lat=complaint.lat,
        lng=complaint.lng,
        location_description=complaint.location_description,
        voice_transcript=complaint.voice_transcript,
        status=ComplaintStatus.SUBMITTED
    )
    
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    
    # Create initial status log
    status_log = StatusLog(
        complaint_id=new_complaint.id,
        old_status=None,
        new_status=ComplaintStatus.SUBMITTED,
        changed_by="00000000-0000-0000-0000-000000000000",  # Placeholder
        note="Complaint submitted"
    )
    db.add(status_log)
    db.commit()
    
    return new_complaint


@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    ward_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    List complaints with pagination and filters
    """
    query = db.query(Complaint)
    
    # Apply filters
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if category:
        query = query.filter(Complaint.category == category)
    if ward_id:
        query = query.filter(Complaint.ward_id == ward_id)
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    complaints = query.order_by(Complaint.created_at.desc()).offset(offset).limit(page_size).all()
    
    return ComplaintListResponse(
        total=total,
        page=page,
        page_size=page_size,
        complaints=complaints
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: UUID,
    db: Session = Depends(get_db)
):
    """Get complaint by ID"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    return complaint


@router.post("/{complaint_id}/assign", response_model=ComplaintResponse)
async def assign_complaint(
    complaint_id: UUID,
    assignment: ComplaintAssign,
    db: Session = Depends(get_db)
):
    """
    Assign complaint to department/officer
    TODO: Add role-based access control (only MLA/admin can assign)
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    old_status = complaint.status
    
    # Update complaint
    complaint.dept_id = assignment.dept_id
    complaint.assigned_to = assignment.assigned_to
    complaint.status = ComplaintStatus.ASSIGNED
    complaint.updated_at = datetime.utcnow()
    
    # Create status log
    status_log = StatusLog(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=ComplaintStatus.ASSIGNED,
        changed_by="00000000-0000-0000-0000-000000000000",  # Placeholder - get from auth
        note=assignment.note or "Complaint assigned to department"
    )
    
    db.add(status_log)
    db.commit()
    db.refresh(complaint)
    
    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: UUID,
    status_update: ComplaintStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update complaint status
    TODO: Add role-based access control
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    old_status = complaint.status
    new_status = status_update.status
    
    # Update complaint
    complaint.status = new_status
    complaint.updated_at = datetime.utcnow()
    
    # Update resolved/closed timestamps
    if new_status == ComplaintStatus.RESOLVED:
        complaint.resolved_at = datetime.utcnow()
    elif new_status == ComplaintStatus.CLOSED:
        complaint.closed_at = datetime.utcnow()
    
    # Create status log
    status_log = StatusLog(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status,
        changed_by="00000000-0000-0000-0000-000000000000",  # Placeholder
        note=status_update.note
    )
    
    db.add(status_log)
    db.commit()
    db.refresh(complaint)
    
    return complaint


@router.get("/stats/summary")
async def get_complaint_stats(db: Session = Depends(get_db)):
    """
    Get complaint statistics summary
    """
    total = db.query(Complaint).count()
    submitted = db.query(Complaint).filter(Complaint.status == ComplaintStatus.SUBMITTED).count()
    assigned = db.query(Complaint).filter(Complaint.status == ComplaintStatus.ASSIGNED).count()
    in_progress = db.query(Complaint).filter(Complaint.status == ComplaintStatus.IN_PROGRESS).count()
    resolved = db.query(Complaint).filter(Complaint.status == ComplaintStatus.RESOLVED).count()
    closed = db.query(Complaint).filter(Complaint.status == ComplaintStatus.CLOSED).count()
    
    return {
        "total": total,
        "by_status": {
            "submitted": submitted,
            "assigned": assigned,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed
        },
        "resolution_rate": round((resolved + closed) / total * 100, 2) if total > 0 else 0
    }
