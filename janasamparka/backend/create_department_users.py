"""
Create department officers and auditors for testing
Run: docker compose exec backend python create_department_users.py
"""
import uuid
from app.core.database import SessionLocal
from app.models.user import User
from app.models.constituency import Constituency
from app.models.department import Department

def create_department_users():
    db = SessionLocal()
    
    try:
        print("🏢 Creating Department Officers and Auditors...")
        print("=" * 80)
        
        constituencies = db.query(Constituency).all()
        if not constituencies:
            print("❌ No constituencies found!")
            return
        
        created_users = []
        
        # Department types and their phone number ranges
        dept_configs = [
            ("PWD", "Public Works", "01"),
            ("Water", "Water Supply", "02"),
            ("Electricity", "Electricity", "03"),
            ("Health", "Health Department", "04"),
            ("Education", "Education", "05"),
        ]
        
        for i, const in enumerate(constituencies):
            print(f"\n📍 {const.name}")
            print("-" * 80)
            
            # Create department officers for each constituency
            for j, (dept_code, dept_name, dept_suffix) in enumerate(dept_configs):
                # Check if user already exists
                # Format: +91990 [dept_suffix] [constituency_index] 00
                # Example: +91990 01 0 00 = +91990010000 (PWD Puttur) - 10 digits after +91
                phone = f"+91990{dept_suffix}{i}00"
                existing = db.query(User).filter(User.phone == phone).first()
                
                if existing:
                    print(f"  ⚠️  {dept_name} Officer already exists: {existing.phone}")
                    continue
                
                # Get or create department
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
                created_users.append(officer)
                dept_info = f"[{department.name}]" if department else "[No Dept]"
                print(f"  ✅ Created: {officer.name:40} {officer.phone:15} {dept_info}")
            
            # Create auditor for each constituency
            auditor_phone = f"+91990060{i:02d}"
            existing_auditor = db.query(User).filter(User.phone == auditor_phone).first()
            
            if not existing_auditor:
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
                created_users.append(auditor)
                print(f"  ✅ Created: {auditor.name:40} {auditor.phone:15} [Auditor]")
            else:
                print(f"  ⚠️  Auditor already exists: {existing_auditor.phone}")
        
        if created_users:
            db.commit()
            print(f"\n{'=' * 80}")
            print(f"🎉 Created {len(created_users)} new users!")
        else:
            print(f"\n{'=' * 80}")
            print("✅ All users already exist!")
        
        # Summary
        print(f"\n{'=' * 80}")
        print("📋 USER SUMMARY")
        print("=" * 80)
        
        for role in ["moderator", "department_officer", "auditor"]:
            users = db.query(User).filter(User.role == role).all()
            print(f"\n{role.upper()}: {len(users)} users")
            for u in users:
                const = db.query(Constituency).filter(Constituency.id == u.constituency_id).first()
                const_name = const.name if const else 'N/A'
                dept = db.query(Department).filter(Department.id == u.department_id).first() if u.department_id else None
                dept_name = f"[{dept.name}]" if dept else ""
                print(f"  • {u.name:45} {u.phone:15} {const_name:20} {dept_name}")
        
        print(f"\n{'=' * 80}")
        print("🔐 TEST LOGIN CREDENTIALS")
        print("=" * 80)
        print("\n👮 Moderators:")
        mods = db.query(User).filter(User.role == "moderator").all()
        for m in mods:
            const = db.query(Constituency).filter(Constituency.id == m.constituency_id).first()
            print(f"  {m.phone}  →  {m.name} ({const.name if const else 'N/A'})")
        
        print("\n🏢 Department Officers:")
        officers = db.query(User).filter(User.role == "department_officer").all()
        for o in officers:
            const = db.query(Constituency).filter(Constituency.id == o.constituency_id).first()
            dept = db.query(Department).filter(Department.id == o.department_id).first() if o.department_id else None
            dept_info = f" - {dept.name}" if dept else ""
            print(f"  {o.phone}  →  {const.name if const else 'N/A'}{dept_info}")
        
        print("\n📊 Auditors:")
        auditors = db.query(User).filter(User.role == "auditor").all()
        for a in auditors:
            const = db.query(Constituency).filter(Constituency.id == a.constituency_id).first()
            print(f"  {a.phone}  →  {a.name} ({const.name if const else 'N/A'})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_department_users()
