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
    """Business categories for constituency"""
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
    MICRO = "micro"  # < 10 employees, < 1 crore turnover
    SMALL = "small"  # 10-50 employees, 1-10 crore turnover
    MEDIUM = "medium"  # 50-250 employees, 10-100 crore turnover
    LARGE = "large"  # > 250 employees, > 100 crore turnover


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
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    ward_id = Column(String, ForeignKey("wards.id"), nullable=True, index=True)
    
    # Farm Details
    land_area_acres = Column(Float, nullable=True)
    land_area_hectares = Column(Float, nullable=True)
    soil_type = Column(String(100))
    water_source = Column(String(100))  # borewell, canal, rain-fed, etc.
    irrigation_type = Column(String(100))
    
    # Farming Information
    farming_type = Column(SQLEnum(FarmingType), nullable=True)
    primary_crops = Column(JSON)  # List of CropType
    secondary_crops = Column(JSON)  # List of CropType
    livestock_count = Column(JSON)  # {"cows": 5, "goats": 10, "chickens": 50}
    farm_equipment = Column(JSON)  # List of equipment owned
    
    # Support Programs
    government_schemes = Column(JSON)  # List of schemes enrolled
    mla_support_received = Column(JSON)  # List of MLA-provided support
    insurance_policies = Column(JSON)  # Crop insurance details
    
    # Contact & Location
    farm_address = Column(Text)
    farm_latitude = Column(String(50))
    farm_longitude = Column(String(50))
    preferred_language = Column(String(50), default="kannada")
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    priority_farmer = Column(Boolean, default=False)  # VIP farmers
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_visit_date = Column(DateTime)
    
    # Relationships
    farmer = relationship("User", foreign_keys=[farmer_id])
    constituency = relationship("Constituency")
    ward = relationship("Ward")
    crop_requests = relationship("CropRequest", back_populates="farmer", cascade="all, delete-orphan")
    market_listings = relationship("MarketListing", back_populates="farmer", cascade="all, delete-orphan")
    training_participations = relationship("TrainingParticipation", back_populates="farmer", cascade="all, delete-orphan")


