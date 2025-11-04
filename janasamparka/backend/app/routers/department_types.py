"""
Department Types router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.auth import require_auth, require_role
from app.models.user import User, UserRole
from app.models.department_type import DepartmentType
from app.models.department import Department
from app.schemas.department_type import (
    DepartmentTypeCreate,
    DepartmentTypeUpdate,
    DepartmentTypeResponse,
    DepartmentTypeListResponse
)

router = APIRouter()


@router.get("/", response_model=DepartmentTypeListResponse)
def list_department_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """List all department types with instance counts"""
    
    query = db.query(
        DepartmentType,
        func.count(Department.id).label('instance_count')
    ).outerjoin(
        Department, Department.department_type_id == DepartmentType.id
    ).group_by(DepartmentType.id)
    
    if is_active is not None:
        query = query.filter(DepartmentType.is_active == is_active)
    
    query = query.order_by(DepartmentType.display_order, DepartmentType.name)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    # Format response
    response_items: List[DepartmentTypeResponse] = []
    for dept_type, count in items:
        item_dict = {
            "id": dept_type.id,
            "name": dept_type.name,
            "code": dept_type.code,
            "description": dept_type.description,
            "icon": dept_type.icon,
            "color": dept_type.color,
            "display_order": dept_type.display_order,
            "is_active": dept_type.is_active,
            "instance_count": count,
            "created_at": dept_type.created_at,
            "updated_at": dept_type.updated_at,
        }
        response_items.append(DepartmentTypeResponse(**item_dict))
    
    return DepartmentTypeListResponse(total=total, items=response_items)


@router.get("/{type_id}", response_model=DepartmentTypeResponse)
def get_department_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Get specific department type by ID"""
    
    result = db.query(
        DepartmentType,
        func.count(Department.id).label('instance_count')
    ).outerjoin(
        Department, Department.department_type_id == DepartmentType.id
    ).filter(
        DepartmentType.id == type_id
    ).group_by(DepartmentType.id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department type not found"
        )
    
    dept_type, count = result
    
    return DepartmentTypeResponse(
        id=dept_type.id,
        name=dept_type.name,
        code=dept_type.code,
        description=dept_type.description,
        icon=dept_type.icon,
        color=dept_type.color,
        display_order=dept_type.display_order,
        is_active=dept_type.is_active,
        instance_count=count,
        created_at=dept_type.created_at,
        updated_at=dept_type.updated_at,
    )


@router.post("/", response_model=DepartmentTypeResponse, status_code=status.HTTP_201_CREATED)
def create_department_type(
    department_type: DepartmentTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Create new department type (admin only)"""
    
    # Check if code already exists
    existing = db.query(DepartmentType).filter(
        (DepartmentType.code == department_type.code) | 
        (DepartmentType.name == department_type.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department type with this code or name already exists"
        )
    
    db_department_type = DepartmentType(**department_type.model_dump())
    db.add(db_department_type)
    db.commit()
    db.refresh(db_department_type)
    
    return DepartmentTypeResponse(
        **db_department_type.__dict__,
        instance_count=0
    )


@router.put("/{type_id}", response_model=DepartmentTypeResponse)
def update_department_type(
    type_id: UUID,
    department_type: DepartmentTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Update department type (admin only)"""
    
    db_type = db.query(DepartmentType).filter(DepartmentType.id == type_id).first()
    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department type not found"
        )
    
    # Update fields
    update_data = department_type.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_type, field, value)
    
    db.commit()
    db.refresh(db_type)
    
    # Get instance count
    count = db.query(func.count(Department.id)).filter(
        Department.department_type_id == type_id
    ).scalar()
    
    return DepartmentTypeResponse(
        **db_type.__dict__,
        instance_count=count
    )


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Delete department type (admin only)"""
    
    db_type = db.query(DepartmentType).filter(DepartmentType.id == type_id).first()
    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department type not found"
        )
    
    # Check if any departments use this type
    dept_count = db.query(func.count(Department.id)).filter(
        Department.department_type_id == type_id
    ).scalar()
    
    if dept_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete department type with {dept_count} active departments"
        )
    
    db.delete(db_type)
    db.commit()
    
    return None
