"""
Fix coordinates for Puttur constituency complaints.
Updates existing complaints to have correct Puttur coordinates.
"""
from app.core.database import SessionLocal
from app.models.complaint import Complaint
from app.models.constituency import Constituency

# Puttur locations with correct coordinates
# Puttur center: 12.7593° N, 75.2114° E
PUTTUR_LOCATIONS = [
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
    (12.7645, 75.2125, "Puttur Market Complex"),
    (12.7555, 75.2145, "Puttur Police Station Area"),
    (12.7605, 75.2105, "Puttur Municipal Office"),
]

def fix_puttur_coordinates():
    db = SessionLocal()
    try:
        # Get Puttur constituency
        puttur = db.query(Constituency).filter(Constituency.name == 'Puttur').first()
        if not puttur:
            print("❌ Puttur constituency not found!")
            return
        
        print(f"✅ Found Puttur constituency: {puttur.id}")
        
        # Get all Puttur complaints
        complaints = db.query(Complaint).filter(Complaint.constituency_id == puttur.id).all()
        print(f"📊 Found {len(complaints)} complaints for Puttur")
        
        if not complaints:
            print("⚠️  No complaints to update")
            return
        
        # Update each complaint with correct Puttur coordinates
        updated = 0
        for i, complaint in enumerate(complaints):
            # Assign coordinates from our list, cycling through if needed
            location = PUTTUR_LOCATIONS[i % len(PUTTUR_LOCATIONS)]
            
            # Update the complaint (convert float to Decimal for SQLAlchemy)
            from decimal import Decimal
            complaint.lat = Decimal(str(location[0]))
            complaint.lng = Decimal(str(location[1]))
            if not complaint.location_description:
                complaint.location_description = location[2]
            
            updated += 1
            if updated <= 5:  # Show first 5
                print(f"✅ Updated: {complaint.title[:50]} → ({location[0]}, {location[1]}) {location[2]}")
        
        db.commit()
        print()
        print(f"🎉 Successfully updated {updated} complaints with correct Puttur coordinates!")
        print(f"📍 All complaints now have coordinates around Puttur (12.76°N, 75.21°E)")
        print(f"🗺️  Refresh http://localhost:3000/map to see the changes")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Fixing Puttur Constituency Coordinates")
    print("=" * 60)
    print()
    fix_puttur_coordinates()
