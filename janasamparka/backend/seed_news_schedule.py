"""
Seed script for news, MLA schedules, and ticker items
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db, engine
from app.models.news import News, NewsCategory, NewsPriority, MLASchedule, ScheduleType, ScheduleStatus, TickerItem
from app.models.user import User
from app.models.constituency import Constituency
import uuid


def seed_news_data(db: Session):
    """Seed sample news data"""
    
    # Get constituencies and users
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore North").first()
    
    puttur_mla = db.query(User).filter(User.phone == "+919876543211").first()
    mangalore_mla = db.query(User).filter(User.phone == "+919876543212").first()
    
    if not all([puttur, mangalore, puttur_mla, mangalore_mla]):
        print("Missing required users or constituencies")
        return
    
    # Sample news for Puttur
    puttur_news = [
        {
            "title": "New Road Construction Project Approved for Puttur Main Road",
            "content": "The government has approved a comprehensive road development project for the main road in Puttur. The project includes widening the existing road, improving drainage systems, and installing proper street lighting. This development will significantly improve connectivity and reduce traffic congestion in the area.",
            "summary": "Major road development project approved for Puttur with improved infrastructure",
            "category": NewsCategory.LOCAL_DEVELOPMENT,
            "priority": NewsPriority.HIGH,
            "is_published": True,
            "is_featured": True,
            "show_in_ticker": True,
            "source": "Government Press Release",
            "author": "District Information Office",
            "tags": ["infrastructure", "roads", "development", "puttur"]
        },
        {
            "title": "Free Health Camp Organized at Puttur Government Hospital",
            "content": "A comprehensive free health camp was organized at the Puttur Government Hospital, providing medical check-ups, consultations, and free medicines to over 500 citizens. Specialist doctors from various fields participated in the camp, offering services in general medicine, pediatrics, gynecology, and ophthalmology.",
            "summary": "Free health camp serves 500+ citizens with specialist consultations",
            "category": NewsCategory.PUBLIC_SERVICE,
            "priority": NewsPriority.MEDIUM,
            "is_published": True,
            "is_featured": False,
            "show_in_ticker": True,
            "source": "Health Department",
            "author": "Hospital Administration",
            "tags": ["healthcare", "camp", "public service", "puttur"]
        },
        {
            "title": "MLA Inaugurates New Water Supply Scheme in Rural Puttur",
            "content": "The newly elected MLA inaugurated a modern water supply scheme that will provide clean drinking water to 10 villages in rural Puttur. The project, costing Rs. 5 crores, includes a water treatment plant, storage tanks, and distribution network. This will solve the long-standing water scarcity issues in the region.",
            "summary": "New water supply scheme inaugurated for 10 villages in rural Puttur",
            "category": NewsCategory.GOVERNMENT_INITIATIVE,
            "priority": NewsPriority.HIGH,
            "is_published": True,
            "is_featured": True,
            "show_in_ticker": True,
            "source": "MLA Office",
            "author": "Press Secretary",
            "tags": ["water", "rural development", "infrastructure", "puttur"]
        },
        {
            "title": "Annual Sports Meet Concluded at Puttur College",
            "content": "The annual sports meet at Puttur College concluded with enthusiastic participation from students across various disciplines. Events included track and field, team sports, and cultural performances. The MLA distributed prizes to the winners and emphasized the importance of sports in overall development.",
            "summary": "Annual sports meet successfully concluded with student participation",
            "category": NewsCategory.OTHER,
            "priority": NewsPriority.LOW,
            "is_published": True,
            "is_featured": False,
            "show_in_ticker": False,
            "source": "College Administration",
            "author": "Sports Department",
            "tags": ["sports", "education", "college", "puttur"]
        }
    ]
    
    # Create news items for Puttur
    for news_data in puttur_news:
        news = News(
            id=str(uuid.uuid4()),
            constituency_id=puttur.id,
            mla_id=puttur_mla.id,
            created_by=puttur_mla.id,
            published_at=datetime.utcnow(),
            **news_data
        )
        db.add(news)
    
    # Sample news for Mangalore North
    mangalore_news = [
        {
            "title": "Coastal Protection Works to Begin Next Month",
            "content": "The government has sanctioned Rs. 20 crores for coastal protection works in Mangalore North. The project includes construction of sea walls, beach nourishment, and installation of warning systems. This will protect coastal communities from erosion and flooding during monsoon.",
            "summary": "Rs. 20 crore coastal protection project sanctioned for Mangalore North",
            "category": NewsCategory.LOCAL_DEVELOPMENT,
            "priority": NewsPriority.HIGH,
            "is_published": True,
            "is_featured": True,
            "show_in_ticker": True,
            "source": "Coastal Zone Management",
            "author": "Environmental Department",
            "tags": ["coastal", "protection", "environment", "mangalore"]
        },
        {
            "title": "Digital Literacy Program Launched for Senior Citizens",
            "content": "A special digital literacy program has been launched for senior citizens in Mangalore North. The program aims to teach basic computer skills, smartphone usage, and online safety to elderly citizens. Free training sessions will be conducted at community centers across the constituency.",
            "summary": "Digital literacy program launched for elderly citizens",
            "category": NewsCategory.PUBLIC_SERVICE,
            "priority": NewsPriority.MEDIUM,
            "is_published": True,
            "is_featured": False,
            "show_in_ticker": True,
            "source": "Education Department",
            "author": "Digital Initiative Team",
            "tags": ["digital", "literacy", "senior citizens", "mangalore"]
        }
    ]
    
    # Create news items for Mangalore North
    for news_data in mangalore_news:
        news = News(
            id=str(uuid.uuid4()),
            constituency_id=mangalore.id,
            mla_id=mangalore_mla.id,
            created_by=mangalore_mla.id,
            published_at=datetime.utcnow(),
            **news_data
        )
        db.add(news)
    
    print(f"Created {len(puttur_news + mangalore_news)} news items")


def seed_schedule_data(db: Session):
    """Seed sample MLA schedule data"""
    
    # Get constituencies and users
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore North").first()
    
    puttur_mla = db.query(User).filter(User.phone == "+919876543211").first()
    mangalore_mla = db.query(User).filter(User.phone == "+919876543212").first()
    
    # Generate schedules for the next 30 days
    base_date = datetime.utcnow()
    
    # Puttur MLA schedules
    puttur_schedules = [
        {
            "title": "Weekly Public Meeting",
            "description": "Meet with citizens to address their concerns and grievances",
            "schedule_type": ScheduleType.MEETING,
            "venue": "MLA Office, Puttur",
            "address": "Main Road, Puttur, Karnataka",
            "start_datetime": base_date + timedelta(days=1, hours=10),
            "end_datetime": base_date + timedelta(days=1, hours=13),
            "is_public": True,
            "is_featured": True,
            "contact_person": "Personal Secretary",
            "contact_phone": "+91-9876543210",
            "agenda": "1. Listen to citizen grievances\n2. Review development works\n3. Discuss local issues"
        },
        {
            "title": "Village Visit - Sulthan Bathery",
            "description": "Visit to inspect ongoing development works and meet with villagers",
            "schedule_type": ScheduleType.CAMP,
            "venue": "Village Community Center",
            "address": "Sulthan Bathery Village, Puttur Taluk",
            "start_datetime": base_date + timedelta(days=3, hours=9),
            "end_datetime": base_date + timedelta(days=3, hours=17),
            "is_public": True,
            "is_featured": False,
            "expected_attendees": 200,
            "contact_person": "Village Panchayat Head",
            "contact_phone": "+91-9876543211"
        },
        {
            "title": "Infrastructure Inspection",
            "description": "Inspection of newly constructed roads and drainage systems",
            "schedule_type": ScheduleType.INSPECTION,
            "venue": "Various Locations",
            "address": "Puttur Constituency",
            "start_datetime": base_date + timedelta(days=5, hours=8),
            "end_datetime": base_date + timedelta(days=5, hours=14),
            "is_public": False,
            "is_featured": False,
            "contact_person": "Engineer-in-Charge",
            "contact_phone": "+91-9876543212"
        },
        {
            "title": "Press Conference - Development Initiatives",
            "description": "Address media about upcoming development projects and achievements",
            "schedule_type": ScheduleType.PRESS_CONFERENCE,
            "venue": "Press Club",
            "address": "Mangalore Press Club, Karnataka",
            "start_datetime": base_date + timedelta(days=7, hours=11),
            "end_datetime": base_date + timedelta(days=7, hours=13),
            "is_public": True,
            "is_featured": True,
            "max_attendees": 50,
            "registration_required": True,
            "contact_person": "Press Secretary",
            "contact_email": "press@mlaputtur.in"
        },
        {
            "title": "Educational Institution Visit",
            "description": "Visit to Government College to interact with students and faculty",
            "schedule_type": ScheduleType.PUBLIC_EVENT,
            "venue": "Government College, Puttur",
            "address": "College Road, Puttur, Karnataka",
            "start_datetime": base_date + timedelta(days=10, hours=14),
            "end_datetime": base_date + timedelta(days=10, hours=17),
            "is_public": True,
            "is_featured": False,
            "expected_attendees": 500,
            "contact_person": "College Principal",
            "contact_phone": "+91-9876543213"
        }
    ]
    
    # Create schedules for Puttur MLA
    for schedule_data in puttur_schedules:
        schedule = MLASchedule(
            id=str(uuid.uuid4()),
            constituency_id=puttur.id,
            mla_id=puttur_mla.id,
            created_by=puttur_mla.id,
            **schedule_data
        )
        db.add(schedule)
    
    # Mangalore North MLA schedules
    mangalore_schedules = [
        {
            "title": "Coastal Area Development Meeting",
            "description": "Meeting with fishing community and coastal residents",
            "schedule_type": ScheduleType.MEETING,
            "venue": "Fishing Community Hall",
            "address": "Coastal Road, Mangalore North",
            "start_datetime": base_date + timedelta(days=2, hours=15),
            "end_datetime": base_date + timedelta(days=2, hours=18),
            "is_public": True,
            "is_featured": True,
            "expected_attendees": 150,
            "contact_person": "Community Leader",
            "contact_phone": "+91-9876543220"
        },
        {
            "title": "Beach Cleanliness Drive",
            "description": "Leading a beach cleanliness campaign with local volunteers",
            "schedule_type": ScheduleType.PUBLIC_EVENT,
            "venue": "Panambur Beach",
            "address": "Panambur, Mangalore North",
            "start_datetime": base_date + timedelta(days=4, hours=7),
            "end_datetime": base_date + timedelta(days=4, hours=10),
            "is_public": True,
            "is_featured": False,
            "expected_attendees": 300,
            "contact_person": "Environmental Group",
            "contact_phone": "+91-9876543221"
        },
        {
            "title": "Office Hours - Citizen Grievances",
            "description": "Regular office hours to meet citizens and address their issues",
            "schedule_type": ScheduleType.OFFICE_HOURS,
            "venue": "MLA Office",
            "address": "Mangalore North Constituency Office",
            "start_datetime": base_date + timedelta(days=6, hours=10),
            "end_datetime": base_date + timedelta(days=6, hours=16),
            "is_public": True,
            "is_featured": False,
            "contact_person": "Office Staff",
            "contact_phone": "+91-9876543222"
        }
    ]
    
    # Create schedules for Mangalore North MLA
    for schedule_data in mangalore_schedules:
        schedule = MLASchedule(
            id=str(uuid.uuid4()),
            constituency_id=mangalore.id,
            mla_id=mangalore_mla.id,
            created_by=mangalore_mla.id,
            **schedule_data
        )
        db.add(schedule)
    
    print(f"Created {len(puttur_schedules + mangalore_schedules)} schedule items")


def seed_ticker_data(db: Session):
    """Seed sample ticker items"""
    
    # Get constituencies and users
    puttur = db.query(Constituency).filter(Constituency.name == "Puttur").first()
    mangalore = db.query(Constituency).filter(Constituency.name == "Mangalore North").first()
    
    puttur_mla = db.query(User).filter(User.phone == "+919876543211").first()
    mangalore_mla = db.query(User).filter(User.phone == "+919876543212").first()
    
    # Ticker items for Puttur
    puttur_tickers = [
        {
            "content": "📢 Weekly Public Meeting every Monday 10 AM - 1 PM at MLA Office",
            "content_type": "announcement",
            "priority": 5,
            "background_color": "#007bff",
            "text_color": "#ffffff",
            "icon": "📢"
        },
        {
            "content": "🚧 Road construction work on Main Road - Traffic diversion advised",
            "content_type": "alert",
            "priority": 8,
            "background_color": "#dc3545",
            "text_color": "#ffffff",
            "icon": "🚧"
        },
        {
            "content": "💧 New water supply scheme inaugurated - 10 villages to benefit",
            "content_type": "info",
            "priority": 6,
            "background_color": "#28a745",
            "text_color": "#ffffff",
            "icon": "💧"
        },
        {
            "content": "🏥 Free health camp tomorrow at Government Hospital - All welcome",
            "content_type": "announcement",
            "priority": 4,
            "background_color": "#17a2b8",
            "text_color": "#ffffff",
            "icon": "🏥"
        }
    ]
    
    # Create ticker items for Puttur
    for ticker_data in puttur_tickers:
        ticker = TickerItem(
            id=str(uuid.uuid4()),
            constituency_id=puttur.id,
            mla_id=puttur_mla.id,
            created_by=puttur_mla.id,
            start_time=datetime.utcnow(),
            **ticker_data
        )
        db.add(ticker)
    
    # Ticker items for Mangalore North
    mangalore_tickers = [
        {
            "content": "🌊 Coastal protection works starting next month - Rs. 20 crore project",
            "content_type": "info",
            "priority": 7,
            "background_color": "#007bff",
            "text_color": "#ffffff",
            "icon": "🌊"
        },
        {
            "content": "💻 Digital literacy program for senior citizens - Register now",
            "content_type": "announcement",
            "priority": 3,
            "background_color": "#6f42c1",
            "text_color": "#ffffff",
            "icon": "💻"
        },
        {
            "content": "🏖️ Beach cleanliness drive this Saturday - Join us at Panambur",
            "content_type": "announcement",
            "priority": 5,
            "background_color": "#28a745",
            "text_color": "#ffffff",
            "icon": "🏖️"
        }
    ]
    
    # Create ticker items for Mangalore North
    for ticker_data in mangalore_tickers:
        ticker = TickerItem(
            id=str(uuid.uuid4()),
            constituency_id=mangalore.id,
            mla_id=mangalore_mla.id,
            created_by=mangalore_mla.id,
            start_time=datetime.utcnow(),
            **ticker_data
        )
        db.add(ticker)
    
    print(f"Created {len(puttur_tickers + mangalore_tickers)} ticker items")


def main():
    """Main function to seed all data"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("Seeding news data...")
        seed_news_data(db)
        
        print("Seeding schedule data...")
        seed_schedule_data(db)
        
        print("Seeding ticker data...")
        seed_ticker_data(db)
        
        # Commit all changes
        db.commit()
        print("✅ All news, schedule, and ticker data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
