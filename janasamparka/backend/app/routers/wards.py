"""
Wards router - CRUD operations for wards
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.ward import Ward
from app.models.user import User
from app.schemas.ward import WardCreate, WardUpdate, WardResponse

router = APIRouter()


@router.post("/", response_model=WardResponse, status_code=status.HTTP_201_CREATED)
async def create_ward(
    ward: WardCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new ward
    """
    # Check if ward number already exists in constituency
    existing = db.query(Ward).filter(
        Ward.ward_number == ward.ward_number,
        Ward.constituency_id == ward.constituency_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ward number '{ward.ward_number}' already exists in this constituency"
        )
    
    new_ward = Ward(
        name=ward.name,
        ward_number=ward.ward_number,
        taluk=ward.taluk,
        constituency_id=ward.constituency_id,
        population=ward.population,
        male_population=ward.male_population,
        female_population=ward.female_population,
        area_sq_km=ward.area_sq_km
    )
    
    db.add(new_ward)
    db.commit()
    db.refresh(new_ward)
    
    return new_ward


@router.get("/", response_model=List[WardResponse])
async def get_wards(
    skip: int = 0,
    limit: int = 100,
    constituency_id: Optional[UUID] = None,
    ward_type: Optional[str] = None,
    gram_panchayat_id: Optional[UUID] = None,
    taluk_panchayat_id: Optional[UUID] = None,
    city_corporation_id: Optional[UUID] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get list of wards with hierarchical filtering
    Non-admin users can only see wards from their own constituency
    
    Filters:
    - constituency_id: Filter by constituency (admin only)
    - ward_type: Filter by type (gram_panchayat, taluk_panchayat, city_corporation, municipality)
    - gram_panchayat_id: Filter by Gram Panchayat
    - taluk_panchayat_id: Filter by Taluk Panchayat
    - city_corporation_id: Filter by City Corporation
    """
    query = db.query(Ward)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Ward.constituency_id == constituency_filter)
    
    # Apply filters
    if constituency_id and not constituency_filter:  # Only allow explicit filter if admin
        query = query.filter(Ward.constituency_id == constituency_id)
    
    if ward_type:
        query = query.filter(Ward.ward_type == ward_type)
    
    if gram_panchayat_id:
        query = query.filter(Ward.gram_panchayat_id == gram_panchayat_id)
    
    if taluk_panchayat_id:
        query = query.filter(Ward.taluk_panchayat_id == taluk_panchayat_id)
    
    if city_corporation_id:
        query = query.filter(Ward.city_corporation_id == city_corporation_id)
    
    wards = query.offset(skip).limit(limit).all()
    return wards


@router.get("/{ward_id}", response_model=WardResponse)
async def get_ward(
    ward_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific ward by ID
    """
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    
    if not ward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ward not found"
        )
    
    return ward


@router.put("/{ward_id}", response_model=WardResponse)
async def update_ward(
    ward_id: UUID,
    ward_update: WardUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a ward
    """
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    
    if not ward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ward not found"
        )
    
    # Update fields
    update_data = ward_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ward, field, value)
    
    ward.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ward)
    
    return ward


@router.delete("/{ward_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ward(
    ward_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a ward
    """
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    
    if not ward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ward not found"
        )
    
    db.delete(ward)
    db.commit()
    
    return None
