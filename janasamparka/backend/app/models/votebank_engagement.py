"""
Votebank Engagement Models - Agriculture, Business, Youth, Career Guidance, and Community Development
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Enum as SQLEnum, Float, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from app.core.database import Base


class CropType(str, Enum):
    """Agricultural crop categories"""
    FOOD_GRAINS = "food_grains"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    COMMERCIAL_CROPS = "commercial_crops"
    SPICES = "spices"
    PLANTATION = "plantation"
    HORTICULTURE = "horticulture"
    LIVESTOCK = "livestock"
    DAIRY = "dairy"
    POULTRY = "poultry"
    FISHERY = "fishery"
    OTHER = "other"


class FarmingType(str, Enum):
    """Types of farming practices"""
    ORGANIC = "organic"
    CONVENTIONAL = "conventional"
    NATURAL = "natural"
    ZERO_BUDGET = "zero_budget"
    PRECISION = "precision"
    GREENHOUSE = "greenhouse"
    HYDROPONIC = "hydroponic"
    MIXED = "mixed"


class BusinessCategory(str, Enum):
    """Business categories for constituency businesses"""
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    AGRICULTURE = "agriculture"
    TECHNOLOGY = "technology"
    CONSTRUCTION = "construction"
    TRANSPORT = "transport"
    TOURISM = "tourism"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    OTHER = "other"


class BusinessSize(str, Enum):
    """Business size classifications"""
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ProgramType(str, Enum):
    """Youth and community program types"""
    EDUCATION = "education"
    SKILL_DEVELOPMENT = "skill_development"
    SPORTS = "sports"
    CULTURAL = "cultural"
    ENVIRONMENT = "environment"
    HEALTH = "health"
    LEADERSHIP = "leadership"
    ENTREPRENEURSHIP = "entrepreneurship"
    SOCIAL_SERVICE = "social_service"
    TECHNOLOGY = "technology"
    ARTS = "arts"
    OTHER = "other"


class CareerField(str, Enum):
    """Career guidance fields"""
    ENGINEERING = "engineering"
    MEDICAL = "medical"
    MANAGEMENT = "management"
    LAW = "law"
    CIVIL_SERVICES = "civil_services"
    DEFENSE = "defense"
    AGRICULTURE = "agriculture"
    SCIENCE = "science"
    ARTS = "arts"
    COMMERCE = "commerce"
    VOCATIONAL = "vocational"
    ENTREPRENEURSHIP = "entrepreneurship"
    OTHER = "other"


class FarmerProfile(Base):
    """Farmer profile and agricultural support model"""
    __tablename__ = "farmer_profiles"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    farmer_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    ward_id = Column(PGUUID(as_uuid=True), ForeignKey("wards.id"), nullable=True, index=True)
    
    # Farm Details
    land_area_acres = Column(Float, nullable=True)
    land_area_hectares = Column(Float, nullable=True)
    soil_type = Column(String(100))
    water_source = Column(String(100))
    irrigation_type = Column(String(100))
    
    # Farming Information
    farming_type = Column(SQLEnum(FarmingType), nullable=True)
    primary_crops = Column(JSON)
    secondary_crops = Column(JSON)
    livestock_count = Column(JSON)
    farm_equipment = Column(JSON)
    
    # Support and Schemes
    government_schemes = Column(JSON)
    mla_support_received = Column(JSON)
    insurance_policies = Column(JSON)
    
    # Location
    farm_address = Column(Text)
    farm_latitude = Column(String(50))
    farm_longitude = Column(String(50))
    
    # Preferences
    preferred_language = Column(String(50), default="kannada")
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    priority_farmer = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_visit_date = Column(DateTime)
    
    # Relationships
    farmer = relationship("User", back_populates="farmer_profile")
    constituency = relationship("Constituency")
    ward = relationship("Ward")
    crop_requests = relationship("CropRequest", back_populates="farmer")
    market_listings = relationship("MarketListing", back_populates="farmer")
    training_participations = relationship("TrainingParticipation", back_populates="participant")


class CropRequest(Base):
    """Crop information and market price requests"""
    __tablename__ = "crop_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    farmer_id = Column(PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Crop Information
    crop_type = Column(SQLEnum(CropType), nullable=False, index=True)
    crop_name = Column(String(100), nullable=False)
    variety = Column(String(100))
    expected_harvest_date = Column(DateTime)
    
    # Market Information
    current_market_price = Column(Float)
    expected_market_price = Column(Float)
    target_market = Column(String(200))
    
    # Request Type
    request_type = Column(String(50))
    quantity_available = Column(Float)
    quality_grade = Column(String(50))
    priority = Column(String(50), default="medium")
    
    # Status and Tracking
    status = Column(String(50), default="pending")
    buyer_contacts = Column(JSON)
    market_suggestions = Column(JSON)
    mla_assistance = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    farmer = relationship("FarmerProfile", back_populates="crop_requests")
    constituency = relationship("Constituency")


class MarketListing(Base):
    """Agricultural product marketplace listings"""
    __tablename__ = "market_listings"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    farmer_id = Column(PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Product Information
    crop_type = Column(SQLEnum(CropType), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    variety = Column(String(100))
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), default="kg")
    quality_grade = Column(String(50))
    
    # Quality and Certification
    is_organic = Column(Boolean, default=False)
    certification = Column(String(200))
    
    # Pricing
    expected_price = Column(Float)
    minimum_price = Column(Float)
    price_negotiable = Column(Boolean, default=True)
    
    # Location and Delivery
    farm_location = Column(String(500))
    delivery_available = Column(Boolean, default=False)
    delivery_radius_km = Column(Integer)
    
    # Media
    product_photos = Column(JSON)
    quality_videos = Column(JSON)
    certificates = Column(JSON)
    
    # Status and Tracking
    status = Column(String(50), default="active")
    featured_listing = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    interested_buyers = Column(JSON)
    views_count = Column(Integer, default=0)
    contacts_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sold_at = Column(DateTime)
    
    # Relationships
    farmer = relationship("FarmerProfile", back_populates="market_listings")
    constituency = relationship("Constituency")


class BusinessProfile(Base):
    """Business community profiles and support"""
    __tablename__ = "business_profiles"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    ward_id = Column(PGUUID(as_uuid=True), ForeignKey("wards.id"), nullable=True, index=True)
    
    # Business Details
    business_name = Column(String(200), nullable=False)
    business_category = Column(SQLEnum(BusinessCategory), nullable=False)
    business_size = Column(SQLEnum(BusinessSize), nullable=True)
    
    # Registration and Legal
    registration_number = Column(String(100))
    gst_number = Column(String(50))
    license_type = Column(String(100))
    license_expiry = Column(DateTime)
    
    # Business Information
    year_established = Column(Integer)
    employee_count = Column(Integer)
    annual_turnover = Column(Float)
    
    # Contact Information
    business_address = Column(Text)
    business_phone = Column(String(20))
    business_email = Column(String(200))
    website = Column(String(500))
    business_latitude = Column(String(50))
    business_longitude = Column(String(50))
    
    # Support and Schemes
    mla_support_received = Column(JSON)
    government_schemes = Column(JSON)
    bank_loans = Column(JSON)
    business_associations = Column(JSON)
    partnership_interests = Column(JSON)
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    featured_business = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verification_date = Column(DateTime)
    
    # Relationships
    owner = relationship("User", back_populates="business_profile")
    constituency = relationship("Constituency")
    ward = relationship("Ward")
    business_requests = relationship("BusinessRequest", back_populates="business")
    connections_as_business = relationship("BusinessConnection", foreign_keys="BusinessConnection.business_id", back_populates="business")


class BusinessRequest(Base):
    """Business support requests and assistance"""
    __tablename__ = "business_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    business_id = Column(PGUUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Request Details
    request_type = Column(String(100))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Specific Request Information
    funding_amount = Column(Float)
    partnership_type = Column(String(100))
    license_type = Column(String(100))
    market_expansion = Column(String(200))
    
    # Priority and Timeline
    urgency_level = Column(String(50), default="medium")
    expected_resolution = Column(DateTime)
    priority = Column(String(50), default="medium")
    
    # Status and Tracking
    status = Column(String(50), default="pending")
    mla_assistance = Column(Text)
    government_schemes_suggested = Column(JSON)
    potential_partners = Column(JSON)
    funding_sources = Column(JSON)
    
    # Documents
    documents = Column(JSON)
    presentations = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    business = relationship("BusinessProfile", back_populates="business_requests")
    constituency = relationship("Constituency")


class BusinessConnection(Base):
    """Business networking and collaboration platform"""
    __tablename__ = "business_connections"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    business_id = Column(PGUUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False, index=True)
    connected_business_id = Column(PGUUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=True, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Connection Details
    connection_type = Column(String(100))
    collaboration_interest = Column(String(200))
    looking_for = Column(String(500))
    offering = Column(String(500))
    
    # Status and Tracking
    status = Column(String(50), default="active")
    connection_strength = Column(String(50), default="new")
    last_interaction_date = Column(DateTime)
    interaction_count = Column(Integer, default=0)
    successful_collaborations = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("BusinessProfile", foreign_keys=[business_id], back_populates="connections_as_business")
    connected_business = relationship("BusinessProfile", foreign_keys=[connected_business_id])
    constituency = relationship("Constituency")


class YouthProfile(Base):
    """Youth engagement and development profiles"""
    __tablename__ = "youth_profiles"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    youth_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    ward_id = Column(PGUUID(as_uuid=True), ForeignKey("wards.id"), nullable=True, index=True)
    
    # Personal Information
    date_of_birth = Column(DateTime)
    education_level = Column(String(100))
    field_of_study = Column(String(200))
    current_status = Column(String(100))
    
    # Skills and Interests
    technical_skills = Column(JSON)
    soft_skills = Column(JSON)
    interests = Column(JSON)
    hobbies = Column(JSON)
    
    # Career and Goals
    career_goals = Column(String(500))
    preferred_industries = Column(JSON)
    job_search_status = Column(String(100))
    entrepreneur_interest = Column(Boolean, default=False)
    volunteer_interest = Column(Boolean, default=False)
    
    # Social and Community
    social_issues = Column(JSON)
    leadership_roles = Column(JSON)
    
    # Preferences
    preferred_language = Column(String(50), default="kannada")
    notification_preferences = Column(JSON)
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    featured_youth = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_date = Column(DateTime)
    
    # Relationships
    youth = relationship("User", back_populates="youth_profile")
    constituency = relationship("Constituency")
    ward = relationship("Ward")
    program_participations = relationship("ProgramParticipation", back_populates="youth")
    career_requests = relationship("CareerRequest", back_populates="youth")
    mentorship_connections = relationship("MentorshipConnection", back_populates="youth")


class YouthProgram(Base):
    """Youth development programs and initiatives"""
    __tablename__ = "youth_programs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    program_type = Column(SQLEnum(ProgramType), nullable=False)
    
    # Organization
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    organizer_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    partner_organizations = Column(JSON)
    
    # Schedule
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    application_deadline = Column(DateTime)
    duration_weeks = Column(Integer)
    
    # Capacity and Requirements
    max_participants = Column(Integer)
    min_age = Column(Integer)
    max_age = Column(Integer)
    education_requirements = Column(String(200))
    skill_requirements = Column(JSON)
    
    # Location and Format
    venue = Column(String(500))
    is_online = Column(Boolean, default=False)
    is_hybrid = Column(Boolean, default=False)
    meeting_link = Column(String(500))
    
    # Benefits and Outcomes
    benefits = Column(JSON)
    certification_offered = Column(Boolean, default=False)
    certificate_type = Column(String(200))
    placement_assistance = Column(Boolean, default=False)
    stipend_amount = Column(Float)
    
    # Media and Resources
    program_photos = Column(JSON)
    program_videos = Column(JSON)
    resource_materials = Column(JSON)
    
    # Status and Tracking
    status = Column(String(50), default="upcoming")
    is_featured = Column(Boolean, default=False)
    application_count = Column(Integer, default=0)
    selected_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    constituency = relationship("Constituency")
    organizer = relationship("User", back_populates="organized_programs")
    program_participations = relationship("ProgramParticipation", back_populates="program")


class ProgramParticipation(Base):
    """Youth program participation tracking"""
    __tablename__ = "program_participations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    youth_id = Column(PGUUID(as_uuid=True), ForeignKey("youth_profiles.id"), nullable=False, index=True)
    program_id = Column(PGUUID(as_uuid=True), ForeignKey("youth_programs.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Application Information
    application_date = Column(DateTime, default=datetime.utcnow)
    application_status = Column(String(50), default="applied")
    selection_date = Column(DateTime)
    
    # Participation Details
    attendance_percentage = Column(Float)
    completion_status = Column(String(50))
    completion_date = Column(DateTime)
    performance_rating = Column(String(10))
    
    # Skills and Projects
    skills_acquired = Column(JSON)
    projects_completed = Column(JSON)
    
    # Feedback
    youth_feedback = Column(Text)
    organizer_feedback = Column(Text)
    
    # Certification and Placement
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))
    placement_status = Column(String(100))
    placement_company = Column(String(200))
    
    # Entrepreneurship
    startup_founded = Column(Boolean, default=False)
    startup_details = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    youth = relationship("YouthProfile", back_populates="program_participations")
    program = relationship("YouthProgram", back_populates="program_participations")
    constituency = relationship("Constituency")


class CareerRequest(Base):
    """Career guidance and job placement requests"""
    __tablename__ = "career_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    youth_id = Column(PGUUID(as_uuid=True), ForeignKey("youth_profiles.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Career Information
    career_field = Column(SQLEnum(CareerField), nullable=False, index=True)
    request_type = Column(String(100))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Education and Experience
    current_education = Column(String(200))
    target_companies = Column(JSON)
    salary_expectation = Column(Float)
    preferred_location = Column(String(200))
    
    # Skills and Portfolio
    relevant_skills = Column(JSON)
    certifications = Column(JSON)
    work_experience = Column(JSON)
    portfolio_url = Column(String(500))
    
    # Priority and Status
    status = Column(String(50), default="pending")
    priority = Column(String(50), default="medium")
    urgency_level = Column(String(50), default="medium")
    
    # Guidance and Placement
    guidance_provided = Column(Text)
    training_suggested = Column(JSON)
    job_opportunities = Column(JSON)
    internship_opportunities = Column(JSON)
    mentor_assigned = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Placement Outcome
    placement_achieved = Column(Boolean, default=False)
    placed_company = Column(String(200))
    placed_position = Column(String(200))
    placed_salary = Column(Float)
    
    # Documents
    resume_url = Column(String(500))
    certificates_urls = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    youth = relationship("YouthProfile", back_populates="career_requests")
    constituency = relationship("Constituency")
    mentor = relationship("User", back_populates="career_guidance")


class MentorshipConnection(Base):
    """Youth mentorship program connections"""
    __tablename__ = "mentorship_connections"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    youth_id = Column(PGUUID(as_uuid=True), ForeignKey("youth_profiles.id"), nullable=False, index=True)
    mentor_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Mentorship Details
    mentorship_area = Column(String(200))
    goals = Column(JSON)
    duration_months = Column(Integer)
    
    # Status and Schedule
    status = Column(String(50), default="active")
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    
    # Session Tracking
    session_count = Column(Integer, default=0)
    last_session_date = Column(DateTime)
    total_hours = Column(Float, default=0.0)
    
    # Progress and Outcomes
    progress_notes = Column(Text)
    achievements = Column(JSON)
    goals_achieved = Column(Integer, default=0)
    career_progress = Column(String(500))
    
    # Feedback
    youth_feedback = Column(Text)
    mentor_feedback = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    youth = relationship("YouthProfile", back_populates="mentorship_connections")
    mentor = relationship("User", back_populates="mentorship_connections")
    constituency = relationship("Constituency")


class TrainingProgram(Base):
    """Training and skill development programs"""
    __tablename__ = "training_programs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    training_category = Column(String(100))
    
    # Organization
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    trainer_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    training_partner = Column(String(200))
    
    # Schedule
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration_hours = Column(Integer)
    session_frequency = Column(String(100))
    
    # Capacity and Requirements
    max_participants = Column(Integer)
    min_participants = Column(Integer)
    prerequisites = Column(JSON)
    
    # Location and Format
    venue = Column(String(500))
    is_online = Column(Boolean, default=False)
    meeting_link = Column(String(500))
    
    # Certification and Cost
    certification_offered = Column(Boolean, default=False)
    certificate_issuer = Column(String(200))
    training_cost = Column(Float)
    cost_sponsorship = Column(JSON)
    
    # Status and Tracking
    status = Column(String(50), default="upcoming")
    is_free = Column(Boolean, default=True)
    enrollment_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    constituency = relationship("Constituency")
    trainer = relationship("User", back_populates="conducted_trainings")
    training_participations = relationship("TrainingParticipation", back_populates="training")


class TrainingParticipation(Base):
    """Training program participation tracking"""
    __tablename__ = "training_participations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Basic Information
    participant_id = Column(PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id"), nullable=False, index=True)
    training_id = Column(PGUUID(as_uuid=True), ForeignKey("training_programs.id"), nullable=False, index=True)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Enrollment Information
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    enrollment_status = Column(String(50), default="enrolled")
    completion_date = Column(DateTime)
    
    # Performance
    attendance_percentage = Column(Float)
    assessment_score = Column(Float)
    
    # Skills and Outcomes
    skills_acquired = Column(JSON)
    participant_feedback = Column(Text)
    trainer_feedback = Column(Text)
    
    # Certification and Impact
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))
    income_improvement = Column(Float)
    business_improvement = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participant = relationship("FarmerProfile", back_populates="training_participations")
    training = relationship("TrainingProgram", back_populates="training_participations")
    constituency = relationship("Constituency")
