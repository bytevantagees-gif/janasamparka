"""
Fix complaint coordinates to ensure all pins are on land, not in the Arabian Sea.
Updates longitude to be between 74.85 and 75.25 (all on Karnataka mainland).
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from decimal import Decimal
import random
from app.core.database import SessionLocal
from app.models.complaint import Complaint

def fix_coordinates():
    """Update all complaint coordinates to ensure they're on land."""
    db = SessionLocal()
    try:
        # Get all complaints
        complaints = db.query(Complaint).all()
        print(f"\n📍 Found {len(complaints)} complaints to check")
        
        fixed_count = 0
        sea_count = 0
        
        for complaint in complaints:
            if complaint.lng:
                lng_float = float(complaint.lng)
                
                # Check if longitude is in the sea (< 74.75)
                if lng_float < 74.75:
                    sea_count += 1
                    # Fix: generate new longitude between 74.85 and 75.25
                    new_lng = Decimal(str(74.85 + random.uniform(0, 0.4)))
                    old_lng = complaint.lng
                    complaint.lng = new_lng
                    fixed_count += 1
                    print(f"  🔧 Fixed complaint {str(complaint.id)[:8]}... : {old_lng} → {new_lng}")
        
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ Fixed {fixed_count} complaints that were in the sea")
            print(f"📊 Total: {len(complaints)} complaints, {sea_count} were in water, {fixed_count} fixed")
        else:
            print(f"\n✅ All {len(complaints)} complaints are already on land!")
        
    except Exception as e:
        print(f"❌ Error fixing coordinates: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_coordinates()