class CropRequest(Base):
    """Crop information and market price requests"""
    __tablename__ = "crop_requests"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    farmer_id = Column(String, ForeignKey("farmer_profiles.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Crop Information
    crop_type = Column(SQLEnum(CropType), nullable=False, index=True)
    crop_name = Column(String(100), nullable=False)
    variety = Column(String(100))
    expected_harvest_date = Column(DateTime)
    
    # Market Information
    current_market_price = Column(Float)
    expected_market_price = Column(Float)
    target_market = Column(String(200))  # Where they want to sell
    
    # Request Type
    request_type = Column(String(50))  # price_info, market_connect, buyer_request, etc.
    quantity_available = Column(Float)  # in tons or quintals
    quality_grade = Column(String(50))  # A, B, C grade
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed
    priority = Column(String(50), default="medium")
    
    # Response
    buyer_contacts = Column(JSON)  # List of interested buyers
    market_suggestions = Column(JSON)  # Market recommendations
    mla_assistance = Column(Text)  # MLA provided assistance details
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    farmer = relationship("FarmerProfile", back_populates="crop_requests")
    constituency = relationship("Constituency")


class MarketListing(Base):
    """Agricultural market place for farmers"""
    __tablename__ = "market_listings"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    farmer_id = Column(String, ForeignKey("farmer_profiles.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Product Details
    crop_type = Column(SQLEnum(CropType), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    variety = Column(String(100))
    quantity = Column(Float, nullable=False)  # Available quantity
    unit = Column(String(50))  # kg, quintal, ton, etc.
    
    # Quality and Certification
    quality_grade = Column(String(50))
    is_organic = Column(Boolean, default=False)
    certification = Column(String(200))  # Organic, FSSAI, etc.
    
    # Pricing
    expected_price = Column(Float)
    minimum_price = Column(Float)
    price_negotiable = Column(Boolean, default=True)
    
    # Location and Logistics
    farm_location = Column(String(500))
    delivery_available = Column(Boolean, default=False)
    delivery_radius_km = Column(Integer)
    
    # Media
    product_photos = Column(JSON)  # URLs of product photos
    quality_videos = Column(JSON)  # URLs of quality videos
    certificates = Column(JSON)  # URLs of certificates
    
    # Status
    status = Column(String(50), default="active")  # active, sold, expired
    featured_listing = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    
    # Buyer Interest
    interested_buyers = Column(JSON)  # List of buyer contact info
    views_count = Column(Integer, default=0)
    contacts_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sold_at = Column(DateTime)
    
    # Relationships
    farmer = relationship("FarmerProfile", back_populates="market_listings")
    constituency = relationship("Constituency")


class BusinessProfile(Base):
    """Business community profile and support model"""
    __tablename__ = "business_profiles"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    ward_id = Column(String, ForeignKey("wards.id"), nullable=True, index=True)
    
    # Business Details
    business_name = Column(String(200), nullable=False)
    business_category = Column(SQLEnum(BusinessCategory), nullable=False, index=True)
    business_size = Column(SQLEnum(BusinessSize), nullable=True)
    
    # Registration and Legal
    registration_number = Column(String(100))
    gst_number = Column(String(50))
    license_type = Column(String(100))
    license_expiry = Column(DateTime)
    
    # Operations
    year_established = Column(Integer)
    employee_count = Column(Integer)
    annual_turnover = Column(Float)
    
    # Contact and Location
    business_address = Column(Text)
    business_phone = Column(String(20))
    business_email = Column(String(200))
    website = Column(String(500))
    business_latitude = Column(String(50))
    business_longitude = Column(String(50))
    
    # Support and Assistance
    mla_support_received = Column(JSON)  # List of MLA-provided support
    government_schemes = Column(JSON)  # Government schemes availed
    bank_loans = Column(JSON)  # Loan details
    
    # Networking
    business_associations = Column(JSON)  # Trade associations membership
    partnership_interests = Column(JSON)  # Looking for partnerships
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    featured_business = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verification_date = Column(DateTime)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    constituency = relationship("Constituency")
    ward = relationship("Ward")
    business_requests = relationship("BusinessRequest", back_populates="business", cascade="all, delete-orphan")
    network_connections = relationship("BusinessConnection", back_populates="business", cascade="all, delete-orphan")


class BusinessRequest(Base):
    """Business support requests and opportunities"""
    __tablename__ = "business_requests"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    business_id = Column(String, ForeignKey("business_profiles.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Request Details
    request_type = Column(String(100))  # funding, partnership, license, market, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Specific Information
    funding_amount = Column(Float)  # For funding requests
    partnership_type = Column(String(100))  # For partnership requests
    license_type = Column(String(100))  # For license requests
    market_expansion = Column(String(200))  # For market expansion requests
    
    # Urgency and Priority
    urgency_level = Column(String(50), default="medium")
    expected_resolution = Column(DateTime)
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, resolved
    priority = Column(String(50), default="medium")
    
    # Response and Assistance
    mla_assistance = Column(Text)
    government_schemes_suggested = Column(JSON)
    potential_partners = Column(JSON)
    funding_sources = Column(JSON)
    
    # Attachments
    documents = Column(JSON)  # URLs of supporting documents
    presentations = Column(JSON)  # URLs of business presentations
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    business = relationship("BusinessProfile", back_populates="business_requests")
    constituency = relationship("Constituency")


class BusinessConnection(Base):
    """Business networking and collaboration platform"""
    __tablename__ = "business_connections"

    id = Column(String, primary_key=True, index=True)
    
    # Connection Details
    business_id = Column(String, ForeignKey("business_profiles.id"), nullable=False, index=True)
    connected_business_id = Column(String, ForeignKey("business_profiles.id"), nullable=True, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Connection Type
    connection_type = Column(String(100))  # supplier, customer, partner, mentor, etc.
    collaboration_interest = Column(String(200))
    
    # Business Details
    looking_for = Column(String(500))  # What they're looking for
    offering = Column(String(500))  # What they're offering
    
    # Status
    status = Column(String(50), default="active")  # active, inactive, completed
    connection_strength = Column(String(50), default="new")  # new, developing, strong
    
    # Interaction Tracking
    last_interaction_date = Column(DateTime)
    interaction_count = Column(Integer, default=0)
    successful_collaborations = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("BusinessProfile", foreign_keys=[business_id], back_populates="network_connections")
    connected_business = relationship("BusinessProfile", foreign_keys=[connected_business_id])
    constituency = relationship("Constituency")


class YouthProfile(Base):
    """Youth engagement and development profile"""
    __tablename__ = "youth_profiles"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    youth_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    ward_id = Column(String, ForeignKey("wards.id"), nullable=True, index=True)
    
    # Personal Details
    date_of_birth = Column(DateTime)
    education_level = Column(String(100))
    field_of_study = Column(String(200))
    current_status = Column(String(100))  # student, employed, unemployed, entrepreneur
    
    # Skills and Interests
    technical_skills = Column(JSON)  # List of technical skills
    soft_skills = Column(JSON)  # List of soft skills
    interests = Column(JSON)  # Areas of interest
    hobbies = Column(JSON)  # Hobbies and extracurricular activities
    
    # Career Information
    career_goals = Column(String(500))
    preferred_industries = Column(JSON)  # Industries interested in
    job_search_status = Column(String(100))  # active, passive, not_searching
    entrepreneur_interest = Column(Boolean, default=False)
    
    # Community Engagement
    volunteer_interest = Column(Boolean, default=False)
    social_issues = Column(JSON)  # Social issues they care about
    leadership_roles = Column(JSON)  # Previous leadership experience
    
    # Contact and Preferences
    preferred_language = Column(String(50), default="kannada")
    notification_preferences = Column(JSON)  # Types of notifications they want
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    featured_youth = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_date = Column(DateTime)
    
    # Relationships
    youth = relationship("User", foreign_keys=[youth_id])
    constituency = relationship("Constituency")
    ward = relationship("Ward")
    program_participations = relationship("ProgramParticipation", back_populates="youth", cascade="all, delete-orphan")
    career_requests = relationship("CareerRequest", back_populates="youth", cascade="all, delete-orphan")
    mentorship_connections = relationship("MentorshipConnection", back_populates="youth", cascade="all, delete-orphan")


class YouthProgram(Base):
    """Youth development programs and initiatives"""
    __tablename__ = "youth_programs"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    program_type = Column(SQLEnum(ProgramType), nullable=False, index=True)
    
    # Organization
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    organizer_id = Column(String, ForeignKey("users.id"), nullable=False)  # MLA or staff
    partner_organizations = Column(JSON)  # Partner organizations
    
    # Schedule and Duration
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
    benefits = Column(JSON)  # List of program benefits
    certification_offered = Column(Boolean, default=False)
    certificate_type = Column(String(200))
    placement_assistance = Column(Boolean, default=False)
    stipend_amount = Column(Float)
    
    # Status
    status = Column(String(50), default="upcoming")  # upcoming, ongoing, completed, cancelled
    is_featured = Column(Boolean, default=False)
    
    # Media and Resources
    program_photos = Column(JSON)
    program_videos = Column(JSON)
    resource_materials = Column(JSON)
    
    # Metrics
    application_count = Column(Integer, default=0)
    selected_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    constituency = relationship("Constituency")
    organizer = relationship("User", foreign_keys=[organizer_id])
    participations = relationship("ProgramParticipation", back_populates="program", cascade="all, delete-orphan")


class ProgramParticipation(Base):
    """Youth program participation tracking"""
    __tablename__ = "program_participations"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    youth_id = Column(String, ForeignKey("youth_profiles.id"), nullable=False, index=True)
    program_id = Column(String, ForeignKey("youth_programs.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Application Details
    application_date = Column(DateTime, default=datetime.utcnow)
    application_status = Column(String(50), default="applied")  # applied, shortlisted, selected, rejected, waitlisted
    selection_date = Column(DateTime)
    
    # Participation Details
    attendance_percentage = Column(Float)
    completion_status = Column(String(50))  # ongoing, completed, dropped_out
    completion_date = Column(DateTime)
    
    # Performance and Assessment
    performance_rating = Column(String(10))  # A, B, C, D
    skills_acquired = Column(JSON)
    projects_completed = Column(JSON)
    
    # Feedback and Outcomes
    youth_feedback = Column(Text)
    organizer_feedback = Column(Text)
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))
    
    # Post-Program Outcomes
    placement_status = Column(String(100))
    placement_company = Column(String(200))
    startup_founded = Column(Boolean, default=False)
    startup_details = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    youth = relationship("YouthProfile", back_populates="program_participations")
    program = relationship("YouthProgram", back_populates="participations")
    constituency = relationship("Constituency")


class CareerRequest(Base):
    """Career guidance and job placement requests"""
    __tablename__ = "career_requests"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    youth_id = Column(String, ForeignKey("youth_profiles.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Request Details
    career_field = Column(SQLEnum(CareerField), nullable=False, index=True)
    request_type = Column(String(100))  # guidance, training, job_placement, internship, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Specific Information
    current_education = Column(String(200))
    target_companies = Column(JSON)  # Companies they're interested in
    salary_expectation = Column(Float)
    preferred_location = Column(String(200))
    
    # Skills and Qualifications
    relevant_skills = Column(JSON)
    certifications = Column(JSON)
    work_experience = Column(JSON)  # Previous work experience
    portfolio_url = Column(String(500))
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, resolved
    priority = Column(String(50), default="medium")
    urgency_level = Column(String(50), default="medium")
    
    # Response and Assistance
    guidance_provided = Column(Text)
    training_suggested = Column(JSON)
    job_opportunities = Column(JSON)
    internship_opportunities = Column(JSON)
    mentor_assigned = Column(String, ForeignKey("users.id"))
    
    # Outcomes
    placement_achieved = Column(Boolean, default=False)
    placed_company = Column(String(200))
    placed_position = Column(String(200))
    placed_salary = Column(Float)
    
    # Attachments
    resume_url = Column(String(500))
    certificates_urls = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    youth = relationship("YouthProfile", back_populates="career_requests")
    constituency = relationship("Constituency")
    mentor = relationship("User", foreign_keys=[mentor_assigned])


class MentorshipConnection(Base):
    """Youth mentorship and guidance program"""
    __tablename__ = "mentorship_connections"

    id = Column(String, primary_key=True, index=True)
    
    # Connection Details
    youth_id = Column(String, ForeignKey("youth_profiles.id"), nullable=False, index=True)
    mentor_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Mentorship Details
    mentorship_area = Column(String(200))  # Career guidance, entrepreneurship, etc.
    goals = Column(JSON)  # Mentorship goals
    duration_months = Column(Integer)
    
    # Status
    status = Column(String(50), default="active")  # active, completed, paused
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    
    # Interaction Tracking
    session_count = Column(Integer, default=0)
    last_session_date = Column(DateTime)
    total_hours = Column(Float, default=0)
    
    # Progress and Outcomes
    progress_notes = Column(Text)
    achievements = Column(JSON)
    youth_feedback = Column(Text)
    mentor_feedback = Column(Text)
    
    # Success Metrics
    goals_achieved = Column(Integer, default=0)
    career_progress = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    youth = relationship("YouthProfile", back_populates="mentorship_connections")
    mentor = relationship("User", foreign_keys=[mentor_id])
    constituency = relationship("Constituency")


class TrainingProgram(Base):
    """Skill development and vocational training programs"""
    __tablename__ = "training_programs"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    training_category = Column(String(100))  # technical, soft_skills, vocational, etc.
    
    # Organization
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    trainer_id = Column(String, ForeignKey("users.id"), nullable=False)
    training_partner = Column(String(200))
    
    # Schedule
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration_hours = Column(Integer)
    session_frequency = Column(String(100))  # daily, weekly, weekend
    
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
    cost_sponsorship = Column(JSON)  # MLA sponsorship details
    
    # Status
    status = Column(String(50), default="upcoming")  # upcoming, ongoing, completed, cancelled
    is_free = Column(Boolean, default=True)
    
    # Metrics
    enrollment_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    constituency = relationship("Constituency")
    trainer = relationship("User", foreign_keys=[trainer_id])
    participations = relationship("TrainingParticipation", back_populates="training", cascade="all, delete-orphan")


class TrainingParticipation(Base):
    """Training program participation tracking"""
    __tablename__ = "training_participations"

    id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    participant_id = Column(String, ForeignKey("farmer_profiles.id"), nullable=False, index=True)
    training_id = Column(String, ForeignKey("training_programs.id"), nullable=False, index=True)
    constituency_id = Column(String, ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Enrollment Details
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    enrollment_status = Column(String(50), default="enrolled")  # enrolled, completed, dropped_out
    completion_date = Column(DateTime)
    
    # Performance
    attendance_percentage = Column(Float)
    assessment_score = Column(Float)
    skills_acquired = Column(JSON)
    
    # Feedback
    participant_feedback = Column(Text)
    trainer_feedback = Column(Text)
    
    # Certification
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))
    
    # Post-Training Impact
    income_improvement = Column(Float)
    business_improvement = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participant = relationship("FarmerProfile", back_populates="training_participations")
    training = relationship("TrainingProgram", back_populates="participations")
    constituency = relationship("Constituency")
