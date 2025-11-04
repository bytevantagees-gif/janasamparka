"""
Votebank Engagement API Routes - Agriculture, Business, Youth, Career Guidance, and Community Development
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.votebank_engagement import (
    FarmerProfile, CropRequest, MarketListing, BusinessProfile, BusinessRequest,
    BusinessConnection, YouthProfile, YouthProgram, ProgramParticipation,
    CareerRequest, MentorshipConnection, TrainingProgram, TrainingParticipation,
    CropType, FarmingType, BusinessCategory, BusinessSize, ProgramType, CareerField
)
from app.schemas.votebank_engagement import (
    FarmerProfileCreate, FarmerProfileResponse, CropRequestCreate, CropRequestResponse,
    MarketListingCreate, MarketListingResponse, BusinessProfileCreate, BusinessProfileResponse,
    BusinessRequestCreate, BusinessRequestResponse, BusinessConnectionCreate, BusinessConnectionResponse,
    YouthProfileCreate, YouthProfileResponse, YouthProgramCreate, YouthProgramResponse,
    ProgramParticipationCreate, ProgramParticipationResponse, CareerRequestCreate, CareerRequestResponse,
    MentorshipConnectionCreate, MentorshipConnectionResponse, TrainingProgramCreate, TrainingProgramResponse,
    TrainingParticipationCreate, TrainingParticipationResponse
)

router = APIRouter(tags=["Votebank Engagement"])


# ==================== FARMER & AGRICULTURE MODULE ====================

@router.post("/farmers/profile", response_model=FarmerProfileResponse)
async def create_farmer_profile(
    farmer_data: FarmerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update farmer profile"""
    # Check if profile already exists
    existing_profile = db.query(FarmerProfile).filter(
        FarmerProfile.farmer_id == current_user.id
    ).first()
    
    if existing_profile:
        # Update existing profile
        for key, value in farmer_data.dict().items():
            if hasattr(existing_profile, key):
                setattr(existing_profile, key, value)
        existing_profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    
    # Create new profile
    profile = FarmerProfile(
        id=str(uuid.uuid4()),
        farmer_id=current_user.id,
        constituency_id=current_user.constituency_id,
        **farmer_data.dict()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/farmers/profile", response_model=FarmerProfileResponse)
async def get_farmer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's farmer profile"""
    profile = db.query(FarmerProfile).filter(
        FarmerProfile.farmer_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    return profile


@router.get("/farmers", response_model=List[FarmerProfileResponse])
async def list_farmers(
    ward_id: Optional[str] = Query(None),
    farming_type: Optional[FarmingType] = Query(None),
    crop_type: Optional[CropType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["mla", "moderator", "department_officer"])),
    db: Session = Depends(get_db)
):
    """List farmers in constituency with filters"""
    query = db.query(FarmerProfile).filter(
        FarmerProfile.constituency_id == current_user.constituency_id,
        FarmerProfile.is_active == True
    )
    
    if ward_id:
        query = query.filter(FarmerProfile.ward_id == ward_id)
    if farming_type:
        query = query.filter(FarmerProfile.farming_type == farming_type)
    if crop_type:
        query = query.filter(FarmerProfile.primary_crops.contains([crop_type.value]))
    
    farmers = query.offset(skip).limit(limit).all()
    return farmers


@router.post("/farmers/crop-requests", response_model=CropRequestResponse)
async def create_crop_request(
    request_data: CropRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create crop information or market request"""
    # Get farmer profile
    farmer_profile = db.query(FarmerProfile).filter(
        FarmerProfile.farmer_id == current_user.id
    ).first()
    
    if not farmer_profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    
    request = CropRequest(
        id=str(uuid.uuid4()),
        farmer_id=farmer_profile.id,
        constituency_id=current_user.constituency_id,
        **request_data.dict()
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/farmers/crop-requests", response_model=List[CropRequestResponse])
async def list_crop_requests(
    status: Optional[str] = Query(None),
    crop_type: Optional[CropType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["mla", "moderator", "department_officer"])),
    db: Session = Depends(get_db)
):
    """List crop requests in constituency"""
    query = db.query(CropRequest).filter(
        CropRequest.constituency_id == current_user.constituency_id
    )
    
    if status:
        query = query.filter(CropRequest.status == status)
    if crop_type:
        query = query.filter(CropRequest.crop_type == crop_type)
    
    requests = query.order_by(CropRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.post("/farmers/market-listings", response_model=MarketListingResponse)
async def create_market_listing(
    listing_data: MarketListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create agricultural product market listing"""
    farmer_profile = db.query(FarmerProfile).filter(
        FarmerProfile.farmer_id == current_user.id
    ).first()
    
    if not farmer_profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    
    # Set expiry date (30 days from now)
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    listing = MarketListing(
        id=str(uuid.uuid4()),
        farmer_id=farmer_profile.id,
        constituency_id=current_user.constituency_id,
        expires_at=expires_at,
        **listing_data.dict()
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/farmers/market-listings", response_model=List[MarketListingResponse])
async def list_market_listings(
    crop_type: Optional[CropType] = Query(None),
    is_organic: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List market listings in constituency"""
    query = db.query(MarketListing).filter(
        MarketListing.constituency_id == current_user.constituency_id,
        MarketListing.status == "active",
        MarketListing.expires_at > datetime.utcnow()
    )
    
    if crop_type:
        query = query.filter(MarketListing.crop_type == crop_type)
    if is_organic is not None:
        query = query.filter(MarketListing.is_organic == is_organic)
    if min_price:
        query = query.filter(MarketListing.expected_price >= min_price)
    if max_price:
        query = query.filter(MarketListing.expected_price <= max_price)
    
    listings = query.order_by(MarketListing.created_at.desc()).offset(skip).limit(limit).all()
    return listings


@router.post("/farmers/market-listings/{listing_id}/contact")
async def contact_market_seller(
    listing_id: str,
    message: str,
    contact_info: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Contact seller for market listing"""
    listing = db.query(MarketListing).filter(
        MarketListing.id == listing_id,
        MarketListing.constituency_id == current_user.constituency_id
    ).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Market listing not found")
    
    # Add buyer contact info
    if not listing.interested_buyers:
        listing.interested_buyers = []
    
    buyer_info = {
        "user_id": current_user.id,
        "name": current_user.name,
        "phone": current_user.phone,
        "email": current_user.email,
        "message": message,
        "contact_info": contact_info,
        "contacted_at": datetime.utcnow().isoformat()
    }
    
    listing.interested_buyers.append(buyer_info)
    listing.contacts_count += 1
    
    db.commit()
    return {"message": "Contact information sent to seller successfully"}


# ==================== BUSINESS COMMUNITY MODULE ====================

@router.post("/businesses/profile", response_model=BusinessProfileResponse)
async def create_business_profile(
    business_data: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update business profile"""
    existing_profile = db.query(BusinessProfile).filter(
        BusinessProfile.owner_id == current_user.id
    ).first()
    
    if existing_profile:
        for key, value in business_data.dict().items():
            if hasattr(existing_profile, key):
                setattr(existing_profile, key, value)
        existing_profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    
    profile = BusinessProfile(
        id=str(uuid.uuid4()),
        owner_id=current_user.id,
        constituency_id=current_user.constituency_id,
        **business_data.dict()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/businesses/profile", response_model=BusinessProfileResponse)
async def get_business_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's business profile"""
    profile = db.query(BusinessProfile).filter(
        BusinessProfile.owner_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return profile


@router.get("/businesses", response_model=List[BusinessProfileResponse])
async def list_businesses(
    category: Optional[BusinessCategory] = Query(None),
    size: Optional[BusinessSize] = Query(None),
    ward_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List businesses in constituency"""
    query = db.query(BusinessProfile).filter(
        BusinessProfile.constituency_id == current_user.constituency_id,
        BusinessProfile.is_active == True,
        BusinessProfile.is_verified == True
    )
    
    if category:
        query = query.filter(BusinessProfile.business_category == category)
    if size:
        query = query.filter(BusinessProfile.business_size == size)
    if ward_id:
        query = query.filter(BusinessProfile.ward_id == ward_id)
    
    businesses = query.offset(skip).limit(limit).all()
    return businesses


@router.post("/businesses/requests", response_model=BusinessRequestResponse)
async def create_business_request(
    request_data: BusinessRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create business support request"""
    business_profile = db.query(BusinessProfile).filter(
        BusinessProfile.owner_id == current_user.id
    ).first()
    
    if not business_profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    
    request = BusinessRequest(
        id=str(uuid.uuid4()),
        business_id=business_profile.id,
        constituency_id=current_user.constituency_id,
        **request_data.dict()
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/businesses/requests", response_model=List[BusinessRequestResponse])
async def list_business_requests(
    request_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["mla", "moderator", "department_officer"])),
    db: Session = Depends(get_db)
):
    """List business requests in constituency"""
    query = db.query(BusinessRequest).filter(
        BusinessRequest.constituency_id == current_user.constituency_id
    )
    
    if request_type:
        query = query.filter(BusinessRequest.request_type == request_type)
    if status:
        query = query.filter(BusinessRequest.status == status)
    
    requests = query.order_by(BusinessRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.post("/businesses/network", response_model=BusinessConnectionResponse)
async def create_business_connection(
    connection_data: BusinessConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create business networking connection"""
    business_profile = db.query(BusinessProfile).filter(
        BusinessProfile.owner_id == current_user.id
    ).first()
    
    if not business_profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    
    connection = BusinessConnection(
        id=str(uuid.uuid4()),
        business_id=business_profile.id,
        constituency_id=current_user.constituency_id,
        **connection_data.dict()
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@router.get("/businesses/network", response_model=List[BusinessConnectionResponse])
async def list_business_network(
    connection_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List business networking opportunities"""
    query = db.query(BusinessConnection).filter(
        BusinessConnection.constituency_id == current_user.constituency_id,
        BusinessConnection.status == "active"
    )
    
    if connection_type:
        query = query.filter(BusinessConnection.connection_type == connection_type)
    
    connections = query.order_by(BusinessConnection.created_at.desc()).offset(skip).limit(limit).all()
    return connections


# ==================== YOUTH ENGAGEMENT MODULE ====================

@router.post("/youth/profile", response_model=YouthProfileResponse)
async def create_youth_profile(
    youth_data: YouthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update youth profile"""
    existing_profile = db.query(YouthProfile).filter(
        YouthProfile.youth_id == current_user.id
    ).first()
    
    if existing_profile:
        for key, value in youth_data.dict().items():
            if hasattr(existing_profile, key):
                setattr(existing_profile, key, value)
        existing_profile.updated_at = datetime.utcnow()
        existing_profile.last_active_date = datetime.utcnow()
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    
    profile = YouthProfile(
        id=str(uuid.uuid4()),
        youth_id=current_user.id,
        constituency_id=current_user.constituency_id,
        last_active_date=datetime.utcnow(),
        **youth_data.dict()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/youth/profile", response_model=YouthProfileResponse)
async def get_youth_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's youth profile"""
    profile = db.query(YouthProfile).filter(
        YouthProfile.youth_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Youth profile not found")
    return profile


@router.get("/youth", response_model=List[YouthProfileResponse])
async def list_youth(
    education_level: Optional[str] = Query(None),
    current_status: Optional[str] = Query(None),
    interests: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["mla", "moderator", "department_officer"])),
    db: Session = Depends(get_db)
):
    """List youth in constituency"""
    query = db.query(YouthProfile).filter(
        YouthProfile.constituency_id == current_user.constituency_id,
        YouthProfile.is_active == True
    )
    
    if education_level:
        query = query.filter(YouthProfile.education_level == education_level)
    if current_status:
        query = query.filter(YouthProfile.current_status == current_status)
    if interests:
        query = query.filter(YouthProfile.interests.contains([interests]))
    
    youth = query.offset(skip).limit(limit).all()
    return youth


@router.post("/youth/programs", response_model=YouthProgramResponse)
async def create_youth_program(
    program_data: YouthProgramCreate,
    current_user: User = Depends(require_role(["mla", "moderator"])),
    db: Session = Depends(get_db)
):
    """Create youth development program"""
    program = YouthProgram(
        id=str(uuid.uuid4()),
        constituency_id=current_user.constituency_id,
        organizer_id=current_user.id,
        **program_data.dict()
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.get("/youth/programs", response_model=List[YouthProgramResponse])
async def list_youth_programs(
    program_type: Optional[ProgramType] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List youth programs in constituency"""
    query = db.query(YouthProgram).filter(
        YouthProgram.constituency_id == current_user.constituency_id
    )
    
    if program_type:
        query = query.filter(YouthProgram.program_type == program_type)
    if status:
        query = query.filter(YouthProgram.status == status)
    
    programs = query.order_by(YouthProgram.start_date.desc()).offset(skip).limit(limit).all()
    return programs


@router.post("/youth/programs/{program_id}/apply")
async def apply_to_youth_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply to youth program"""
    # Get youth profile
    youth_profile = db.query(YouthProfile).filter(
        YouthProfile.youth_id == current_user.id
    ).first()
    
    if not youth_profile:
        raise HTTPException(status_code=404, detail="Youth profile not found")
    
    # Check if already applied
    existing_application = db.query(ProgramParticipation).filter(
        ProgramParticipation.youth_id == youth_profile.id,
        ProgramParticipation.program_id == program_id
    ).first()
    
    if existing_application:
        raise HTTPException(status_code=400, detail="Already applied to this program")
    
    # Create participation
    participation = ProgramParticipation(
        id=str(uuid.uuid4()),
        youth_id=youth_profile.id,
        program_id=program_id,
        constituency_id=current_user.constituency_id
    )
    db.add(participation)
    
    # Update program application count
    program = db.query(YouthProgram).filter(YouthProgram.id == program_id).first()
    if program:
        program.application_count += 1
    
    db.commit()
    return {"message": "Application submitted successfully"}


@router.get("/youth/programs/my-applications", response_model=List[ProgramParticipationResponse])
async def list_my_program_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's program applications"""
    youth_profile = db.query(YouthProfile).filter(
        YouthProfile.youth_id == current_user.id
    ).first()
    
    if not youth_profile:
        raise HTTPException(status_code=404, detail="Youth profile not found")
    
    applications = db.query(ProgramParticipation).filter(
        ProgramParticipation.youth_id == youth_profile.id
    ).order_by(ProgramParticipation.application_date.desc()).all()
    return applications


# ==================== CAREER GUIDANCE MODULE ====================

@router.post("/youth/career-requests", response_model=CareerRequestResponse)
async def create_career_request(
    request_data: CareerRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create career guidance request"""
    youth_profile = db.query(YouthProfile).filter(
        YouthProfile.youth_id == current_user.id
    ).first()
    
    if not youth_profile:
        raise HTTPException(status_code=404, detail="Youth profile not found")
    
    request = CareerRequest(
        id=str(uuid.uuid4()),
        youth_id=youth_profile.id,
        constituency_id=current_user.constituency_id,
        **request_data.dict()
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/youth/career-requests", response_model=List[CareerRequestResponse])
async def list_career_requests(
    career_field: Optional[CareerField] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["mla", "moderator", "department_officer"])),
    db: Session = Depends(get_db)
):
    """List career guidance requests"""
    query = db.query(CareerRequest).filter(
        CareerRequest.constituency_id == current_user.constituency_id
    )
    
    if career_field:
        query = query.filter(CareerRequest.career_field == career_field)
    if status:
        query = query.filter(CareerRequest.status == status)
    
    requests = query.order_by(CareerRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.post("/youth/mentorship", response_model=MentorshipConnectionResponse)
async def create_mentorship_connection(
    mentorship_data: MentorshipConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create mentorship connection"""
    youth_profile = db.query(YouthProfile).filter(
        YouthProfile.youth_id == current_user.id
    ).first()
    
    if not youth_profile:
        raise HTTPException(status_code=404, detail="Youth profile not found")
    
    connection = MentorshipConnection(
        id=str(uuid.uuid4()),
        youth_id=youth_profile.id,
        constituency_id=current_user.constituency_id,
        **mentorship_data.dict()
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@router.get("/youth/mentorship", response_model=List[MentorshipConnectionResponse])
async def list_mentorship_opportunities(
    mentorship_area: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List mentorship opportunities"""
    query = db.query(MentorshipConnection).filter(
        MentorshipConnection.constituency_id == current_user.constituency_id,
        MentorshipConnection.status == "active"
    )
    
    if mentorship_area:
        query = query.filter(MentorshipConnection.mentorship_area == mentorship_area)
    
    connections = query.order_by(MentorshipConnection.created_at.desc()).offset(skip).limit(limit).all()
    return connections


# ==================== TRAINING & SKILL DEVELOPMENT MODULE ====================

@router.post("/training/programs", response_model=TrainingProgramResponse)
async def create_training_program(
    training_data: TrainingProgramCreate,
    current_user: User = Depends(require_role(["mla", "moderator", "department_officer"])),
    db: Session = Depends(get_db)
):
    """Create training program"""
    program = TrainingProgram(
        id=str(uuid.uuid4()),
        constituency_id=current_user.constituency_id,
        trainer_id=current_user.id,
        **training_data.dict()
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.get("/training/programs", response_model=List[TrainingProgramResponse])
async def list_training_programs(
    training_category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_free: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List training programs"""
    query = db.query(TrainingProgram).filter(
        TrainingProgram.constituency_id == current_user.constituency_id
    )
    
    if training_category:
        query = query.filter(TrainingProgram.training_category == training_category)
    if status:
        query = query.filter(TrainingProgram.status == status)
    if is_free is not None:
        query = query.filter(TrainingProgram.is_free == is_free)
    
    programs = query.order_by(TrainingProgram.start_date.desc()).offset(skip).limit(limit).all()
    return programs


@router.post("/training/programs/{program_id}/enroll")
async def enroll_in_training_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in training program"""
    # Get farmer profile (farmers are primary target for training)
    farmer_profile = db.query(FarmerProfile).filter(
        FarmerProfile.farmer_id == current_user.id
    ).first()
    
    if not farmer_profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    
    # Check if already enrolled
    existing_enrollment = db.query(TrainingParticipation).filter(
        TrainingParticipation.participant_id == farmer_profile.id,
        TrainingParticipation.training_id == program_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled in this training")
    
    # Create participation
    participation = TrainingParticipation(
        id=str(uuid.uuid4()),
        participant_id=farmer_profile.id,
        training_id=program_id,
        constituency_id=current_user.constituency_id
    )
    db.add(participation)
    
    # Update program enrollment count
    program = db.query(TrainingProgram).filter(TrainingProgram.id == program_id).first()
    if program:
        program.enrollment_count += 1
    
    db.commit()
    return {"message": "Enrollment successful"}


@router.get("/training/my-enrollments", response_model=List[TrainingParticipationResponse])
async def list_my_training_enrollments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's training enrollments"""
    farmer_profile = db.query(FarmerProfile).filter(
        FarmerProfile.farmer_id == current_user.id
    ).first()
    
    if not farmer_profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    
    enrollments = db.query(TrainingParticipation).filter(
        TrainingParticipation.participant_id == farmer_profile.id
    ).order_by(TrainingParticipation.enrollment_date.desc()).all()
    return enrollments


# ==================== VOTEBANK ANALYTICS DASHBOARD ====================

@router.get("/analytics/dashboard")
async def get_votebank_analytics(
    current_user: User = Depends(require_role(["admin", "mla", "moderator"])),
    db: Session = Depends(get_db)
):
    """Get comprehensive votebank engagement analytics"""
    constituency_id = current_user.constituency_id
    
    # Build base queries
    farmer_query = db.query(FarmerProfile)
    crop_request_query = db.query(CropRequest)
    market_listing_query = db.query(MarketListing)
    business_query = db.query(BusinessProfile)
    business_request_query = db.query(BusinessRequest)
    business_connection_query = db.query(BusinessConnection)
    youth_query = db.query(YouthProfile)
    youth_program_query = db.query(YouthProgram)
    career_request_query = db.query(CareerRequest)
    mentorship_query = db.query(MentorshipConnection)
    training_program_query = db.query(TrainingProgram)
    training_participation_query = db.query(TrainingParticipation).join(TrainingProgram)
    
    # Apply constituency filter only if user has a constituency (non-admin)
    if constituency_id:
        farmer_query = farmer_query.filter(FarmerProfile.constituency_id == constituency_id)
        crop_request_query = crop_request_query.filter(CropRequest.constituency_id == constituency_id)
        market_listing_query = market_listing_query.filter(MarketListing.constituency_id == constituency_id)
        business_query = business_query.filter(BusinessProfile.constituency_id == constituency_id)
        business_request_query = business_request_query.filter(BusinessRequest.constituency_id == constituency_id)
        business_connection_query = business_connection_query.filter(BusinessConnection.constituency_id == constituency_id)
        youth_query = youth_query.filter(YouthProfile.constituency_id == constituency_id)
        youth_program_query = youth_program_query.filter(YouthProgram.constituency_id == constituency_id)
        career_request_query = career_request_query.filter(CareerRequest.constituency_id == constituency_id)
        mentorship_query = mentorship_query.filter(MentorshipConnection.constituency_id == constituency_id)
        training_program_query = training_program_query.filter(TrainingProgram.constituency_id == constituency_id)
        training_participation_query = training_participation_query.filter(TrainingProgram.constituency_id == constituency_id)
    
    # Farmer Analytics
    total_farmers = farmer_query.filter(FarmerProfile.is_active == True).count()
    
    verified_farmers = farmer_query.filter(FarmerProfile.is_verified == True).count()
    
    pending_crop_requests = crop_request_query.filter(CropRequest.status == "pending").count()
    
    active_market_listings = market_listing_query.filter(MarketListing.status == "active").count()
    
    # Business Analytics
    total_businesses = business_query.filter(
        BusinessProfile.is_active == True,
        BusinessProfile.is_verified == True
    ).count()
    
    business_requests = business_request_query.filter(BusinessRequest.status == "pending").count()
    
    # Youth Analytics
    total_youth = youth_query.filter(YouthProfile.is_active == True).count()
    
    youth_programs = youth_program_query.filter(
        YouthProgram.status.in_(["upcoming", "ongoing"])
    ).count()
    
    career_requests = career_request_query.filter(CareerRequest.status == "pending").count()
    
    # Training Analytics
    training_programs = training_program_query.filter(
        TrainingProgram.status.in_(["upcoming", "ongoing"])
    ).count()
    
    total_trainees = training_participation_query.filter(
        TrainingParticipation.enrollment_status == "enrolled"
    ).count()
    
    return {
        "farmer_engagement": {
            "total_farmers": total_farmers,
            "verified_farmers": verified_farmers,
            "verification_rate": (verified_farmers / total_farmers * 100) if total_farmers > 0 else 0,
            "pending_crop_requests": pending_crop_requests,
            "active_market_listings": active_market_listings
        },
        "business_engagement": {
            "total_businesses": total_businesses,
            "pending_requests": business_requests,
            "active_connections": business_connection_query.filter(
                BusinessConnection.status == "active"
            ).count()
        },
        "youth_engagement": {
            "total_youth": total_youth,
            "active_programs": youth_programs,
            "career_requests": career_requests,
            "mentorship_connections": mentorship_query.filter(
                MentorshipConnection.status == "active"
            ).count()
        },
        "training_engagement": {
            "active_programs": training_programs,
            "total_trainees": total_trainees,
            "completion_rate": 0  # Will be calculated based on completed trainings
        },
        "overall_engagement": {
            "total_constituents_engaged": total_farmers + total_businesses + total_youth,
            "pending_requests": pending_crop_requests + business_requests + career_requests,
            "active_programs": youth_programs + training_programs
        }
    }


@router.get("/analytics/votebank-potential")
async def get_votebank_potential(
    current_user: User = Depends(require_role(["mla"])),
    db: Session = Depends(get_db)
):
    """Get votebank potential analysis"""
    constituency_id = current_user.constituency_id
    
    # Calculate potential votes from each segment
    farmer_votes = db.query(FarmerProfile).filter(
        FarmerProfile.constituency_id == constituency_id,
        FarmerProfile.is_active == True
    ).count() * 5  # Each farmer influences 5 family members
    
    business_votes = db.query(BusinessProfile).filter(
        BusinessProfile.constituency_id == constituency_id,
        BusinessProfile.is_active == True
    ).count() * 10  # Each business influences 10 people (employees, family, customers)
    
    youth_votes = db.query(YouthProfile).filter(
        YouthProfile.constituency_id == constituency_id,
        YouthProfile.is_active == True
    ).count() * 3  # Each youth influences 3 friends/family members
    
    # Calculate satisfaction scores based on response times and resolution rates
    farmer_satisfaction = min(95, 70 + db.query(CropRequest).filter(
        CropRequest.constituency_id == constituency_id,
        CropRequest.status == "resolved"
    ).count() * 2)
    
    business_satisfaction = min(95, 70 + db.query(BusinessRequest).filter(
        BusinessRequest.constituency_id == constituency_id,
        BusinessRequest.status == "resolved"
    ).count() * 3)
    
    youth_satisfaction = min(95, 70 + db.query(CareerRequest).filter(
        CareerRequest.constituency_id == constituency_id,
        CareerRequest.status == "resolved"
    ).count() * 4)
    
    return {
        "votebank_potential": {
            "farmer_segment": {
                "direct_constituents": db.query(FarmerProfile).filter(
                    FarmerProfile.constituency_id == constituency_id,
                    FarmerProfile.is_active == True
                ).count(),
                "potential_votes": farmer_votes,
                "satisfaction_score": farmer_satisfaction,
                "loyalty_factor": 0.8
            },
            "business_segment": {
                "direct_constituents": db.query(BusinessProfile).filter(
                    BusinessProfile.constituency_id == constituency_id,
                    BusinessProfile.is_active == True
                ).count(),
                "potential_votes": business_votes,
                "satisfaction_score": business_satisfaction,
                "loyalty_factor": 0.7
            },
            "youth_segment": {
                "direct_constituents": db.query(YouthProfile).filter(
                    YouthProfile.constituency_id == constituency_id,
                    YouthProfile.is_active == True
                ).count(),
                "potential_votes": youth_votes,
                "satisfaction_score": youth_satisfaction,
                "loyalty_factor": 0.6
            }
        },
        "total_potential_votes": farmer_votes + business_votes + youth_votes,
        "overall_satisfaction": (farmer_satisfaction + business_satisfaction + youth_satisfaction) / 3,
        "recommendations": [
            "Focus on resolving pending crop requests to improve farmer satisfaction",
            "Create more business networking events to strengthen business votebank",
            "Launch career guidance programs to capture youth votebank",
            "Increase training programs for skill development"
        ]
    }
