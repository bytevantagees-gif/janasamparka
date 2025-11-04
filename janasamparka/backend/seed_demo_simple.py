"""
Simple Demo Seed Data - Complaints and Citizens Only
Run after seed_data.py: python seed_demo_simple.py
"""
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.database import SessionLocal
from app.models.constituency import Constituency
from app.models.ward import Ward
from app.models.department import Department
from app.models.user import User
from app.models.complaint import Complaint

def random_date(days_ago=30):
    return datetime.utcnow() - timedelta(days=random.randint(0, days_ago))

def seed_demo():
    db = SessionLocal()
    
    try:
        print("🌱 Starting demo data creation...")
        print("="*80)
        
        constituencies = db.query(Constituency).all()
        if not constituencies:
            print("❌ No constituencies found. Run seed_data.py first!")
            return
        
        wards = db.query(Ward).all()
        departments = db.query(Department).all()
        
        print(f"✅ Found {len(constituencies)} constituencies, {len(wards)} wards")
        
        # Create 40 citizens
        print("\n📱 Creating 40 citizen users...")
        citizen_names = [
            "Ramesh Kumar", "Priya Shetty", "Suresh Bhat", "Anita Rao",
            "Mohan Poojary", "Lakshmi Nayak", "Ganesh Acharya", "Savita Kulkarni",
            "Prakash Shenoy", "Deepa Hegde", "Raghavendra Pai", "Manjula Karkera",
            "Dinesh Alva", "Suma Shetty", "Krishnamurthy Bhat", "Nandini Rao",
            "Santhosh Kumar", "Divya Prabhu", "Mahesh Shetty", "Rashmi Hegde",
            "Vijay Kumar", "Shwetha Rai", "Ashok Bhandary", "Kavitha Shetty",
            "Nagaraj Bhat", "Pooja Rao", "Ravi Kumar", "Asha Nayak",
            "Sudhir Shetty", "Meena Pai", "Girish Karkera", "Bharathi Shenoy",
            "Ravindra Alva", "Latha Kulkarni", "Shankar Hegde", "Sowmya Bhat",
            "Kiran Kumar", "Vidya Rao", "Jagadish Shetty", "Renuka Prabhu"
        ]
        
        citizens = []
        for i, name in enumerate(citizen_names):
            constituency = random.choice(constituencies)
            constituency_wards = [w for w in wards if w.constituency_id == constituency.id]
            ward = random.choice(constituency_wards) if constituency_wards else None
            
            citizen = User(
                id=uuid.uuid4(),
                name=name,
                phone=f"+919{800000000 + i:09d}",
                role="citizen",
                constituency_id=constituency.id,
                ward_id=ward.id if ward else None,
                locale_pref=random.choice(["kn", "en"]),
                is_active=True
            )
            db.add(citizen)
            citizens.append(citizen)
        
        db.flush()
        print(f"✅ Created {len(citizens)} citizens")
        
        # Create 15 department users
        print("\n👷 Creating department users...")
        dept_users = []
        for dept in departments:
            user = User(
                id=uuid.uuid4(),
                name=f"{dept.name} Officer",
                phone=f"+919{700000000 + len(dept_users):09d}",
                role="department_user",
                constituency_id=dept.constituency_id,
                locale_pref="kn",
                is_active=True
            )
            db.add(user)
            dept_users.append(user)
        
        db.flush()
        print(f"✅ Created {len(dept_users)} department users")
        
        # Create 100 realistic complaints
        print("\n📋 Creating 100 complaints...")
        
        complaint_templates = [
            ("Roads & Infrastructure", "Road full of potholes near Market junction causing daily accidents", "high"),
            ("Roads & Infrastructure", "Broken road divider near school zone - very dangerous for children", "urgent"),
            ("Water Supply", "No water supply for last 3 days in our area", "high"),
            ("Water Supply", "Water pipe leakage causing street flooding", "medium"),
            ("Electricity", "Frequent power cuts (4-5 times daily) affecting businesses", "high"),
            ("Electricity", "Exposed electric wires hanging dangerously low", "urgent"),
            ("Sanitation", "Overflowing sewage near residential area - unbearable smell", "high"),
            ("Garbage Collection", "Garbage not collected for 5 days creating health hazard", "medium"),
            ("Street Lights", "No street lights for 2 weeks - safety concern", "medium"),
            ("Public Transport", "Bus stop shelter damaged and needs immediate repair", "low"),
        ]
        
        statuses = ["submitted", "assigned", "in_progress", "resolved", "closed"]
        
        complaints = []
        for i in range(100):
            category, desc_template, priority = random.choice(complaint_templates)
            constituency = random.choice(constituencies)
            constituency_wards = [w for w in wards if w.constituency_id == constituency.id]
            ward = random.choice(constituency_wards) if constituency_wards else None
            constituency_citizens = [c for c in citizens if c.constituency_id == constituency.id]
            citizen = random.choice(constituency_citizens) if constituency_citizens else random.choice(citizens)
            constituency_depts = [d for d in departments if d.constituency_id == constituency.id]
            dept = random.choice(constituency_depts) if constituency_depts else random.choice(departments)
            
            status = random.choice(statuses)
            created_date = random_date(60)
            
            complaint = Complaint(
                id=uuid.uuid4(),
                title=f"{category} Issue #{i+1} - {ward.name if ward else 'Location'}",
                description=desc_template,
                category=category,
                priority=priority,
                status=status,
                user_id=citizen.id,
                constituency_id=constituency.id,
                ward_id=ward.id if ward else None,
                dept_id=dept.id,
                assigned_to=random.choice(dept_users).id if status in ["assigned", "in_progress", "resolved", "closed"] else None,
                lat=Decimal(str(12.8 + random.uniform(-0.5, 0.5))),
                lng=Decimal(str(74.85 + random.uniform(0, 0.4))),  # Fixed: 74.85-75.25 (all on land)
                location_description=f"{ward.name if ward else 'Area'}, {constituency.name}",
                created_at=created_date,
                updated_at=created_date + timedelta(days=random.randint(0, 10)) if status != "submitted" else created_date
            )
            db.add(complaint)
            complaints.append(complaint)
        
        db.commit()
        print(f"✅ Created {len(complaints)} complaints")
        
        print("\n" + "="*80)
        print("🎉 DEMO DATA CREATED SUCCESSFULLY!")
        print("="*80)
        print(f"\n📊 Summary:")
        print(f"   • {len(citizens)} Citizen Users (phones: +9198000XXXXX)")
        print(f"   • {len(dept_users)} Department Users (phones: +9197000XXXXX)")
        print(f"   • {len(complaints)} Complaints across all categories")
        
        status_counts = {}
        for c in complaints:
            status_counts[c.status] = status_counts.get(c.status, 0) + 1
        
        print(f"\n📈 Complaint Status Distribution:")
        for status, count in sorted(status_counts.items()):
            print(f"      • {status}: {count}")
        
        print("\n🚀 Ready for demo!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo()
