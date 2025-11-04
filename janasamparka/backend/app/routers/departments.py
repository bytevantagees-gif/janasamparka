"""
Departments router - CRUD operations for departments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from sqlalchemy import or_

router = APIRouter()


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new department
    """
    # Check if department code already exists
    existing = db.query(Department).filter(Department.code == department.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with code '{department.code}' already exists"
        )
    
    new_department = Department(
        name=department.name,
        code=department.code,
        contact_phone=department.contact_phone,
        contact_email=department.contact_email,
        head_name=department.head_name,
        is_active=department.is_active
    )
    
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    
    return new_department


@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    department_type_id: Optional[UUID] = None,
    constituency_id: Optional[UUID] = None,
    taluk_panchayat_id: Optional[UUID] = None,
    gram_panchayat_id: Optional[UUID] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get list of departments with hierarchical filters
    Non-admin users can only see departments from their own constituency
    """
    query = db.query(Department)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Department.constituency_id == constituency_filter)
    
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    
    if department_type_id is not None:
        query = query.filter(Department.department_type_id == department_type_id)
    
    if constituency_id is not None and not constituency_filter:  # Only allow explicit filter if admin
        query = query.filter(Department.constituency_id == constituency_id)
    
    if taluk_panchayat_id is not None:
        query = query.filter(Department.taluk_panchayat_id == taluk_panchayat_id)
    
    if gram_panchayat_id is not None:
        query = query.filter(Department.gram_panchayat_id == gram_panchayat_id)
    
    departments = query.offset(skip).limit(limit).all()
    
    # Add complaint counts for each department
    from app.models.complaint import Complaint
    departments_with_counts = []
    for dept in departments:
        complaint_count = db.query(Complaint).filter(
            Complaint.dept_id == dept.id,
            # Apply same constituency filtering to complaints
            or_(constituency_filter == None, Complaint.constituency_id == constituency_filter)
        ).count()
        
        # Create response with complaint count
        dept_response = DepartmentResponse(
            id=dept.id,
            name=dept.name,
            code=dept.code,
            contact_phone=dept.contact_phone,
            contact_email=dept.contact_email,
            is_active=dept.is_active,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
            complaint_count=complaint_count
        )
        departments_with_counts.append(dept_response)
    
    return departments_with_counts


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: UUID,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific department by ID
    Non-admin users can only access departments from their own constituency
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Enforce constituency access control
    if constituency_filter and department.constituency_id != constituency_filter:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access departments from your constituency"
        )
    
    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: UUID,
    department_update: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a department
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Update fields
    update_data = department_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(department, field, value)
    
    department.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(department)
    
    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Soft delete a department (set is_active to False)
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    department.is_active = False
    department.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return None
