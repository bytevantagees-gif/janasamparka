"""
Panchayat Raj API Router - Gram, Taluk, and Zilla Panchayats
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.user import User, UserRole
from app.models.panchayat import GramPanchayat, TalukPanchayat, ZillaPanchayat
from app.models.constituency import Constituency
from app.models.complaint import Complaint
from app.schemas import gram_panchayat as gp_schemas
from app.schemas import taluk_panchayat as tp_schemas
from app.schemas import zilla_panchayat as zp_schemas


router = APIRouter(prefix="/api/panchayats", tags=["panchayats"])


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_access_filter(user: User, db: Session):
    """
    Get filtering conditions based on user's role and assigned panchayat
    """
    # Admin sees everything
    if user.role == UserRole.ADMIN:
        return None
    
    # MLA sees entire constituency
    if user.role == UserRole.MLA:
        return {"constituency_id": user.constituency_id}
    
    # Zilla Panchayat level users
    if user.role in [UserRole.ZILLA_PANCHAYAT_OFFICER, UserRole.ZP_PRESIDENT]:
        if not user.zilla_panchayat_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not assigned to any Zilla Panchayat"
            )
        return {"zilla_panchayat_id": user.zilla_panchayat_id}
    
    # Taluk Panchayat level users
    if user.role in [UserRole.TALUK_PANCHAYAT_OFFICER, UserRole.TP_PRESIDENT]:
        if not user.taluk_panchayat_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not assigned to any Taluk Panchayat"
            )
        return {"taluk_panchayat_id": user.taluk_panchayat_id}
    
    # Gram Panchayat level users (PDO, VA, GP President)
    if user.role in [UserRole.PDO, UserRole.VILLAGE_ACCOUNTANT, UserRole.GP_PRESIDENT]:
        if not user.gram_panchayat_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not assigned to any Gram Panchayat"
            )
        return {"gram_panchayat_id": user.gram_panchayat_id}
    
    # Other roles (officers, moderators, auditors) see constituency level
    if user.constituency_id:
        return {"constituency_id": user.constituency_id}
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User not assigned to any administrative unit"
    )


# ============================================
# GRAM PANCHAYAT ENDPOINTS
# ============================================

@router.get("/gram", response_model=List[gp_schemas.GramPanchayatResponse])
def list_gram_panchayats(
    taluk_panchayat_id: Optional[UUID] = None,
    constituency_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id)
):
    """
    List Gram Panchayats with filtering
    Non-admin users can only see Gram Panchayats from their own constituency
    """
    # Build query
    query = db.query(GramPanchayat)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(GramPanchayat.constituency_id == constituency_filter)
    
    # Apply filters
    if taluk_panchayat_id:
        query = query.filter(GramPanchayat.taluk_panchayat_id == taluk_panchayat_id)
    if constituency_id and not constituency_filter:  # Only allow explicit filter if admin
        query = query.filter(GramPanchayat.constituency_id == constituency_id)
    if is_active is not None:
        query = query.filter(GramPanchayat.is_active == is_active)
    
    # Pagination
    gram_panchayats = query.offset(skip).limit(limit).all()
    
    return gram_panchayats


@router.get("/gram/{gp_id}", response_model=gp_schemas.GramPanchayatWithHierarchy)
def get_gram_panchayat(
    gp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Get detailed information about a specific Gram Panchayat with hierarchy
    """
    # Get GP
    gp = db.query(GramPanchayat).filter(GramPanchayat.id == gp_id).first()
    
    if not gp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gram Panchayat not found"
        )
    
    # Get statistics
    total_users = db.query(func.count(User.id)).filter(User.gram_panchayat_id == gp_id).scalar() or 0
    
    total_submissions = db.query(func.count(Complaint.id)).filter(Complaint.gram_panchayat_id == gp_id).scalar() or 0
    
    pending_submissions = db.query(func.count(Complaint.id)).filter(
        and_(
            Complaint.gram_panchayat_id == gp_id,
            Complaint.status.in_(["submitted", "in_progress"])
        )
    ).scalar() or 0
    
    # Build response with hierarchy
    response = gp_schemas.GramPanchayatWithHierarchy.model_validate(gp)
    response.total_users = total_users
    response.total_submissions = total_submissions
    response.pending_submissions = pending_submissions
    
    if gp.taluk_panchayat:
        response.taluk_panchayat_name = gp.taluk_panchayat.name
        if gp.taluk_panchayat.zilla_panchayat:
            response.zilla_panchayat_name = gp.taluk_panchayat.zilla_panchayat.name
    
    if gp.constituency:
        response.constituency_name = gp.constituency.name
        response.mla_name = gp.constituency.mla_name
    
    return response


