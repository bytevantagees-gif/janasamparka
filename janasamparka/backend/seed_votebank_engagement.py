"""
Seed script for votebank engagement data - farmers, businesses, youth, career guidance, and training programs
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db, engine
from app.models.votebank_engagement import (
    FarmerProfile, CropRequest, MarketListing, BusinessProfile, BusinessRequest,
    BusinessConnection, YouthProfile, YouthProgram, ProgramParticipation,
    CareerRequest, MentorshipConnection, TrainingProgram, TrainingParticipation,
    CropType, FarmingType, BusinessCategory, BusinessSize, ProgramType, CareerField
)
from app.models.user import User
from app.models.constituency import Constituency
from app.models.ward import Ward
import uuid


def seed_farmer_data(db: Session):
    """Seed sample farmer data"""
    
    # Get constituencies and users
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore City South").first()
    
    # Get test users (citizens)
    puttur_citizens = db.query(User).filter(
        User.constituency_id == puttur.id,
        User.role == "citizen"
    ).limit(10).all()
    
    mangalore_citizens = db.query(User).filter(
        User.constituency_id == mangalore.id,
        User.role == "citizen"
    ).limit(10).all()
    
    if not puttur_citizens or not mangalore_citizens:
        print("Not enough citizen users found")
        return
    
    # Sample farmer profiles for Puttur
    puttur_farmers = [
        {
            "land_area_acres": 5.5,
            "land_area_hectares": 2.2,
            "soil_type": "Red Laterite",
            "water_source": "Borewell",
            "irrigation_type": "Drip Irrigation",
            "farming_type": FarmingType.ORGANIC,
            "primary_crops": ["rice", "vegetables"],
            "secondary_crops": ["coconut", "arecanut"],
            "livestock_count": {"cows": 3, "goats": 5, "chickens": 20},
            "farm_equipment": ["tractor", "power_tiller", "sprayer"],
            "government_schemes": ["PMKisan", "Kisan Credit Card"],
            "farm_address": "Village Kadaba, Puttur Taluk",
            "farm_latitude": "12.7647",
            "farm_longitude": "75.2128",
            "preferred_language": "kannada",
            "is_verified": True,
            "priority_farmer": True
        },
        {
            "land_area_acres": 8.0,
            "land_area_hectares": 3.2,
            "soil_type": "Clay Loam",
            "water_source": "Canal",
            "irrigation_type": "Flood Irrigation",
            "farming_type": FarmingType.CONVENTIONAL,
            "primary_crops": ["paddy", "sugarcane"],
            "secondary_crops": ["vegetables", "fruits"],
            "livestock_count": {"cows": 5, "buffaloes": 2},
            "farm_equipment": ["tractor", "thresher", "pump_set"],
            "government_schemes": ["PMKisan", "Soil Health Card"],
            "farm_address": "Village Nellyadi, Puttur Taluk",
            "farm_latitude": "12.7800",
            "farm_longitude": "75.2300",
            "preferred_language": "kannada",
            "is_verified": True
        },
        {
            "land_area_acres": 2.5,
            "land_area_hectares": 1.0,
            "soil_type": "Sandy Loam",
            "water_source": "Rain-fed",
            "irrigation_type": "Traditional",
            "farming_type": FarmingType.NATURAL,
            "primary_crops": ["millets", "pulses"],
            "secondary_crops": ["vegetables"],
            "livestock_count": {"goats": 8, "chickens": 15},
            "farm_equipment": ["power_tiller"],
            "government_schemes": ["PMKisan"],
            "farm_address": "Village Uppinangady, Puttur Taluk",
            "farm_latitude": "12.7500",
            "farm_longitude": "75.2000",
            "preferred_language": "kannada",
            "is_verified": False
        }
    ]
    
    # Create farmer profiles for Puttur
    for i, farmer_data in enumerate(puttur_farmers):
        citizen = puttur_citizens[i % len(puttur_citizens)]
        farmer = FarmerProfile(
            id=str(uuid.uuid4()),
            farmer_id=citizen.id,
            constituency_id=puttur.id,
            created_at=datetime.utcnow() - timedelta(days=i*10),
            **farmer_data
        )
        db.add(farmer)
    
    # Sample farmer profiles for Mangalore North
    mangalore_farmers = [
        {
            "land_area_acres": 3.0,
            "land_area_hectares": 1.2,
            "soil_type": "Coastal Sandy",
            "water_source": "Well",
            "irrigation_type": "Sprinkler",
            "farming_type": FarmingType.CONVENTIONAL,
            "primary_crops": ["vegetables", "flowers"],
            "secondary_crops": ["fruits"],
            "livestock_count": {"cows": 2, "chickens": 25},
            "farm_equipment": ["power_tiller", "sprayer"],
            "government_schemes": ["PMKisan"],
            "farm_address": "Village Surathkal, Mangalore Taluk",
            "farm_latitude": "12.9100",
            "farm_longitude": "74.8600",
            "preferred_language": "tulu",
            "is_verified": True
        },
        {
            "land_area_acres": 6.5,
            "land_area_hectares": 2.6,
            "soil_type": "Alluvial",
            "water_source": "River",
            "irrigation_type": "Drip Irrigation",
            "farming_type": FarmingType.ORGANIC,
            "primary_crops": ["vegetables", "fruits"],
            "secondary_crops": ["coconut"],
            "livestock_count": {"cows": 4, "goats": 6},
            "farm_equipment": ["tractor", "drip_system"],
            "government_schemes": ["PMKisan", "Organic Farming Scheme"],
            "farm_address": "Village Mulki, Mangalore Taluk",
            "farm_latitude": "12.9200",
            "farm_longitude": "74.8700",
            "preferred_language": "kannada",
            "is_verified": True,
            "priority_farmer": True
        }
    ]
    
    # Create farmer profiles for Mangalore North
    for i, farmer_data in enumerate(mangalore_farmers):
        citizen = mangalore_citizens[i % len(mangalore_citizens)]
        farmer = FarmerProfile(
            id=str(uuid.uuid4()),
            farmer_id=citizen.id,
            constituency_id=mangalore.id,
            created_at=datetime.utcnow() - timedelta(days=i*10),
            **farmer_data
        )
        db.add(farmer)
    
    print(f"Created {len(puttur_farmers + mangalore_farmers)} farmer profiles")


def seed_crop_requests(db: Session):
    """Seed sample crop requests"""
    
    # Get farmer profiles
    farmers = db.query(FarmerProfile).all()
    
    if not farmers:
        print("No farmer profiles found")
        return
    
    # Sample crop requests
    crop_requests = [
        {
            "crop_type": CropType.VEGETABLES,
            "crop_name": "Tomatoes",
            "variety": "Hybrid Roma",
            "expected_harvest_date": datetime.utcnow() + timedelta(days=45),
            "current_market_price": 25.0,
            "expected_market_price": 30.0,
            "target_market": "Mangalore Market",
            "request_type": "price_info",
            "quantity_available": 500.0,
            "quality_grade": "A",
            "priority": "high"
        },
        {
            "crop_type": CropType.FOOD_GRAINS,
            "crop_name": "Rice",
            "variety": "Sona Masoori",
            "expected_harvest_date": datetime.utcnow() + timedelta(days=60),
            "current_market_price": 35.0,
            "expected_market_price": 40.0,
            "target_market": "Puttur Market",
            "request_type": "market_connect",
            "quantity_available": 2000.0,
            "quality_grade": "A",
            "priority": "medium"
        },
        {
            "crop_type": CropType.SPICES,
            "crop_name": "Pepper",
            "variety": "Malabar Pepper",
            "expected_harvest_date": datetime.utcnow() + timedelta(days=90),
            "current_market_price": 450.0,
            "expected_market_price": 500.0,
            "target_market": "Export Market",
            "request_type": "buyer_request",
            "quantity_available": 100.0,
            "quality_grade": "Premium",
            "priority": "urgent"
        },
        {
            "crop_type": CropType.FRUITS,
            "crop_name": "Mangoes",
            "variety": "Alphonso",
            "expected_harvest_date": datetime.utcnow() + timedelta(days=120),
            "current_market_price": 80.0,
            "expected_market_price": 100.0,
            "target_market": "Bangalore Market",
            "request_type": "price_info",
            "quantity_available": 300.0,
            "quality_grade": "A",
            "priority": "medium"
        },
        {
            "crop_type": CropType.VEGETABLES,
            "crop_name": "Brinjal",
            "variety": "Long Purple",
            "expected_harvest_date": datetime.utcnow() + timedelta(days=30),
            "current_market_price": 20.0,
            "expected_market_price": 25.0,
            "target_market": "Local Market",
            "request_type": "market_connect",
            "quantity_available": 200.0,
            "quality_grade": "B",
            "priority": "low"
        }
    ]
    
    # Create crop requests
    for i, request_data in enumerate(crop_requests):
        farmer = farmers[i % len(farmers)]
        request = CropRequest(
            id=str(uuid.uuid4()),
            farmer_id=farmer.id,
            constituency_id=farmer.constituency_id,
            created_at=datetime.utcnow() - timedelta(days=i),
            **request_data
        )
        db.add(request)
    
    print(f"Created {len(crop_requests)} crop requests")


def seed_market_listings(db: Session):
    """Seed sample market listings"""
    
    # Get farmer profiles
    farmers = db.query(FarmerProfile).all()
    
    if not farmers:
        print("No farmer profiles found")
        return
    
    # Sample market listings
    market_listings = [
        {
            "crop_type": CropType.VEGETABLES,
            "product_name": "Organic Tomatoes",
            "variety": "Desert Hybrid",
            "quantity": 1000.0,
            "unit": "kg",
            "quality_grade": "Premium Organic",
            "is_organic": True,
            "certification": "Organic Certification 2024",
            "expected_price": 45.0,
            "minimum_price": 40.0,
            "price_negotiable": True,
            "farm_location": "Kadaba Village, Puttur",
            "delivery_available": True,
            "delivery_radius_km": 50,
            "product_photos": ["tomatoes1.jpg", "tomatoes2.jpg"],
            "quality_videos": ["tomato_quality.mp4"]
        },
        {
            "crop_type": CropType.FOOD_GRAINS,
            "product_name": "Premium Sona Masoori Rice",
            "variety": "Sona Masoori 2024",
            "quantity": 5000.0,
            "unit": "kg",
            "quality_grade": "A Grade",
            "is_organic": False,
            "expected_price": 42.0,
            "minimum_price": 38.0,
            "price_negotiable": False,
            "farm_location": "Nellyadi Village, Puttur",
            "delivery_available": True,
            "delivery_radius_km": 100,
            "product_photos": ["rice1.jpg", "rice2.jpg"]
        },
        {
            "crop_type": CropType.SPICES,
            "product_name": "Premium Black Pepper",
            "variety": "Malabar Special",
            "quantity": 200.0,
            "unit": "kg",
            "quality_grade": "Export Quality",
            "is_organic": True,
            "certification": "Spice Board Certified",
            "expected_price": 550.0,
            "minimum_price": 500.0,
            "price_negotiable": True,
            "farm_location": "Uppinangady Village, Puttur",
            "delivery_available": False,
            "product_photos": ["pepper1.jpg", "pepper2.jpg"],
            "certificates": ["organic_cert.pdf", "spice_board_cert.pdf"]
        },
        {
            "crop_type": CropType.FRUITS,
            "product_name": "Fresh Mangoes",
            "variety": "Alphonso",
            "quantity": 800.0,
            "unit": "dozen",
            "quality_grade": "A Grade",
            "is_organic": False,
            "expected_price": 1200.0,
            "minimum_price": 1000.0,
            "price_negotiable": True,
            "farm_location": "Surathkal Village, Mangalore",
            "delivery_available": True,
            "delivery_radius_km": 75,
            "product_photos": ["mango1.jpg", "mango2.jpg", "mango3.jpg"]
        },
        {
            "crop_type": CropType.VEGETABLES,
            "product_name": "Mixed Vegetables Pack",
            "variety": "Seasonal Mix",
            "quantity": 500.0,
            "unit": "kg",
            "quality_grade": "Fresh",
            "is_organic": True,
            "expected_price": 35.0,
            "minimum_price": 30.0,
            "price_negotiable": True,
            "farm_location": "Mulki Village, Mangalore",
            "delivery_available": True,
            "delivery_radius_km": 30,
            "product_photos": ["mixed_veg1.jpg"]
        }
    ]
    
    # Create market listings
    for i, listing_data in enumerate(market_listings):
        farmer = farmers[i % len(farmers)]
        listing = MarketListing(
            id=str(uuid.uuid4()),
            farmer_id=farmer.id,
            constituency_id=farmer.constituency_id,
            expires_at=datetime.utcnow() + timedelta(days=30),
            created_at=datetime.utcnow() - timedelta(days=i*2),
            **listing_data
        )
        db.add(listing)
    
    print(f"Created {len(market_listings)} market listings")


def seed_business_data(db: Session):
    """Seed sample business data"""
    
    # Get constituencies and users
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore City South").first()
    
    # Get test users (citizens)
    puttur_citizens = db.query(User).filter(
        User.constituency_id == puttur.id,
        User.role == "citizen"
    ).limit(10).offset(10).all()
    
    mangalore_citizens = db.query(User).filter(
        User.constituency_id == mangalore.id,
        User.role == "citizen"
    ).limit(10).offset(10).all()
    
    if not puttur_citizens or not mangalore_citizens:
        print("Not enough citizen users found")
        return
    
    # Sample business profiles for Puttur
    puttur_businesses = [
        {
            "business_name": "Sri Venkateshwara Rice Mill",
            "business_category": BusinessCategory.AGRICULTURE,
            "business_size": BusinessSize.SMALL,
            "registration_number": "ROC-KAR-2024-0123",
            "gst_number": "29AAAPL1234C1ZV",
            "year_established": 2015,
            "employee_count": 15,
            "annual_turnover": 8500000.0,
            "business_address": "Industrial Area, Puttur",
            "business_phone": "+918241234567",
            "business_email": "svrice@example.com",
            "business_latitude": "12.7650",
            "business_longitude": "75.2130",
            "mla_support_received": ["Machinery Subsidy", "Working Capital Loan"],
            "government_schemes": ["MSME Development", "Food Processing Scheme"],
            "business_associations": ["Karnataka Rice Millers Association"],
            "is_verified": True,
            "featured_business": True
        },
        {
            "business_name": "Namma Supermarket",
            "business_category": BusinessCategory.RETAIL,
            "business_size": BusinessSize.MICRO,
            "registration_number": "SHOP-2024-0456",
            "year_established": 2020,
            "employee_count": 8,
            "annual_turnover": 2500000.0,
            "business_address": "Main Road, Puttur Town",
            "business_phone": "+918241234568",
            "business_email": "namma@example.com",
            "business_latitude": "12.7640",
            "business_longitude": "75.2120",
            "mla_support_received": ["Shop Establishment Assistance"],
            "government_schemes": ["PM Vishwakarma"],
            "is_verified": True
        },
        {
            "business_name": "Puttur Engineering Works",
            "business_category": BusinessCategory.MANUFACTURING,
            "business_size": BusinessSize.SMALL,
            "registration_number": "MSME-KAR-2024-0789",
            "gst_number": "29AAAPL5678C1ZV",
            "year_established": 2018,
            "employee_count": 25,
            "annual_turnover": 12000000.0,
            "business_address": "Industrial Estate, Puttur",
            "business_phone": "+918241234569",
            "business_email": "engineering@example.com",
            "business_latitude": "12.7660",
            "business_longitude": "75.2140",
            "mla_support_received": ["Equipment Purchase Grant"],
            "government_schemes": ["Technology Upgradation Fund"],
            "business_associations": ["Karnataka Small Industries Association"],
            "is_verified": True,
            "featured_business": True
        }
    ]
    
    # Create business profiles for Puttur
    for i, business_data in enumerate(puttur_businesses):
        citizen = puttur_citizens[i % len(puttur_citizens)]
        business = BusinessProfile(
            id=str(uuid.uuid4()),
            owner_id=citizen.id,
            constituency_id=puttur.id,
            created_at=datetime.utcnow() - timedelta(days=i*15),
            **business_data
        )
        db.add(business)
    
    # Sample business profiles for Mangalore North
    mangalore_businesses = [
        {
            "business_name": "Coastal Sea Foods Export",
            "business_category": BusinessCategory.MANUFACTURING,
            "business_size": BusinessSize.MEDIUM,
            "registration_number": "FSSAI-2024-0345",
            "gst_number": "29AAAPL9012C1ZV",
            "license_type": "FSSAI License",
            "license_expiry": datetime.utcnow() + timedelta(days=365),
            "year_established": 2012,
            "employee_count": 50,
            "annual_turnover": 25000000.0,
            "business_address": "Fisheries Port, Mangalore",
            "business_phone": "+918242345678",
            "business_email": "coastal@example.com",
            "website": "www.coastalseafoods.com",
            "business_latitude": "12.9150",
            "business_longitude": "74.8650",
            "mla_support_received": ["Export Promotion Grant", "Cold Storage Subsidy"],
            "government_schemes": ["Marine Products Export Development Authority"],
            "business_associations": ["Seafood Exporters Association"],
            "is_verified": True,
            "featured_business": True
        },
        {
            "business_name": "Tech Solutions IT Services",
            "business_category": BusinessCategory.TECHNOLOGY,
            "business_size": BusinessSize.SMALL,
            "registration_number": "STPI-KAR-2024-0234",
            "gst_number": "29AAAPL3456C1ZV",
            "year_established": 2019,
            "employee_count": 20,
            "annual_turnover": 8000000.0,
            "business_address": "IT Park, Mangalore",
            "business_phone": "+918242345679",
            "business_email": "tech@example.com",
            "website": "www.techsolutions.in",
            "business_latitude": "12.9250",
            "business_longitude": "74.8750",
            "mla_support_received": ["Startup Seed Funding"],
            "government_schemes": ["Startup India", "Digital India"],
            "partnership_interests": ["Software Development", "IT Consulting"],
            "is_verified": True
        }
    ]
    
    # Create business profiles for Mangalore North
    for i, business_data in enumerate(mangalore_businesses):
        citizen = mangalore_citizens[i % len(mangalore_citizens)]
        business = BusinessProfile(
            id=str(uuid.uuid4()),
            owner_id=citizen.id,
            constituency_id=mangalore.id,
            created_at=datetime.utcnow() - timedelta(days=i*15),
            **business_data
        )
        db.add(business)
    
    print(f"Created {len(puttur_businesses + mangalore_businesses)} business profiles")


def seed_business_requests(db: Session):
    """Seed sample business requests"""
    
    # Get business profiles
    businesses = db.query(BusinessProfile).all()
    
    if not businesses:
        print("No business profiles found")
        return
    
    # Sample business requests
    business_requests = [
        {
            "request_type": "funding",
            "title": "Working Capital Loan for Expansion",
            "description": "Need working capital loan of Rs. 25 lakhs for expanding production capacity and hiring additional staff.",
            "funding_amount": 2500000.0,
            "urgency_level": "high",
            "expected_resolution": datetime.utcnow() + timedelta(days=30),
            "priority": "high"
        },
        {
            "request_type": "partnership",
            "title": "Looking for Distribution Partners",
            "description": "Seeking distribution partners across Karnataka for our organic rice products. Looking for established retail chains.",
            "partnership_type": "distribution",
            "urgency_level": "medium",
            "expected_resolution": datetime.utcnow() + timedelta(days=60),
            "priority": "medium"
        },
        {
            "request_type": "license",
            "title": "Food Processing License Assistance",
            "description": "Need assistance in obtaining FSSAI license and other food processing certifications for our new product line.",
            "license_type": "FSSAI",
            "urgency_level": "urgent",
            "expected_resolution": datetime.utcnow() + timedelta(days=15),
            "priority": "urgent"
        },
        {
            "request_type": "market",
            "title": "Export Market Access Support",
            "description": "Looking for support to access international markets for our seafood products. Need export documentation and market information.",
            "market_expansion": "International Markets - UAE, Singapore, Malaysia",
            "urgency_level": "high",
            "expected_resolution": datetime.utcnow() + timedelta(days=45),
            "priority": "high"
        },
        {
            "request_type": "funding",
            "title": "Technology Upgrade Funding",
            "description": "Need funding for upgrading our IT infrastructure and implementing ERP system for better business management.",
            "funding_amount": 1500000.0,
            "urgency_level": "medium",
            "expected_resolution": datetime.utcnow() + timedelta(days=90),
            "priority": "medium"
        }
    ]
    
    # Create business requests
    for i, request_data in enumerate(business_requests):
        business = businesses[i % len(businesses)]
        request = BusinessRequest(
            id=str(uuid.uuid4()),
            business_id=business.id,
            constituency_id=business.constituency_id,
            created_at=datetime.utcnow() - timedelta(days=i*3),
            **request_data
        )
        db.add(request)
    
    print(f"Created {len(business_requests)} business requests")


def seed_youth_data(db: Session):
    """Seed sample youth data"""
    
    # Get constituencies and users
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore City South").first()
    
    # Get test users (citizens)
    puttur_citizens = db.query(User).filter(
        User.constituency_id == puttur.id,
        User.role == "citizen"
    ).limit(10).offset(20).all()
    
    mangalore_citizens = db.query(User).filter(
        User.constituency_id == mangalore.id,
        User.role == "citizen"
    ).limit(10).offset(20).all()
    
    if not puttur_citizens or not mangalore_citizens:
        print("Not enough citizen users found")
        return
    
    # Sample youth profiles for Puttur
    puttur_youth = [
        {
            "date_of_birth": datetime.utcnow() - timedelta(days=22*365),
            "education_level": "Bachelor's Degree",
            "field_of_study": "Computer Science Engineering",
            "current_status": "unemployed",
            "technical_skills": ["Python", "Java", "Web Development", "Machine Learning"],
            "soft_skills": ["Communication", "Team Work", "Problem Solving"],
            "interests": ["Technology", "Entrepreneurship", "Social Service"],
            "hobbies": ["Coding", "Reading", "Photography"],
            "career_goals": "Start a tech startup focused on agricultural technology",
            "preferred_industries": ["Technology", "Agriculture", "Startups"],
            "job_search_status": "active",
            "entrepreneur_interest": True,
            "volunteer_interest": True,
            "social_issues": ["Education", "Environment", "Rural Development"],
            "leadership_roles": ["College Technical Club President"],
            "preferred_language": "kannada",
            "is_verified": True,
            "featured_youth": True
        },
        {
            "date_of_birth": datetime.utcnow() - timedelta(days=24*365),
            "education_level": "Master's Degree",
            "field_of_study": "Business Administration",
            "current_status": "employed",
            "technical_skills": ["MS Office", "Data Analysis", "Digital Marketing"],
            "soft_skills": ["Leadership", "Public Speaking", "Negotiation"],
            "interests": ["Business", "Finance", "Leadership"],
            "hobbies": ["Reading", "Travel", "Networking"],
            "career_goals": "Become a business consultant and help local businesses grow",
            "preferred_industries": ["Finance", "Consulting", "Education"],
            "job_search_status": "passive",
            "entrepreneur_interest": False,
            "volunteer_interest": True,
            "social_issues": ["Women Empowerment", "Education"],
            "leadership_roles": ["Student Union Member"],
            "preferred_language": "kannada",
            "is_verified": True
        },
        {
            "date_of_birth": datetime.utcnow() - timedelta(days=20*365),
            "education_level": "Pre-University",
            "field_of_study": "Science",
            "current_status": "student",
            "technical_skills": ["Basic Computer", "Internet Research"],
            "soft_skills": ["Communication", "Creativity"],
            "interests": ["Sports", "Arts", "Environment"],
            "hobbies": ["Cricket", "Painting", "Gardening"],
            "career_goals": "Become a sports coach and promote rural sports talent",
            "preferred_industries": ["Sports", "Education", "Social Service"],
            "job_search_status": "not_searching",
            "entrepreneur_interest": False,
            "volunteer_interest": True,
            "social_issues": ["Sports Development", "Youth Empowerment"],
            "leadership_roles": ["College Cricket Team Captain"],
            "preferred_language": "kannada",
            "is_verified": False
        }
    ]
    
    # Create youth profiles for Puttur
    for i, youth_data in enumerate(puttur_youth):
        citizen = puttur_citizens[i % len(puttur_citizens)]
        youth = YouthProfile(
            id=str(uuid.uuid4()),
            youth_id=citizen.id,
            constituency_id=puttur.id,
            last_active_date=datetime.utcnow() - timedelta(days=i),
            created_at=datetime.utcnow() - timedelta(days=i*20),
            **youth_data
        )
        db.add(youth)
    
    # Sample youth profiles for Mangalore North
    mangalore_youth = [
        {
            "date_of_birth": datetime.utcnow() - timedelta(days=23*365),
            "education_level": "Bachelor's Degree",
            "field_of_study": "Marine Biology",
            "current_status": "student",
            "technical_skills": ["Research", "Data Analysis", "Marine Research"],
            "soft_skills": ["Research Methodology", "Report Writing"],
            "interests": ["Marine Life", "Environment", "Research"],
            "hobbies": ["Scuba Diving", "Photography", "Reading"],
            "career_goals": "Work in marine conservation and fisheries development",
            "preferred_industries": ["Research", "Environment", "Fisheries"],
            "job_search_status": "passive",
            "entrepreneur_interest": False,
            "volunteer_interest": True,
            "social_issues": ["Marine Conservation", "Climate Change"],
            "leadership_roles": ["Environment Club Member"],
            "preferred_language": "tulu",
            "is_verified": True,
            "featured_youth": True
        },
        {
            "date_of_birth": datetime.utcnow() - timedelta(days=21*365),
            "education_level": "Diploma",
            "field_of_study": "Hotel Management",
            "current_status": "unemployed",
            "technical_skills": ["Hospitality Management", "Food Service", "Customer Service"],
            "soft_skills": ["Communication", "Team Work", "Problem Solving"],
            "interests": ["Hospitality", "Tourism", "Business"],
            "hobbies": ["Cooking", "Travel", "Music"],
            "career_goals": "Start a beachside restaurant promoting local cuisine",
            "preferred_industries": ["Hospitality", "Tourism", "Entrepreneurship"],
            "job_search_status": "active",
            "entrepreneur_interest": True,
            "volunteer_interest": False,
            "social_issues": ["Tourism Development", "Local Culture"],
            "leadership_roles": ["College Cultural Committee"],
            "preferred_language": "kannada",
            "is_verified": True
        }
    ]
    
    # Create youth profiles for Mangalore North
    for i, youth_data in enumerate(mangalore_youth):
        citizen = mangalore_citizens[i % len(mangalore_citizens)]
        youth = YouthProfile(
            id=str(uuid.uuid4()),
            youth_id=citizen.id,
            constituency_id=mangalore.id,
            last_active_date=datetime.utcnow() - timedelta(days=i),
            created_at=datetime.utcnow() - timedelta(days=i*20),
            **youth_data
        )
        db.add(youth)
    
    print(f"Created {len(puttur_youth + mangalore_youth)} youth profiles")


def seed_youth_programs(db: Session):
    """Seed sample youth programs"""
    
    # Get constituencies and MLAs
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore City South").first()
    
    puttur_mla = db.query(User).filter(User.phone == "+919876543211").first()
    mangalore_mla = db.query(User).filter(User.phone == "+919876543212").first()
    
    if not puttur_mla or not mangalore_mla:
        print("Required MLA users not found, skipping youth programs")
        return
    
    # Sample youth programs
    youth_programs = [
        {
            "title": "Digital Skills for Rural Youth",
            "description": "Comprehensive training program on digital literacy, coding, and entrepreneurship for rural youth to prepare them for the digital economy.",
            "program_type": ProgramType.SKILL_DEVELOPMENT,
            "partner_organizations": ["National Skill Development Corporation", "Local IT Companies"],
            "start_date": datetime.utcnow() + timedelta(days=15),
            "end_date": datetime.utcnow() + timedelta(days=75),
            "application_deadline": datetime.utcnow() + timedelta(days=10),
            "duration_weeks": 8,
            "max_participants": 50,
            "min_age": 18,
            "max_age": 30,
            "education_requirements": "Minimum 10th pass",
            "skill_requirements": ["Basic computer knowledge"],
            "venue": "Community Hall, Puttur",
            "is_online": False,
            "is_hybrid": True,
            "meeting_link": "https://meet.janasamparka.in/digital-skills",
            "benefits": ["Free certification", "Placement assistance", "Startup mentoring"],
            "certification_offered": True,
            "certificate_type": "Digital Skills Professional",
            "placement_assistance": True,
            "stipend_amount": 3000.0,
            "status": "upcoming",
            "is_featured": True
        },
        {
            "title": "Young Leaders Development Program",
            "description": "Leadership and personality development program to identify and nurture future community leaders among youth.",
            "program_type": ProgramType.LEADERSHIP,
            "partner_organizations": ["Rotary Club", "Local Colleges"],
            "start_date": datetime.utcnow() + timedelta(days=30),
            "end_date": datetime.utcnow() + timedelta(days=90),
            "application_deadline": datetime.utcnow() + timedelta(days=25),
            "duration_weeks": 8,
            "max_participants": 30,
            "min_age": 20,
            "max_age": 35,
            "education_requirements": "Minimum Pre-University",
            "venue": "MLA Office, Puttur",
            "is_online": False,
            "benefits": ["Leadership certification", "Networking opportunities", "Community project experience"],
            "certification_offered": True,
            "certificate_type": "Young Leader",
            "placement_assistance": False,
            "status": "upcoming"
        },
        {
            "title": "Sports Talent Identification Camp",
            "description": "Comprehensive sports training and talent identification program for rural youth in cricket, football, and athletics.",
            "program_type": ProgramType.SPORTS,
            "partner_organizations": ["Sports Authority of Karnataka", "Local Sports Clubs"],
            "start_date": datetime.utcnow() + timedelta(days=20),
            "end_date": datetime.utcnow() + timedelta(days=50),
            "application_deadline": datetime.utcnow() + timedelta(days=15),
            "duration_weeks": 4,
            "max_participants": 100,
            "min_age": 15,
            "max_age": 25,
            "venue": "Sports Ground, Puttur",
            "is_online": False,
            "benefits": ["Professional coaching", "Sports kit", "Tournament participation"],
            "certification_offered": False,
            "placement_assistance": False,
            "status": "upcoming"
        },
        {
            "title": "Coastal Entrepreneurship Bootcamp",
            "description": "Intensive entrepreneurship development program focusing on coastal business opportunities, tourism, and marine resources.",
            "program_type": ProgramType.ENTREPRENEURSHIP,
            "partner_organizations": ["Karnataka Startup Cell", "Marine Business Association"],
            "start_date": datetime.utcnow() + timedelta(days=25),
            "end_date": datetime.utcnow() + timedelta(days=55),
            "application_deadline": datetime.utcnow() + timedelta(days=20),
            "duration_weeks": 4,
            "max_participants": 40,
            "min_age": 21,
            "max_age": 40,
            "education_requirements": "Minimum Diploma",
            "venue": "Marine Science Center, Mangalore",
            "is_online": False,
            "is_hybrid": True,
            "meeting_link": "https://meet.janasamparka.in/coastal-entrepreneurship",
            "benefits": ["Business plan development", "Mentorship", "Funding connections"],
            "certification_offered": True,
            "certificate_type": "Entrepreneurship Development",
            "placement_assistance": False,
            "status": "upcoming",
            "is_featured": True
        },
        {
            "title": "Environmental Conservation Volunteers",
            "description": "Youth volunteer program for environmental conservation, beach cleaning, and sustainable development initiatives.",
            "program_type": ProgramType.ENVIRONMENT,
            "partner_organizations": ["Environmental NGOs", "College Eco Clubs"],
            "start_date": datetime.utcnow() + timedelta(days=10),
            "end_date": datetime.utcnow() + timedelta(days=100),
            "application_deadline": datetime.utcnow() + timedelta(days=5),
            "duration_weeks": 12,
            "max_participants": 75,
            "min_age": 16,
            "max_age": 30,
            "venue": "Various locations across constituency",
            "is_online": False,
            "benefits": ["Volunteer certificate", "Environmental awareness", "Community service experience"],
            "certification_offered": True,
            "certificate_type": "Environmental Volunteer",
            "placement_assistance": False,
            "status": "upcoming"
        }
    ]
    
    # Create youth programs
    for i, program_data in enumerate(youth_programs):
        if i < 3:
            constituency_id = puttur.id
            organizer_id = puttur_mla.id
        else:
            constituency_id = mangalore.id
            organizer_id = mangalore_mla.id
        
        program = YouthProgram(
            id=str(uuid.uuid4()),
            constituency_id=constituency_id,
            organizer_id=organizer_id,
            created_at=datetime.utcnow() - timedelta(days=i*5),
            **program_data
        )
        db.add(program)
    
    print(f"Created {len(youth_programs)} youth programs")


def seed_career_requests(db: Session):
    """Seed sample career requests"""
    
    # Get youth profiles
    youth_profiles = db.query(YouthProfile).all()
    
    if not youth_profiles:
        print("No youth profiles found")
        return
    
    # Sample career requests
    career_requests = [
        {
            "career_field": CareerField.ENGINEERING,
            "request_type": "job_placement",
            "title": "Software Developer Job Opportunities",
            "description": "Looking for software developer job opportunities in Bangalore or Mangalore. Have skills in Python, Java, and web development.",
            "current_education": "Bachelor's in Computer Science Engineering",
            "target_companies": ["Infosys", "TCS", "Wipro", "Local IT Companies"],
            "salary_expectation": 400000.0,
            "preferred_location": "Bangalore, Mangalore",
            "relevant_skills": ["Python", "Java", "JavaScript", "React", "Node.js"],
            "certifications": ["Python Certification", "Web Development Certificate"],
            "work_experience": [{"company": "Internship at Tech Startup", "duration": "6 months", "role": "Junior Developer"}],
            "priority": "high",
            "urgency_level": "medium"
        },
        {
            "career_field": CareerField.ENTREPRENEURSHIP,
            "request_type": "guidance",
            "title": "Guidance for Agricultural Tech Startup",
            "description": "Need guidance and mentorship for starting an agricultural technology startup focused on farmer market connect.",
            "current_education": "Bachelor's in Computer Science",
            "target_companies": ["Self-employed"],
            "preferred_location": "Puttur",
            "relevant_skills": ["Programming", "Business Analysis", "Market Research"],
            "priority": "high",
            "urgency_level": "high"
        },
        {
            "career_field": CareerField.MEDICAL,
            "request_type": "guidance",
            "title": "Medical Career Guidance",
            "description": "Need guidance for medical career options and preparation for NEET PG exam.",
            "current_education": "MBBS",
            "target_companies": ["Government Hospitals", "Private Hospitals"],
            "preferred_location": "Karnataka",
            "relevant_skills": ["Medical Practice", "Patient Care", "Diagnosis"],
            "certifications": ["MBBS Degree"],
            "priority": "medium",
            "urgency_level": "medium"
        },
        {
            "career_field": CareerField.MANAGEMENT,
            "request_type": "job_placement",
            "title": "Business Management Opportunities",
            "description": "Looking for business management or consulting roles in local companies.",
            "current_education": "MBA",
            "target_companies": ["Local Industries", "Consulting Firms", "Banks"],
            "salary_expectation": 600000.0,
            "preferred_location": "Mangalore, Puttur",
            "relevant_skills": ["Business Analysis", "Financial Management", "Team Leadership"],
            "work_experience": [{"company": "Internship at Local Firm", "duration": "3 months", "role": "Management Trainee"}],
            "priority": "medium",
            "urgency_level": "low"
        },
        {
            "career_field": CareerField.CIVIL_SERVICES,
            "request_type": "guidance",
            "title": "UPSC Exam Preparation Guidance",
            "description": "Need guidance and study materials for UPSC civil services exam preparation.",
            "current_education": "Bachelor's in Arts",
            "preferred_location": "Bangalore for coaching",
            "relevant_skills": ["General Studies", "Current Affairs", "Analytical Skills"],
            "priority": "high",
            "urgency_level": "medium"
        }
    ]
    
    # Create career requests
    for i, request_data in enumerate(career_requests):
        youth = youth_profiles[i % len(youth_profiles)]
        request = CareerRequest(
            id=str(uuid.uuid4()),
            youth_id=youth.id,
            constituency_id=youth.constituency_id,
            created_at=datetime.utcnow() - timedelta(days=i*2),
            **request_data
        )
        db.add(request)
    
    print(f"Created {len(career_requests)} career requests")


def seed_training_programs(db: Session):
    """Seed sample training programs"""
    
    # Get constituencies and staff
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore City South").first()
    
    puttur_staff = db.query(User).filter(
        User.constituency_id == puttur.id,
        User.role == "moderator"
    ).first()
    
    mangalore_staff = db.query(User).filter(
        User.constituency_id == mangalore.id,
        User.role.in_(["moderator", "department_officer"])
    ).first()
    
    if not puttur_staff or not mangalore_staff:
        print("Required staff users not found, skipping training programs")
        return
    
    # Sample training programs
    training_programs = [
        {
            "title": "Advanced Organic Farming Techniques",
            "description": "Comprehensive training on advanced organic farming methods, certification processes, and market access for organic produce.",
            "training_category": "Agriculture",
            "training_partner": "Organic Farming Association",
            "start_date": datetime.utcnow() + timedelta(days=10),
            "end_date": datetime.utcnow() + timedelta(days=25),
            "duration_hours": 40,
            "session_frequency": "daily",
            "max_participants": 30,
            "min_participants": 15,
            "prerequisites": ["Basic farming experience"],
            "venue": "Agriculture Research Center, Puttur",
            "is_online": False,
            "certification_offered": True,
            "certificate_issuer": "Organic Farming Board",
            "training_cost": 0.0,
            "cost_sponsorship": {"sponsor": "MLA Office", "amount": 50000},
            "status": "upcoming",
            "is_free": True
        },
        {
            "title": "Digital Marketing for Small Businesses",
            "description": "Training program for small business owners on digital marketing, social media, and online sales strategies.",
            "training_category": "Business",
            "training_partner": "Local Digital Marketing Agency",
            "start_date": datetime.utcnow() + timedelta(days=20),
            "end_date": datetime.utcnow() + timedelta(days=35),
            "duration_hours": 30,
            "session_frequency": "weekend",
            "max_participants": 25,
            "min_participants": 10,
            "prerequisites": ["Basic computer knowledge"],
            "venue": "Community Hall, Puttur",
            "is_online": True,
            "meeting_link": "https://meet.janasamparka.in/digital-marketing",
            "certification_offered": True,
            "certificate_issuer": "Digital Skills Institute",
            "training_cost": 2000.0,
            "cost_sponsorship": {"sponsor": "50% subsidy", "amount": 1000},
            "status": "upcoming",
            "is_free": False
        },
        {
            "title": "Fisheries Value Addition Training",
            "description": "Training for fishermen on fish processing, value addition, and modern preservation techniques.",
            "training_category": "Fisheries",
            "training_partner": "Fisheries Department",
            "start_date": datetime.utcnow() + timedelta(days=15),
            "end_date": datetime.utcnow() + timedelta(days=30),
            "duration_hours": 35,
            "session_frequency": "daily",
            "max_participants": 20,
            "min_participants": 10,
            "prerequisites": ["Fishing experience"],
            "venue": "Fisheries Training Center, Mangalore",
            "is_online": False,
            "certification_offered": True,
            "certificate_issuer": "Fisheries Department",
            "training_cost": 0.0,
            "cost_sponsorship": {"sponsor": "Government Scheme", "amount": 75000},
            "status": "upcoming",
            "is_free": True
        },
        {
            "title": "Financial Literacy and Banking Services",
            "description": "Financial literacy program covering banking services, loan applications, and financial planning for farmers and small business owners.",
            "training_category": "Finance",
            "training_partner": "Local Banks",
            "start_date": datetime.utcnow() + timedelta(days=25),
            "end_date": datetime.utcnow() + timedelta(days=40),
            "duration_hours": 20,
            "session_frequency": "weekly",
            "max_participants": 50,
            "min_participants": 20,
            "prerequisites": ["Basic education"],
            "venue": "Bank Training Hall, Mangalore",
            "is_online": False,
            "certification_offered": True,
            "certificate_issuer": "Banking Institute",
            "training_cost": 0.0,
            "cost_sponsorship": {"sponsor": "Bank CSR", "amount": 30000},
            "status": "upcoming",
            "is_free": True
        }
    ]
    
    # Create training programs
    for i, program_data in enumerate(training_programs):
        if i < 2:
            constituency_id = puttur.id
            trainer_id = puttur_staff.id
        else:
            constituency_id = mangalore.id
            trainer_id = mangalore_staff.id
        
        program = TrainingProgram(
            id=str(uuid.uuid4()),
            constituency_id=constituency_id,
            trainer_id=trainer_id,
            created_at=datetime.utcnow() - timedelta(days=i*3),
            **program_data
        )
        db.add(program)
    
    print(f"Created {len(training_programs)} training programs")


def main():
    """Main function to seed all votebank engagement data"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("Seeding farmer data...")
        seed_farmer_data(db)
        
        print("Seeding crop requests...")
        seed_crop_requests(db)
        
        print("Seeding market listings...")
        seed_market_listings(db)
        
        print("Seeding business data...")
        seed_business_data(db)
        
        print("Seeding business requests...")
        seed_business_requests(db)
        
        print("Seeding youth data...")
        seed_youth_data(db)
        
        print("Seeding youth programs...")
        seed_youth_programs(db)
        
        print("Seeding career requests...")
        seed_career_requests(db)
        
        print("Seeding training programs...")
        seed_training_programs(db)
        
        # Commit all changes
        db.commit()
        print("✅ All votebank engagement data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
