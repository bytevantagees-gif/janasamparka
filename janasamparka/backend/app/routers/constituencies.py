"""
Constituencies router - Multi-tenant management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.constituency import Constituency
from app.models.user import User
from app.models.ward import Ward
from app.models.complaint import Complaint
from app.models.department import Department
from app.schemas.constituency import (
    ConstituencyCreate,
    ConstituencyUpdate,
    ConstituencyResponse,
    ConstituencyStatsResponse,
    ConstituencyListResponse
)

router = APIRouter()


@router.get("/", response_model=ConstituencyListResponse, summary="List all constituencies")
async def list_constituencies(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get list of all constituencies
    By default, only returns active constituencies
    Non-admin users can only see their own constituency
    """
    query = db.query(Constituency)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Constituency.id == constituency_filter)
    
    if active_only:
        query = query.filter(Constituency.is_active == True)
    
    total = query.count()
    constituencies = query.order_by(Constituency.name).offset(skip).limit(limit).all()
    
    return ConstituencyListResponse(
        total=total,
        constituencies=constituencies
    )


@router.get("/{constituency_id}", response_model=ConstituencyStatsResponse, summary="Get constituency details")
async def get_constituency(
    constituency_id: UUID,
    include_stats: bool = True,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a constituency
    Optionally includes statistics
    Non-admin users can only access their own constituency
    """
    # Enforce constituency access control
    if constituency_filter and constituency_filter != constituency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own constituency"
        )
    
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    
    if not constituency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constituency not found"
        )
    
    response_data = ConstituencyResponse.from_orm(constituency)
    
    if include_stats:
        # Calculate statistics
        total_users = db.query(User).filter(User.constituency_id == constituency_id).count()
        total_wards = db.query(Ward).filter(Ward.constituency_id == constituency_id).count()
        total_departments = db.query(Department).filter(Department.constituency_id == constituency_id).count()
        total_complaints = db.query(Complaint).filter(Complaint.constituency_id == constituency_id).count()
        
        # Complaints by status
        resolved_complaints = db.query(Complaint).filter(
            Complaint.constituency_id == constituency_id,
            Complaint.status.in_(['resolved', 'closed'])
        ).count()
        
        statistics = {
            "total_users": total_users,
            "total_wards": total_wards,
            "total_departments": total_departments,
            "total_complaints": total_complaints,
            "resolved_complaints": resolved_complaints,
            "resolution_rate": round((resolved_complaints / total_complaints * 100), 2) if total_complaints > 0 else 0
        }
        
        return ConstituencyStatsResponse(
            **response_data.dict(),
            statistics=statistics
        )
    
    return ConstituencyStatsResponse(
        **response_data.dict(),
        statistics={}
    )


@router.post("/", response_model=ConstituencyResponse, status_code=status.HTTP_201_CREATED)
async def create_constituency(
    constituency: ConstituencyCreate,
    db: Session = Depends(get_db)
    # TODO: Add authentication dependency - only admins can create
):
    """
    Create a new constituency
    Requires admin privileges
    """
    # Check if constituency code already exists
    existing = db.query(Constituency).filter(
        (Constituency.code == constituency.code) | (Constituency.name == constituency.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Constituency with code '{constituency.code}' or name '{constituency.name}' already exists"
        )
    
    # Create new constituency
    new_constituency = Constituency(
        **constituency.dict(),
        is_active=True,
        subscription_tier="basic",
        activated_at=datetime.utcnow()
    )
    
    db.add(new_constituency)
    db.commit()
    db.refresh(new_constituency)
    
    return new_constituency


@router.patch("/{constituency_id}", response_model=ConstituencyResponse)
async def update_constituency(
    constituency_id: UUID,
    constituency_update: ConstituencyUpdate,
    db: Session = Depends(get_db)
    # TODO: Add authentication dependency - only admins can update
):
    """
    Update constituency information
    Requires admin privileges
    """
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    
    if not constituency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constituency not found"
        )
    
    # Update fields
    update_data = constituency_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(constituency, field, value)
    
    constituency.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(constituency)
    
    return constituency


@router.delete("/{constituency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_constituency(
    constituency_id: UUID,
    db: Session = Depends(get_db)
    # TODO: Add authentication dependency - only admins can deactivate
):
    """
    Deactivate a constituency (soft delete)
    Requires admin privileges
    """
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    
    if not constituency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constituency not found"
        )
    
    # Soft delete - set is_active to False
    constituency.is_active = False
    constituency.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None


@router.post("/{constituency_id}/activate", response_model=ConstituencyResponse)
async def activate_constituency(
    constituency_id: UUID,
    db: Session = Depends(get_db)
    # TODO: Add authentication dependency - only admins
):
    """
    Activate a previously deactivated constituency
    Requires admin privileges
    """
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    
    if not constituency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constituency not found"
        )
    
    constituency.is_active = True
    constituency.activated_at = datetime.utcnow()
    constituency.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(constituency)
    
    return constituency


@router.get("/{constituency_id}/stats", summary="Get detailed constituency statistics")
async def get_constituency_statistics(
    constituency_id: UUID,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics for a constituency
    Non-admin users can only access statistics from their own constituency
    """
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    
    if not constituency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constituency not found"
        )
    
    # Enforce constituency access control
    if constituency_filter and constituency_filter != constituency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access statistics from your own constituency"
        )
    
    # Users by role
    users_by_role = db.query(
        User.role,
        func.count(User.id).label('count')
    ).filter(
        User.constituency_id == constituency_id
    ).group_by(User.role).all()
    
    # Complaints by status
    complaints_by_status = db.query(
        Complaint.status,
        func.count(Complaint.id).label('count')
    ).filter(
        Complaint.constituency_id == constituency_id
    ).group_by(Complaint.status).all()
    
    # Complaints by category
    complaints_by_category = db.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).filter(
        Complaint.constituency_id == constituency_id
    ).group_by(Complaint.category).all()
    
    # Ward information
    wards = db.query(Ward).filter(Ward.constituency_id == constituency_id).all()
    total_population = sum(ward.population for ward in wards)
    
    return {
        "constituency": {
            "id": constituency.id,
            "name": constituency.name,
            "code": constituency.code,
            "mla_name": constituency.mla_name
        },
        "users": {
            "by_role": {role: count for role, count in users_by_role},
            "total": sum(count for _, count in users_by_role)
        },
        "complaints": {
            "by_status": {status: count for status, count in complaints_by_status},
            "by_category": {category or "uncategorized": count for category, count in complaints_by_category},
            "total": sum(count for _, count in complaints_by_status)
        },
        "wards": {
            "count": len(wards),
            "total_population": total_population
        }
    }


