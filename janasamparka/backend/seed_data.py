"""
Seed data script for initial constituencies setup
Run this after database migration: python seed_data.py
"""
import uuid
from datetime import datetime
from app.core.database import SessionLocal
from app.models.constituency import Constituency
from app.models.ward import Ward
from app.models.department import Department
from app.models.user import User

def seed_constituencies():
    """Create 3 initial constituencies"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting seed data creation...")
        
        # Check if constituencies already exist
        existing = db.query(Constituency).count()
        if existing > 0:
            print(f"⚠️  Found {existing} existing constituencies. Skipping...")
            return
        
        # ========================================
        # 1. PUTTUR CONSTITUENCY
        # ========================================
        print("\n📍 Creating Puttur constituency...")
        puttur = Constituency(
            id=uuid.uuid4(),
            name="Puttur",
            code="PUT001",
            district="Dakshina Kannada",
            state="Karnataka",
            mla_name="Ashok Kumar Rai",
            mla_party="Indian National Congress",
            mla_contact_phone="+918242226666",
            mla_contact_email="ashok.rai@karnataka.gov.in",
            assembly_number=172,
            total_wards=35,
            total_population=145000,
            is_active=True,
            subscription_tier="premium",
            description="Puttur is a major town and the headquarters of Puttur taluk in Dakshina Kannada district.",
            activated_at=datetime.utcnow()
        )
        db.add(puttur)
        db.flush()
        
        # Add sample wards for Puttur
        puttur_wards = [
            {"name": "Ward 1 - Market Area", "ward_number": 1, "taluk": "Puttur", "population": 4500},
            {"name": "Ward 2 - Bus Stand", "ward_number": 2, "taluk": "Puttur", "population": 4200},
            {"name": "Ward 3 - Nehru Nagar", "ward_number": 3, "taluk": "Puttur", "population": 3800},
            {"name": "Ward 4 - Gandhi Circle", "ward_number": 4, "taluk": "Puttur", "population": 4100},
            {"name": "Ward 5 - Railway Station", "ward_number": 5, "taluk": "Puttur", "population": 3900},
        ]
        
        for ward_data in puttur_wards:
            ward = Ward(
                id=uuid.uuid4(),
                constituency_id=puttur.id,
                **ward_data
            )
            db.add(ward)
        
        # Add departments for Puttur
        puttur_departments = [
            {"name": "Public Works Department", "code": "PWD", "contact_phone": "+918242226001"},
            {"name": "Water Supply & Drainage", "code": "WATER", "contact_phone": "+918242226002"},
            {"name": "Electricity (MESCOM)", "code": "MESCOM", "contact_phone": "+918242226003"},
            {"name": "Health & Family Welfare", "code": "HEALTH", "contact_phone": "+918242226004"},
            {"name": "Education Department", "code": "EDU", "contact_phone": "+918242226005"},
        ]
        
        for dept_data in puttur_departments:
            dept = Department(
                id=uuid.uuid4(),
                constituency_id=puttur.id,
                **dept_data
            )
            db.add(dept)
        
        # Create MLA user for Puttur
        puttur_mla = User(
            id=uuid.uuid4(),
            name="Ashok Kumar Rai",
            phone="+918242226666",
            role="mla",
            constituency_id=puttur.id,
            locale_pref="kn",
            is_active=True
        )
        db.add(puttur_mla)
        
        print(f"✅ Puttur constituency created with {len(puttur_wards)} wards and {len(puttur_departments)} departments")
        
        # ========================================
        # 2. MANGALORE NORTH CONSTITUENCY
        # ========================================
        print("\n📍 Creating Mangalore North constituency...")
        mangalore = Constituency(
            id=uuid.uuid4(),
            name="Mangalore North",
            code="MNG001",
            district="Dakshina Kannada",
            state="Karnataka",
            mla_name="B.A. Mohiuddin Bava",
            mla_party="Indian National Congress",
            mla_contact_phone="+918242227777",
            mla_contact_email="bava@karnataka.gov.in",
            assembly_number=129,
            total_wards=45,
            total_population=180000,
            is_active=True,
            subscription_tier="premium",
            description="Mangalore North is an urban constituency covering northern parts of Mangalore city.",
            activated_at=datetime.utcnow()
        )
        db.add(mangalore)
        db.flush()
        
        # Add sample wards for Mangalore
        mangalore_wards = [
            {"name": "Ward 1 - Kadri", "ward_number": 1, "taluk": "Mangalore", "population": 5200},
            {"name": "Ward 2 - Pandeshwar", "ward_number": 2, "taluk": "Mangalore", "population": 6100},
            {"name": "Ward 3 - Hampankatta", "ward_number": 3, "taluk": "Mangalore", "population": 5800},
            {"name": "Ward 4 - Bunder", "ward_number": 4, "taluk": "Mangalore", "population": 4900},
            {"name": "Ward 5 - Light House Hill", "ward_number": 5, "taluk": "Mangalore", "population": 5400},
        ]
        
        for ward_data in mangalore_wards:
            ward = Ward(
                id=uuid.uuid4(),
                constituency_id=mangalore.id,
                **ward_data
            )
            db.add(ward)
        
        # Add departments for Mangalore
        mangalore_departments = [
            {"name": "Public Works Department", "code": "PWD", "contact_phone": "+918242227001"},
            {"name": "Water Supply & Drainage", "code": "WATER", "contact_phone": "+918242227002"},
            {"name": "Electricity (MESCOM)", "code": "MESCOM", "contact_phone": "+918242227003"},
            {"name": "Health & Family Welfare", "code": "HEALTH", "contact_phone": "+918242227004"},
            {"name": "Education Department", "code": "EDU", "contact_phone": "+918242227005"},
        ]
        
        for dept_data in mangalore_departments:
            dept = Department(
                id=uuid.uuid4(),
                constituency_id=mangalore.id,
                **dept_data
            )
            db.add(dept)
        
        # Create MLA user for Mangalore
        mangalore_mla = User(
            id=uuid.uuid4(),
            name="B.A. Mohiuddin Bava",
            phone="+918242227777",
            role="mla",
            constituency_id=mangalore.id,
            locale_pref="kn",
            is_active=True
        )
        db.add(mangalore_mla)
        
        print(f"✅ Mangalore North constituency created with {len(mangalore_wards)} wards and {len(mangalore_departments)} departments")
        
        # ========================================
        # 3. UDUPI CONSTITUENCY
        # ========================================
        print("\n📍 Creating Udupi constituency...")
        udupi = Constituency(
            id=uuid.uuid4(),
            name="Udupi",
            code="UDU001",
            district="Udupi",
            state="Karnataka",
            mla_name="Yashpal A. Suvarna",
            mla_party="Bharatiya Janata Party",
            mla_contact_phone="+918252255555",
            mla_contact_email="yashpal.suvarna@karnataka.gov.in",
            assembly_number=156,
            total_wards=40,
            total_population=160000,
            is_active=True,
            subscription_tier="premium",
            description="Udupi is a coastal constituency known for Krishna Temple and educational institutions.",
            activated_at=datetime.utcnow()
        )
        db.add(udupi)
        db.flush()
        
        # Add sample wards for Udupi
        udupi_wards = [
            {"name": "Ward 1 - Car Street", "ward_number": 1, "taluk": "Udupi", "population": 4800},
            {"name": "Ward 2 - Temple Area", "ward_number": 2, "taluk": "Udupi", "population": 5200},
            {"name": "Ward 3 - Rajangana", "ward_number": 3, "taluk": "Udupi", "population": 4600},
            {"name": "Ward 4 - Manipal Road", "ward_number": 4, "taluk": "Udupi", "population": 5100},
            {"name": "Ward 5 - Beach Area", "ward_number": 5, "taluk": "Udupi", "population": 4400},
        ]
        
        for ward_data in udupi_wards:
            ward = Ward(
                id=uuid.uuid4(),
                constituency_id=udupi.id,
                **ward_data
            )
            db.add(ward)
        
        # Add departments for Udupi
        udupi_departments = [
            {"name": "Public Works Department", "code": "PWD", "contact_phone": "+918252255001"},
            {"name": "Water Supply & Drainage", "code": "WATER", "contact_phone": "+918252255002"},
            {"name": "Electricity (MESCOM)", "code": "MESCOM", "contact_phone": "+918252255003"},
            {"name": "Health & Family Welfare", "code": "HEALTH", "contact_phone": "+918252255004"},
            {"name": "Education Department", "code": "EDU", "contact_phone": "+918252255005"},
        ]
        
        for dept_data in udupi_departments:
            dept = Department(
                id=uuid.uuid4(),
                constituency_id=udupi.id,
                **dept_data
            )
            db.add(dept)
        
        # Create MLA user for Udupi
        udupi_mla = User(
            id=uuid.uuid4(),
            name="Yashpal A. Suvarna",
            phone="+918252255555",
            role="mla",
            constituency_id=udupi.id,
            locale_pref="kn",
            is_active=True
        )
        db.add(udupi_mla)
        
        print(f"✅ Udupi constituency created with {len(udupi_wards)} wards and {len(udupi_departments)} departments")
        
        # ========================================
        # CREATE SUPER ADMIN USER
        # ========================================
        print("\n👤 Creating super admin user...")
        admin = User(
            id=uuid.uuid4(),
            name="System Administrator",
            phone="+919999999999",
            role="admin",
            constituency_id=None,  # Admin can access all constituencies
            locale_pref="en",
            is_active=True
        )
        db.add(admin)
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*60)
        print("🎉 Seed data created successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   ✅ 3 Constituencies created")
        print(f"   ✅ 15 Wards created (5 per constituency)")
        print(f"   ✅ 15 Departments created (5 per constituency)")
        print(f"   ✅ 3 MLA users created")
        print(f"   ✅ 1 Super admin created")
        print("\n" + "="*60)
        print("\n🔑 Test Credentials:")
        print("\n   MLA Logins:")
        print(f"   - Puttur MLA: +918242226666")
        print(f"   - Mangalore North MLA: +918242227777")
        print(f"   - Udupi MLA: +918252255555")
        print("\n   Super Admin:")
        print(f"   - Admin: +919999999999")
        print("\n" + "="*60)
        print("\n🚀 Next Steps:")
        print("   1. Start the backend: uvicorn app.main:app --reload")
        print("   2. Visit: http://localhost:8000/docs")
        print("   3. Test endpoint: GET /api/constituencies")
        print("   4. Request OTP for any MLA phone number")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_constituencies()
