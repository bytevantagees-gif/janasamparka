"""
Votebank Engagement Pydantic Schemas - Agriculture, Business, Youth, Career Guidance, and Community Development
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.votebank_engagement import (
    CropType, FarmingType, BusinessCategory, BusinessSize, 
    ProgramType, CareerField
)


# ==================== FARMER & AGRICULTURE SCHEMAS ====================

class FarmerProfileBase(BaseModel):
    land_area_acres: Optional[float] = None
    land_area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    water_source: Optional[str] = None
    irrigation_type: Optional[str] = None
    farming_type: Optional[FarmingType] = None
    primary_crops: Optional[List[str]] = []
    secondary_crops: Optional[List[str]] = []
    livestock_count: Optional[Dict[str, int]] = {}
    farm_equipment: Optional[List[str]] = []
    government_schemes: Optional[List[str]] = []
    mla_support_received: Optional[List[str]] = []
    insurance_policies: Optional[Dict[str, Any]] = {}
    farm_address: Optional[str] = None
    farm_latitude: Optional[str] = None
    farm_longitude: Optional[str] = None
    preferred_language: Optional[str] = "kannada"
    is_verified: Optional[bool] = False
    priority_farmer: Optional[bool] = False

class FarmerProfileCreate(FarmerProfileBase):
    ward_id: Optional[str] = None

class FarmerProfileResponse(FarmerProfileBase):
    id: str
    farmer_id: str
    constituency_id: str
    ward_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_visit_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CropRequestBase(BaseModel):
    crop_type: CropType
    crop_name: str
    variety: Optional[str] = None
    expected_harvest_date: Optional[datetime] = None
    current_market_price: Optional[float] = None
    expected_market_price: Optional[float] = None
    target_market: Optional[str] = None
    request_type: Optional[str] = "price_info"
    quantity_available: Optional[float] = None
    quality_grade: Optional[str] = None
    priority: Optional[str] = "medium"

class CropRequestCreate(CropRequestBase):
    pass

class CropRequestResponse(CropRequestBase):
    id: str
    farmer_id: str
    constituency_id: str
    status: str
    buyer_contacts: Optional[List[Dict[str, Any]]] = []
    market_suggestions: Optional[List[str]] = []
    mla_assistance: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MarketListingBase(BaseModel):
    crop_type: CropType
    product_name: str
    variety: Optional[str] = None
    quantity: float
    unit: Optional[str] = "kg"
    quality_grade: Optional[str] = None
    is_organic: Optional[bool] = False
    certification: Optional[str] = None
    expected_price: float
    minimum_price: Optional[float] = None
    price_negotiable: Optional[bool] = True
    farm_location: Optional[str] = None
    delivery_available: Optional[bool] = False
    delivery_radius_km: Optional[int] = None
    product_photos: Optional[List[str]] = []
    quality_videos: Optional[List[str]] = []
    certificates: Optional[List[str]] = []

class MarketListingCreate(MarketListingBase):
    pass

class MarketListingResponse(MarketListingBase):
    id: str
    farmer_id: str
    constituency_id: str
    status: str
    featured_listing: bool
    expires_at: datetime
    interested_buyers: Optional[List[Dict[str, Any]]] = []
    views_count: int
    contacts_count: int
    created_at: datetime
    updated_at: datetime
    sold_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== BUSINESS COMMUNITY SCHEMAS ====================

class BusinessProfileBase(BaseModel):
    business_name: str
    business_category: BusinessCategory
    business_size: Optional[BusinessSize] = None
    registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    license_type: Optional[str] = None
    license_expiry: Optional[datetime] = None
    year_established: Optional[int] = None
    employee_count: Optional[int] = None
    annual_turnover: Optional[float] = None
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    website: Optional[str] = None
    business_latitude: Optional[str] = None
    business_longitude: Optional[str] = None
    mla_support_received: Optional[List[str]] = []
    government_schemes: Optional[List[str]] = []
    bank_loans: Optional[Dict[str, Any]] = {}
    business_associations: Optional[List[str]] = []
    partnership_interests: Optional[List[str]] = []

class BusinessProfileCreate(BusinessProfileBase):
    ward_id: Optional[str] = None

class BusinessProfileResponse(BusinessProfileBase):
    id: str
    owner_id: str
    constituency_id: str
    ward_id: Optional[str] = None
    is_verified: bool
    is_active: bool
    featured_business: bool
    created_at: datetime
    updated_at: datetime
    last_verification_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BusinessRequestBase(BaseModel):
    request_type: str
    title: str
    description: str
    funding_amount: Optional[float] = None
    partnership_type: Optional[str] = None
    license_type: Optional[str] = None
    market_expansion: Optional[str] = None
    urgency_level: Optional[str] = "medium"
    expected_resolution: Optional[datetime] = None
    priority: Optional[str] = "medium"
    documents: Optional[List[str]] = []
    presentations: Optional[List[str]] = []

class BusinessRequestCreate(BusinessRequestBase):
    pass

class BusinessRequestResponse(BusinessRequestBase):
    id: str
    business_id: str
    constituency_id: str
    status: str
    mla_assistance: Optional[str] = None
    government_schemes_suggested: Optional[List[str]] = []
    potential_partners: Optional[List[Dict[str, Any]]] = []
    funding_sources: Optional[List[Dict[str, Any]]] = []
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BusinessConnectionBase(BaseModel):
    connected_business_id: Optional[str] = None
    connection_type: Optional[str] = None
    collaboration_interest: Optional[str] = None
    looking_for: Optional[str] = None
    offering: Optional[str] = None

class BusinessConnectionCreate(BusinessConnectionBase):
    pass

class BusinessConnectionResponse(BusinessConnectionBase):
    id: str
    business_id: str
    constituency_id: str
    status: str
    connection_strength: str
    last_interaction_date: Optional[datetime] = None
    interaction_count: int
    successful_collaborations: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== YOUTH ENGAGEMENT SCHEMAS ====================

class YouthProfileBase(BaseModel):
    date_of_birth: Optional[datetime] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    current_status: Optional[str] = None
    technical_skills: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    hobbies: Optional[List[str]] = []
    career_goals: Optional[str] = None
    preferred_industries: Optional[List[str]] = []
    job_search_status: Optional[str] = None
    entrepreneur_interest: Optional[bool] = False
    volunteer_interest: Optional[bool] = False
    social_issues: Optional[List[str]] = []
    leadership_roles: Optional[List[str]] = []
    preferred_language: Optional[str] = "kannada"
    notification_preferences: Optional[Dict[str, bool]] = {}

class YouthProfileCreate(YouthProfileBase):
    ward_id: Optional[str] = None

class YouthProfileResponse(YouthProfileBase):
    id: str
    youth_id: str
    constituency_id: str
    ward_id: Optional[str] = None
    is_verified: bool
    is_active: bool
    featured_youth: bool
    created_at: datetime
    updated_at: datetime
    last_active_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class YouthProgramBase(BaseModel):
    title: str
    description: str
    program_type: ProgramType
    partner_organizations: Optional[List[str]] = []
    start_date: datetime
    end_date: datetime
    application_deadline: Optional[datetime] = None
    duration_weeks: Optional[int] = None
    max_participants: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    education_requirements: Optional[str] = None
    skill_requirements: Optional[List[str]] = []
    venue: Optional[str] = None
    is_online: Optional[bool] = False
    is_hybrid: Optional[bool] = False
    meeting_link: Optional[str] = None
    benefits: Optional[List[str]] = []
    certification_offered: Optional[bool] = False
    certificate_type: Optional[str] = None
    placement_assistance: Optional[bool] = False
    stipend_amount: Optional[float] = None
    program_photos: Optional[List[str]] = []
    program_videos: Optional[List[str]] = []
    resource_materials: Optional[List[str]] = []

class YouthProgramCreate(YouthProgramBase):
    pass

class YouthProgramResponse(YouthProgramBase):
    id: str
    constituency_id: str
    organizer_id: str
    status: str
    is_featured: bool
    application_count: int
    selected_count: int
    completion_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgramParticipationBase(BaseModel):
    pass

class ProgramParticipationCreate(ProgramParticipationBase):
    pass

class ProgramParticipationResponse(ProgramParticipationBase):
    id: str
    youth_id: str
    program_id: str
    constituency_id: str
    application_date: datetime
    application_status: str
    selection_date: Optional[datetime] = None
    attendance_percentage: Optional[float] = None
    completion_status: Optional[str] = None
    completion_date: Optional[datetime] = None
    performance_rating: Optional[str] = None
    skills_acquired: Optional[List[str]] = []
    projects_completed: Optional[List[str]] = []
    youth_feedback: Optional[str] = None
    organizer_feedback: Optional[str] = None
    certificate_issued: bool
    certificate_url: Optional[str] = None
    placement_status: Optional[str] = None
    placement_company: Optional[str] = None
    startup_founded: bool
    startup_details: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CAREER GUIDANCE SCHEMAS ====================

class CareerRequestBase(BaseModel):
    career_field: CareerField
    request_type: str
    title: str
    description: str
    current_education: Optional[str] = None
    target_companies: Optional[List[str]] = []
    salary_expectation: Optional[float] = None
    preferred_location: Optional[str] = None
    relevant_skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    work_experience: Optional[List[Dict[str, Any]]] = []
    portfolio_url: Optional[str] = None
    priority: Optional[str] = "medium"
    urgency_level: Optional[str] = "medium"
    resume_url: Optional[str] = None
    certificates_urls: Optional[List[str]] = []

class CareerRequestCreate(CareerRequestBase):
    pass

class CareerRequestResponse(CareerRequestBase):
    id: str
    youth_id: str
    constituency_id: str
    status: str
    guidance_provided: Optional[str] = None
    training_suggested: Optional[List[str]] = []
    job_opportunities: Optional[List[Dict[str, Any]]] = []
    internship_opportunities: Optional[List[Dict[str, Any]]] = []
    mentor_assigned: Optional[str] = None
    placement_achieved: bool
    placed_company: Optional[str] = None
    placed_position: Optional[str] = None
    placed_salary: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MentorshipConnectionBase(BaseModel):
    mentor_id: str
    mentorship_area: Optional[str] = None
    goals: Optional[List[str]] = []
    duration_months: Optional[int] = None

class MentorshipConnectionCreate(MentorshipConnectionBase):
    pass

class MentorshipConnectionResponse(MentorshipConnectionBase):
    id: str
    youth_id: str
    constituency_id: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    session_count: int
    last_session_date: Optional[datetime] = None
    total_hours: float
    progress_notes: Optional[str] = None
    achievements: Optional[List[str]] = []
    youth_feedback: Optional[str] = None
    mentor_feedback: Optional[str] = None
    goals_achieved: int
    career_progress: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== TRAINING & SKILL DEVELOPMENT SCHEMAS ====================

class TrainingProgramBase(BaseModel):
    title: str
    description: str
    training_category: Optional[str] = None
    training_partner: Optional[str] = None
    start_date: datetime
    end_date: datetime
    duration_hours: Optional[int] = None
    session_frequency: Optional[str] = None
    max_participants: Optional[int] = None
    min_participants: Optional[int] = None
    prerequisites: Optional[List[str]] = []
    venue: Optional[str] = None
    is_online: Optional[bool] = False
    meeting_link: Optional[str] = None
    certification_offered: Optional[bool] = False
    certificate_issuer: Optional[str] = None
    training_cost: Optional[float] = None
    cost_sponsorship: Optional[Dict[str, Any]] = {}
    status: Optional[str] = "upcoming"
    is_free: Optional[bool] = True

class TrainingProgramCreate(TrainingProgramBase):
    pass

class TrainingProgramResponse(TrainingProgramBase):
    id: str
    constituency_id: str
    trainer_id: str
    enrollment_count: int
    completion_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TrainingParticipationBase(BaseModel):
    pass

class TrainingParticipationCreate(TrainingParticipationBase):
    pass

class TrainingParticipationResponse(TrainingParticipationBase):
    id: str
    participant_id: str
    training_id: str
    constituency_id: str
    enrollment_date: datetime
    enrollment_status: str
    completion_date: Optional[datetime] = None
    attendance_percentage: Optional[float] = None
    assessment_score: Optional[float] = None
    skills_acquired: Optional[List[str]] = []
    participant_feedback: Optional[str] = None
    trainer_feedback: Optional[str] = None
    certificate_issued: bool
    certificate_url: Optional[str] = None
    income_improvement: Optional[float] = None
    business_improvement: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ANALYTICS SCHEMAS ====================

class VotebankAnalyticsResponse(BaseModel):
    farmer_engagement: Dict[str, Any]
    business_engagement: Dict[str, Any]
    youth_engagement: Dict[str, Any]
    training_engagement: Dict[str, Any]
    overall_engagement: Dict[str, Any]

class VotebankPotentialResponse(BaseModel):
    votebank_potential: Dict[str, Any]
    total_potential_votes: int
    overall_satisfaction: float
    recommendations: List[str]


# ==================== VALIDATION HELPERS ====================

@validator('land_area_acres', 'land_area_hectares')
def validate_land_area(cls, v):
    if v is not None and v < 0:
        raise ValueError('Land area cannot be negative')
    return v

@validator('expected_price', 'minimum_price', 'current_market_price', 'expected_market_price')
def validate_price(cls, v):
    if v is not None and v < 0:
        raise ValueError('Price cannot be negative')
    return v

@validator('quantity', 'quantity_available')
def validate_quantity(cls, v):
    if v is not None and v < 0:
        raise ValueError('Quantity cannot be negative')
    return v

@validator('employee_count', 'year_established')
def validate_positive_int(cls, v):
    if v is not None and v < 0:
        raise ValueError('Value cannot be negative')
    return v

@validator('annual_turnover', 'funding_amount', 'salary_expectation', 'placed_salary')
def validate_financial_amount(cls, v):
    if v is not None and v < 0:
        raise ValueError('Financial amount cannot be negative')
    return v

@validator('max_age', 'min_age')
def validate_age(cls, v):
    if v is not None and (v < 0 or v > 120):
        raise ValueError('Age must be between 0 and 120')
    return v

@validator('duration_hours', 'duration_weeks', 'duration_months')
def validate_duration(cls, v):
    if v is not None and v < 0:
        raise ValueError('Duration cannot be negative')
    return v

@validator('max_participants', 'min_participants')
def validate_participants(cls, v):
    if v is not None and v < 0:
        raise ValueError('Number of participants cannot be negative')
    return v

@validator('attendance_percentage')
def validate_percentage(cls, v):
    if v is not None and (v < 0 or v > 100):
        raise ValueError('Percentage must be between 0 and 100')
    return v

@validator('assessment_score')
def validate_score(cls, v):
    if v is not None and (v < 0 or v > 100):
        raise ValueError('Score must be between 0 and 100')
    return v