@router.get("/search/by-code/{code}", response_model=ConstituencyResponse)
async def find_constituency_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Find constituency by code (e.g., PUT001, MNG001)
    """
    constituency = db.query(Constituency).filter(Constituency.code == code).first()
    
    if not constituency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Constituency with code '{code}' not found"
        )
    
    return constituency


@router.get("/compare/all", summary="Compare all constituencies (Admin only)")
async def compare_constituencies(
    db: Session = Depends(get_db)
    # TODO: Add admin authentication
):
    """
    Compare statistics across all active constituencies
    Useful for state-level dashboard
    Requires admin privileges
    """
    constituencies = db.query(Constituency).filter(Constituency.is_active == True).all()
    
    comparison = []
    for constituency in constituencies:
        total_users = db.query(User).filter(User.constituency_id == constituency.id).count()
        total_complaints = db.query(Complaint).filter(Complaint.constituency_id == constituency.id).count()
        resolved_complaints = db.query(Complaint).filter(
            Complaint.constituency_id == constituency.id,
            Complaint.status.in_(['resolved', 'closed'])
        ).count()
        
        comparison.append({
            "constituency": {
                "id": constituency.id,
                "name": constituency.name,
                "code": constituency.code,
                "mla_name": constituency.mla_name,
                "district": constituency.district
            },
            "metrics": {
                "total_users": total_users,
                "total_complaints": total_complaints,
                "resolved_complaints": resolved_complaints,
                "resolution_rate": round((resolved_complaints / total_complaints * 100), 2) if total_complaints > 0 else 0
            }
        })
    
    # Sort by resolution rate
    comparison.sort(key=lambda x: x["metrics"]["resolution_rate"], reverse=True)
    
    return {
        "total_constituencies": len(comparison),
        "comparison": comparison
    }
