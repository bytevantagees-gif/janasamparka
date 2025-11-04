"""
Re-seed Puttur constituency with correct coordinates only.
Deletes existing complaints and adds new ones with proper Puttur coordinates.
"""
import uuid
from datetime import datetime, timedelta, timezone
import random
from app.core.database import SessionLocal
from app.models.complaint import Complaint, ComplaintStatus, Media
from app.models.user import User
from app.models.constituency import Constituency

# Puttur locations with correct coordinates
# Puttur center: 12.7593° N, 75.2114° E
LOCATIONS = [
    (12.7593, 75.2114, "Puttur Town - Main Road"),
    (12.7620, 75.2140, "Puttur Bus Stand Area"),
    (12.7560, 75.2090, "Puttur Market Area"),
    (12.7650, 75.2100, "Puttur Hospital Road"),
    (12.7580, 75.2150, "Puttur College Road"),
    (12.7540, 75.2130, "Puttur Railway Station Road"),
    (12.7600, 75.2080, "Puttur Circle"),
    (12.7570, 75.2170, "Puttur Residential Area"),
    (12.7610, 75.2050, "Puttur Government Office Area"),
    (12.7590, 75.2190, "Puttur School Zone"),
    (12.7630, 75.2120, "Puttur Temple Street"),
    (12.7550, 75.2100, "Puttur Industrial Area"),
]

COMPLAINTS = [
    ("Pothole on main road", "Large pothole causing accidents", "roads", "high"),
    ("Street light not working", "Street light non-functional for a week", "electricity", "medium"),
    ("Water supply disruption", "No water supply for 3 days", "water", "urgent"),
    ("Garbage not collected", "Garbage not collected for over a week", "sanitation", "high"),
    ("Broken footpath", "Footpath broken and dangerous", "roads", "medium"),
    ("Overflowing drainage", "Drainage overflowing causing water logging", "sanitation", "high"),
    ("Traffic signal malfunction", "Traffic signal not working", "roads", "medium"),
    ("Park maintenance needed", "Park needs maintenance", "other", "low"),
    ("Bus stop shed damaged", "Bus stop shed needs repair", "roads", "medium"),
    ("Public toilet not maintained", "Public toilet in unhygienic condition", "sanitation", "high"),
]

STATUSES = [ComplaintStatus.SUBMITTED, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED]

def reseed_puttur():
    db = SessionLocal()
    try:
        # Get Puttur constituency
        puttur = db.query(Constituency).filter(Constituency.name == 'Puttur').first()
        if not puttur:
            print("❌ Puttur constituency not found!")
            return
        
        print(f"✅ Found Puttur constituency: {puttur.id}")
        
        # Delete existing media for Puttur complaints first
        media_deleted = db.query(Media).filter(
            Media.complaint_id.in_(
                db.query(Complaint.id).filter(Complaint.constituency_id == puttur.id)
            )
        ).delete(synchronize_session=False)
        db.commit()
        print(f"🗑️  Deleted {media_deleted} media records")
        
        # Delete existing complaints for Puttur
        deleted = db.query(Complaint).filter(Complaint.constituency_id == puttur.id).delete()
        db.commit()
        print(f"🗑️  Deleted {deleted} existing Puttur complaints")
        
        # Get a citizen user for Puttur
        citizen = db.query(User).filter(
            User.role == 'citizen',
            User.constituency_id == puttur.id
        ).first()
        
        if not citizen:
            print("⚠️  No citizen user found for Puttur, using first available user")
            citizen = db.query(User).filter(User.constituency_id == puttur.id).first()
        
        if not citizen:
            print("❌ No users found for Puttur constituency!")
            return
        
        print(f"✅ Using user: {citizen.name} ({citizen.id})")
        
        # Create complaints with correct Puttur coordinates
        created = 0
        for loc in LOCATIONS:
            complaint_data = random.choice(COMPLAINTS)
            status = random.choice(STATUSES)
            
            created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            updated_at = created_at + timedelta(hours=random.randint(1, 48))
            resolved_at = updated_at if status == ComplaintStatus.RESOLVED else None
            
            complaint = Complaint(
                id=uuid.uuid4(),
                constituency_id=puttur.id,
                user_id=citizen.id,
                title=complaint_data[0],
                description=complaint_data[1],
                category=complaint_data[2],
                lat=loc[0],
                lng=loc[1],
                location_description=loc[2],
                status=status,
                priority=complaint_data[3],
                created_at=created_at,
                updated_at=updated_at,
                resolved_at=resolved_at
            )
            
            db.add(complaint)
            created += 1
            print(f"✅ Created: {complaint_data[0]} at {loc[2]} ({loc[0]}, {loc[1]})")
        
        db.commit()
        print()
        print(f"🎉 Successfully created {created} complaints in Puttur!")
        print(f"📍 All complaints have coordinates around Puttur (12.76°N, 75.21°E)")
        print(f"🗺️  Visit http://localhost:3000/map to see them")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Re-seeding Puttur Constituency with Correct Coordinates")
    print("=" * 60)
    print()
    reseed_puttur()