@router.post("/gram", response_model=gp_schemas.GramPanchayatResponse)
def create_gram_panchayat(
    gp_data: gp_schemas.GramPanchayatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Create a new Gram Panchayat (Admin only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create Gram Panchayats"
        )
    
    # Check if code already exists
    existing = db.query(GramPanchayat).filter(GramPanchayat.code == gp_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gram Panchayat with this code already exists"
        )
    
    # Create GP
    gp = GramPanchayat(**gp_data.model_dump())
    db.add(gp)
    db.commit()
    db.refresh(gp)
    
    return gp


@router.patch("/gram/{gp_id}", response_model=gp_schemas.GramPanchayatResponse)
def update_gram_panchayat(
    gp_id: UUID,
    gp_data: gp_schemas.GramPanchayatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Update Gram Panchayat details (Admin or TP Officer)
    """
    # Get GP
    gp = db.query(GramPanchayat).filter(GramPanchayat.id == gp_id).first()
    if not gp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.TALUK_PANCHAYAT_OFFICER, UserRole.TP_PRESIDENT]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # Update fields
    for field, value in gp_data.model_dump(exclude_unset=True).items():
        setattr(gp, field, value)
    
    db.commit()
    db.refresh(gp)
    
    return gp


# ============================================
# TALUK PANCHAYAT ENDPOINTS
# ============================================

@router.get("/taluk", response_model=List[tp_schemas.TalukPanchayatResponse])
def list_taluk_panchayats(
    constituency_id: Optional[UUID] = None,
    zilla_panchayat_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    List Taluk Panchayats with filtering
    """
    # Build query
    query = db.query(TalukPanchayat)
    
    # Apply filters
    if constituency_id:
        query = query.filter(TalukPanchayat.constituency_id == constituency_id)
    if zilla_panchayat_id:
        query = query.filter(TalukPanchayat.zilla_panchayat_id == zilla_panchayat_id)
    if is_active is not None:
        query = query.filter(TalukPanchayat.is_active == is_active)
    
    # Pagination
    return query.offset(skip).limit(limit).all()


@router.get("/taluk/{tp_id}", response_model=tp_schemas.TalukPanchayatWithHierarchy)
def get_taluk_panchayat(
    tp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Get detailed information about a Taluk Panchayat
    """
    tp = db.query(TalukPanchayat).filter(TalukPanchayat.id == tp_id).first()
    
    if not tp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Get statistics
    gram_panchayats_count = db.query(func.count(GramPanchayat.id)).filter(
        GramPanchayat.taluk_panchayat_id == tp_id
    ).scalar() or 0
    
    total_users = db.query(func.count(User.id)).filter(User.taluk_panchayat_id == tp_id).scalar() or 0
    
    # Build response
    response = tp_schemas.TalukPanchayatWithHierarchy.model_validate(tp)
    response.gram_panchayats_count = gram_panchayats_count
    response.total_users = total_users
    
    if tp.zilla_panchayat:
        response.zilla_panchayat_name = tp.zilla_panchayat.name
    if tp.constituency:
        response.constituency_name = tp.constituency.name
        response.mla_name = tp.constituency.mla_name
    
    return response


# ============================================
# ZILLA PANCHAYAT ENDPOINTS
# ============================================

@router.get("/zilla", response_model=List[zp_schemas.ZillaPanchayatResponse])
def list_zilla_panchayats(
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    List Zilla Panchayats
    """
    # Build query
    query = db.query(ZillaPanchayat)
    
    # Access control for ZP officers
    if current_user.role in [UserRole.ZILLA_PANCHAYAT_OFFICER, UserRole.ZP_PRESIDENT]:
        if current_user.zilla_panchayat_id:
            query = query.filter(ZillaPanchayat.id == current_user.zilla_panchayat_id)
    
    if is_active is not None:
        query = query.filter(ZillaPanchayat.is_active == is_active)
    
    # Pagination
    return query.offset(skip).limit(limit).all()


@router.get("/zilla/{zp_id}", response_model=zp_schemas.ZillaPanchayatWithHierarchy)
def get_zilla_panchayat(
    zp_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Get detailed information about a Zilla Panchayat
    """
    zp = db.query(ZillaPanchayat).filter(ZillaPanchayat.id == zp_id).first()
    
    if not zp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Get counts
    taluk_count = db.query(func.count(TalukPanchayat.id)).filter(
        TalukPanchayat.zilla_panchayat_id == zp_id
    ).scalar() or 0
    
    gram_count = db.query(func.count(GramPanchayat.id)).join(TalukPanchayat).filter(
        TalukPanchayat.zilla_panchayat_id == zp_id
    ).scalar() or 0
    
    response = zp_schemas.ZillaPanchayatWithHierarchy.model_validate(zp)
    response.taluk_panchayats_count = taluk_count
    response.gram_panchayats_count = gram_count
    
    return response


# ============================================
# HIERARCHY ENDPOINT
# ============================================

@router.get("/hierarchy/{constituency_id}", response_model=zp_schemas.PanchayatHierarchy)
def get_panchayat_hierarchy(
    constituency_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Get complete Panchayat hierarchy for a constituency
    """
    # Get constituency
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    if not constituency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Get Taluk Panchayats
    taluk_panchayats = db.query(TalukPanchayat).filter(
        TalukPanchayat.constituency_id == constituency_id
    ).all()
    
    # Build hierarchy
    hierarchy_data = []
    zp = None
    total_gps = 0
    
    for tp in taluk_panchayats:
        if not zp and tp.zilla_panchayat:
            zp = tp.zilla_panchayat
        
        # Get GPs for this TP
        gps = db.query(GramPanchayat).filter(GramPanchayat.taluk_panchayat_id == tp.id).all()
        total_gps += len(gps)
        
        hierarchy_data.append({
            "taluk_panchayat": tp_schemas.TalukPanchayatResponse.model_validate(tp),
            "gram_panchayats": [gp_schemas.GramPanchayatResponse.model_validate(gp) for gp in gps]
        })
    
    return zp_schemas.PanchayatHierarchy(
        constituency_id=constituency_id,
        constituency_name=constituency.name,
        mla_name=constituency.mla_name,
        zilla_panchayat=zp_schemas.ZillaPanchayatResponse.model_validate(zp) if zp else None,
        taluk_panchayats=hierarchy_data,
        total_gram_panchayats=total_gps
    )
