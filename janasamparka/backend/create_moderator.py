"""
Create moderator users for testing
Run: docker compose exec backend python create_moderator.py
"""
import uuid
from app.core.database import SessionLocal
from app.models.user import User
from app.models.constituency import Constituency

def create_moderators():
    db = SessionLocal()
    
    try:
        print("🔐 Creating Moderator Users...")
        print("=" * 60)
        
        constituencies = db.query(Constituency).all()
        if not constituencies:
            print("❌ No constituencies found!")
            return
        
        moderators = []
        for i, const in enumerate(constituencies):
            # Check if moderator already exists
            existing = db.query(User).filter(
                User.role == "moderator",
                User.constituency_id == const.id
            ).first()
            
            if existing:
                print(f"⚠️  Moderator already exists for {const.name}: {existing.phone}")
                continue
            
            mod = User(
                id=uuid.uuid4(),
                name=f"{const.name} Moderator",
                phone=f"+9199000000{i:02d}",
                role="moderator",
                constituency_id=const.id,
                ward_id=None,
                is_active=True,
                locale_pref="en"
            )
            db.add(mod)
            moderators.append(mod)
            print(f"✅ Created: {mod.name}")
            print(f"   Phone: {mod.phone}")
            print(f"   Constituency: {const.name}")
            print("-" * 60)
        
        if moderators:
            db.commit()
            print(f"\n🎉 Created {len(moderators)} moderator users!")
        else:
            print("\n✅ All moderators already exist!")
        
        # Print all moderators
        all_mods = db.query(User).filter(User.role == "moderator").all()
        print(f"\n📋 All Moderators ({len(all_mods)}):")
        print("=" * 60)
        for mod in all_mods:
            const = db.query(Constituency).filter(Constituency.id == mod.constituency_id).first()
            print(f"• {mod.name}")
            print(f"  Phone: {mod.phone}")
            print(f"  Constituency: {const.name if const else 'None'}")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_moderators()
