"""
Users router - User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from typing import List, Optional
from datetime import datetime, timezone

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user
    TODO: Add authentication and authorization
    """
    # Check if phone number already exists
    existing = db.query(User).filter(User.phone == user.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with phone {user.phone} already exists"
        )
    
    new_user = User(
        phone=user.phone,
        name=user.name,
        role=user.role,
        constituency_id=user.constituency_id,
        ward_id=user.ward_id,
        locale_pref=user.locale_pref or 'en',
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    roles: Optional[str] = None,
    constituency_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get list of users with optional filters
    Non-admin users can only see users from their own constituency
    """
    query = db.query(User)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(User.constituency_id == constituency_filter)
    
    if roles:
        role_list = [role.strip() for role in roles.split(',')]
        query = query.filter(User.role.in_(role_list))
    
    if constituency_id and not constituency_filter:  # Only allow explicit filter if admin
        query = query.filter(User.constituency_id == constituency_id)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.locale_pref is not None:
        user.locale_pref = user_update.locale_pref
    if user_update.constituency_id is not None:
        user.constituency_id = user_update.constituency_id
    if user_update.ward_id is not None:
        user.ward_id = user_update.ward_id
    if user_update.profile_photo is not None:
        user.profile_photo = user_update.profile_photo
    
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Soft delete a user (set is_active to False)
    TODO: Add authorization - only admin can delete users
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = "false"
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return None


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Reactivate a deactivated user
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = "true"
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
    return user
