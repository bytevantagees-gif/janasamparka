"""
Seed database with initial data for development/testing
This script creates all necessary users, constituencies, and departments
Run: docker compose exec backend python seed_database.py
"""
import uuid
from app.core.database import SessionLocal
from app.models.user import User
from app.models.constituency import Constituency
from app.models.department import Department

def seed_database():
    db = SessionLocal()
    
    try:
        print("🌱 Seeding Database...")
        print("=" * 80)
        
        # Get all constituencies
        constituencies = db.query(Constituency).all()
        if not constituencies:
            print("❌ No constituencies found! Run migrations first.")
            return
        
        print(f"✅ Found {len(constituencies)} constituencies")
        
        # Create Moderators
        print("\n🔐 Creating Moderators...")
        print("-" * 80)
        for i, const in enumerate(constituencies):
            existing = db.query(User).filter(
                User.role == "moderator",
                User.constituency_id == const.id
            ).first()
            
            if existing:
                print(f"  ⚠️  Moderator already exists for {const.name}: {existing.phone}")
                continue
            
            mod = User(
                id=uuid.uuid4(),
                name=f"{const.name} Moderator",
                phone=f"+9199000000{i:02d}",  # +919900000000, +919900000001, +919900000002
                role="moderator",
                constituency_id=const.id,
                ward_id=None,
                is_active=True,
                locale_pref="en"
            )
            db.add(mod)
            print(f"  ✅ {mod.name}: {mod.phone}")
        
        # Create Department Officers
        print("\n🏢 Creating Department Officers...")
        print("-" * 80)
        dept_configs = [
            ("PWD", "Public Works", "01"),
            ("Water", "Water Supply", "02"),
            ("Electricity", "Electricity", "03"),
            ("Health", "Health", "04"),
            ("Education", "Education", "05"),
        ]
        
        for i, const in enumerate(constituencies):
            print(f"\n  📍 {const.name}")
            
            for dept_code, dept_name, dept_suffix in dept_configs:
                # Phone format: +91990[dept_suffix][constituency_index]00
                # Example: +91990 01 0 00 = +9199001000 (10 digits after +91)
                phone = f"+91990{dept_suffix}{i}00"
                
                existing = db.query(User).filter(User.phone == phone).first()
                if existing:
                    print(f"    ⚠️  {dept_name} Officer already exists: {existing.phone}")
                    continue
                
                # Get department
                department = db.query(Department).filter(
                    Department.name.ilike(f"%{dept_code}%"),
                    Department.constituency_id == const.id
                ).first()
                
                officer = User(
                    id=uuid.uuid4(),
                    name=f"{dept_name} Officer - {const.name}",
                    phone=phone,
                    role="department_officer",
                    constituency_id=const.id,
                    department_id=department.id if department else None,
                    ward_id=None,
                    is_active=True,
                    locale_pref="en"
                )
                db.add(officer)
                print(f"    ✅ {dept_name:20} {phone:15} [{department.name if department else 'No Dept'}]")
        
        # Create Auditors
        print("\n📊 Creating Auditors...")
        print("-" * 80)
        for i, const in enumerate(constituencies):
            auditor_phone = f"+91990060{i:02d}"  # +9199006000, +9199006001, +9199006002
            
            existing = db.query(User).filter(User.phone == auditor_phone).first()
            if existing:
                print(f"  ⚠️  Auditor already exists for {const.name}: {existing.phone}")
                continue
            
            auditor = User(
                id=uuid.uuid4(),
                name=f"Auditor - {const.name}",
                phone=auditor_phone,
                role="auditor",
                constituency_id=const.id,
                ward_id=None,
                is_active=True,
                locale_pref="en"
            )
            db.add(auditor)
            print(f"  ✅ {auditor.name}: {auditor.phone}")
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎉 Database Seeding Complete!")
        print("=" * 80)
        
        # Count users by role
        for role in ["moderator", "department_officer", "auditor"]:
            count = db.query(User).filter(User.role == role).count()
            print(f"  {role:20} {count:3} users")
        
        print("\n📋 Login Credentials:")
        print("-" * 80)
        print("  Moderators:         +919900000000, +919900000001, +919900000002")
        print("  Dept Officers:      +9199001000 to +9199005200 (15 total)")
        print("  Auditors:           +9199006000, +9199006001, +9199006002")
        print("\n  Default Password:   demo (hashed in database)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
