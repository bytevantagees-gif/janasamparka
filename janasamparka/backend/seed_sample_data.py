"""
Seed sample data for testing the map and application
Run this script to populate the database with sample complaints with geolocation
"""
import asyncio
import uuid
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.complaint import Complaint
from app.models.user import User, UserRole
from app.models.constituency import Constituency
from app.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sample data for Bangalore constituencies (approximate coordinates)
SAMPLE_LOCATIONS = [
    # Shanti Nagar, Bangalore
    {"lat": 12.9716, "lng": 77.6412, "desc": "Near Shanti Nagar Circle"},
    {"lat": 12.9725, "lng": 77.6405, "desc": "Shanti Nagar Main Road"},
    {"lat": 12.9700, "lng": 77.6420, "desc": "Richmond Circle Area"},
    
    # Jayanagar, Bangalore
    {"lat": 12.9250, "lng": 77.5838, "desc": "Jayanagar 4th Block"},
    {"lat": 12.9280, "lng": 77.5850, "desc": "Jayanagar Shopping Complex"},
    {"lat": 12.9200, "lng": 77.5900, "desc": "Jayanagar 9th Block"},
    
    # Koramangala, Bangalore
    {"lat": 12.9352, "lng": 77.6245, "desc": "Koramangala 5th Block"},
    {"lat": 12.9300, "lng": 77.6270, "desc": "Koramangala 6th Block"},
    {"lat": 12.9400, "lng": 77.6280, "desc": "Koramangala 7th Block"},
    
    # Indiranagar, Bangalore
    {"lat": 12.9716, "lng": 77.6412, "desc": "Indiranagar 100 Feet Road"},
    {"lat": 12.9780, "lng": 77.6408, "desc": "Indiranagar 12th Main"},
    
    # Malleshwaram, Bangalore
    {"lat": 13.0067, "lng": 77.5697, "desc": "Malleshwaram 18th Cross"},
    {"lat": 13.0050, "lng": 77.5710, "desc": "Sampige Road"},
    
    # Rajajinagar, Bangalore
    {"lat": 12.9899, "lng": 77.5544, "desc": "Rajajinagar 4th Block"},
    {"lat": 12.9920, "lng": 77.5560, "desc": "Rajajinagar MICO Layout"},
]

COMPLAINT_TEMPLATES = [
    {
        "title": "Pothole on main road causing accidents",
        "description": "Large pothole on the main road is causing difficulties for vehicles and has led to minor accidents. Immediate repair required.",
        "category": "road",
        "priority": "high"
    },
    {
        "title": "Street light not working",
        "description": "Street light has been non-functional for the past week, causing safety concerns for residents at night.",
        "category": "electricity",
        "priority": "medium"
    },
    {
        "title": "Water supply disruption",
        "description": "No water supply for the past 3 days. Residents are facing severe difficulties.",
        "category": "water",
        "priority": "urgent"
    },
    {
        "title": "Garbage not collected",
        "description": "Garbage has not been collected for over a week. The area is becoming unhygienic.",
        "category": "sanitation",
        "priority": "high"
    },
    {
        "title": "Broken footpath",
        "description": "Footpath is broken and dangerous for pedestrians, especially elderly citizens.",
        "category": "road",
        "priority": "medium"
    },
    {
        "title": "Overflowing drainage",
        "description": "Drainage is overflowing and causing water logging in the area. Needs immediate attention.",
        "category": "sanitation",
        "priority": "high"
    },
    {
        "title": "Traffic signal malfunction",
        "description": "Traffic signal at the junction is not working properly, causing traffic congestion.",
        "category": "road",
        "priority": "medium"
    },
    {
        "title": "Park maintenance required",
        "description": "Local park needs maintenance. Broken benches and overgrown vegetation.",
        "category": "other",
        "priority": "low"
    }
]

STATUSES = [
    "submitted",
    "assigned",
    "in_progress",
    "resolved",
]

def create_sample_complaints():
    """Create sample complaints with geolocation data"""
    db = SessionLocal()
    try:
        # Get the first constituency and user
        constituency = db.query(Constituency).first()
        if not constituency:
            print("❌ No constituency found. Please run the setup script first.")
            return
        
        user = db.query(User).filter(User.role == UserRole.CITIZEN).first()
        if not user:
            # Create a sample citizen user
            user = User(
                id=uuid.uuid4(),
                name="Sample Citizen",
                phone="+919876543210",
                role=UserRole.CITIZEN,
                constituency_id=constituency.id,
                is_active="true"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        print(f"📍 Using constituency: {constituency.name}")
        print(f"👤 Using user: {user.name}")
        print()
        
        # Create complaints
        created_count = 0
        for i, location in enumerate(SAMPLE_LOCATIONS):
            template = random.choice(COMPLAINT_TEMPLATES)
            status = random.choice(STATUSES)
            
            # Create timestamps
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            updated_at = created_at + timedelta(hours=random.randint(1, 48))
            
            complaint = Complaint(
                id=uuid.uuid4(),
                constituency_id=constituency.id,
                user_id=user.id,
                title=template["title"],
                description=template["description"],
                category=template["category"],
                lat=location["lat"],
                lng=location["lng"],
                location_description=location["desc"],
                status=status,
                priority=template["priority"],
                created_at=created_at,
                updated_at=updated_at
            )
            
            if status == "resolved":
                complaint.resolved_at = updated_at
            
            db.add(complaint)
            created_count += 1
            
            print(f"✅ Created complaint {created_count}: {template['title'][:50]}... at {location['desc']}")
        
        db.commit()
        print()
        print(f"🎉 Successfully created {created_count} sample complaints with geolocation!")
        print(f"📍 Open http://localhost:3000/map to view them on the map")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 Seeding Sample Complaints with Geolocation")
    print("=" * 60)
    print()
    create_sample_complaints()
