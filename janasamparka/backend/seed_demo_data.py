"""
Comprehensive Demo Seed Data Script for MLA Demo
Creates realistic data across all modules for demonstration purposes
Run after seed_data.py: python seed_demo_data.py
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
from app.models.news import News, MLASchedule, TickerItem
from app.models.poll import Poll, PollOption, Vote
from app.models.citizen_engagement import CitizenFeedback, VideoConference

def random_date(days_ago=30):
    """Generate a random date within the last N days"""
    return datetime.utcnow() - timedelta(days=random.randint(0, days_ago))

def random_phone():
    """Generate a random Indian phone number"""
    return f"+919{random.randint(100000000, 999999999)}"

def seed_demo_data():
    """Create comprehensive demo data"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting comprehensive demo data creation...")
        print("="*80)
        
        # Get constituencies
        constituencies = db.query(Constituency).all()
        if not constituencies:
            print("❌ No constituencies found. Please run seed_data.py first!")
            return
        
        print(f"✅ Found {len(constituencies)} constituencies")
        
        # Get wards and departments
        wards = db.query(Ward).all()
        departments = db.query(Department).all()
        mla_users = db.query(User).filter(User.role == "mla").all()
        
        print(f"✅ Found {len(wards)} wards and {len(departments)} departments")
        
        # ========================================
        # 1. CREATE CITIZEN USERS
        # ========================================
        print("\n📱 Creating citizen users...")
        
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
            ward = random.choice([w for w in wards if w.constituency_id == constituency.id])
            
            citizen = User(
                id=uuid.uuid4(),
                name=name,
                phone=f"+919{800000000 + i:09d}",
                role="citizen",
                constituency_id=constituency.id,
                ward_id=ward.id,
                locale_pref=random.choice(["kn", "en"]),
                is_active=True
            )
            db.add(citizen)
            citizens.append(citizen)
        
        db.flush()
        print(f"✅ Created {len(citizens)} citizen users")
        
        # ========================================
        # 2. CREATE DEPARTMENT USERS
        # ========================================
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
        
        # ========================================
        # 3. CREATE COMPLAINTS
        # ========================================
        print("\n📋 Creating complaints...")
        
        complaint_categories = [
            "Roads & Infrastructure", "Water Supply", "Electricity", 
            "Sanitation", "Street Lights", "Drainage", "Garbage Collection",
            "Public Transport", "Health Services", "Education"
        ]
        
        complaint_descriptions = {
            "Roads & Infrastructure": [
                "Road full of potholes near Market junction. Causing accidents daily.",
                "Broken road divider near school zone. Very dangerous for children.",
                "Missing speed breakers near residential area.",
                "Road construction incomplete for 6 months. Heavy traffic jam."
            ],
            "Water Supply": [
                "No water supply for last 3 days in our area.",
                "Water pipe leakage causing flooding in the street.",
                "Low water pressure during peak hours.",
                "Contaminated water supply. Many people falling sick."
            ],
            "Electricity": [
                "Frequent power cuts (4-5 times daily) affecting businesses.",
                "Exposed electric wires hanging dangerously low.",
                "Transformer making loud noise and sparking.",
                "No street lights for 2 weeks. Safety concern."
            ],
            "Sanitation": [
                "Overflowing sewage near residential area. Unbearable smell.",
                "Public toilet in very poor condition and not maintained.",
                "Open drainage causing health hazards.",
                "Sanitary waste not collected for 1 week."
            ],
            "Garbage Collection": [
                "Garbage not collected for 5 days. Creating health hazard.",
                "Garbage truck doesn't come to our street regularly.",
                "Dumping yard near residential area causing problems.",
                "Plastic waste burning causing air pollution."
            ]
        }
        
        priorities = ["low", "medium", "high", "urgent"]
        statuses = ["new", "assigned", "in_progress", "resolved", "closed"]
        
        complaints = []
        for i in range(80):  # Create 80 complaints
            category = random.choice(complaint_categories)
            descriptions = complaint_descriptions.get(category, ["General complaint"])
            
            constituency = random.choice(constituencies)
            ward = random.choice([w for w in wards if w.constituency_id == constituency.id])
            citizen = random.choice([c for c in citizens if c.constituency_id == constituency.id])
            dept = random.choice([d for d in departments if d.constituency_id == constituency.id])
            
            status = random.choice(statuses)
            created_date = random_date(60)
            
            complaint = Complaint(
                id=uuid.uuid4(),
                title=f"{category} Issue - Ward {ward.ward_number}",
                description=random.choice(descriptions),
                category=category,
                priority=random.choice(priorities),
                status=status,
                user_id=citizen.id,
                constituency_id=constituency.id,
                ward_id=ward.id,
                dept_id=dept.id,
                assigned_to=random.choice(dept_users).id if status != "new" and status != "submitted" else None,
                lat=Decimal(str(12.8 + random.uniform(-0.5, 0.5))),
                lng=Decimal(str(74.85 + random.uniform(0, 0.4))),  # Fixed: 74.85-75.25 (all on land)
                location_description=f"Ward {ward.ward_number}, {ward.name}, {constituency.name}",
                created_at=created_date,
                updated_at=created_date + timedelta(days=random.randint(0, 10)) if status != "submitted" else created_date
            )
            db.add(complaint)
            complaints.append(complaint)
        
        db.flush()
        print(f"✅ Created {len(complaints)} complaints")
        
        # ========================================
        # 4. CREATE NEWS ARTICLES
        # ========================================
        print("\n📰 Creating news articles...")
        
        news_articles = []
        news_data = [
            {
                "title_en": "New Road Development Project Approved",
                "title_kn": "ಹೊಸ ರಸ್ತೆ ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗೆ ಅನುಮೋದನೆ",
                "content_en": "The government has approved a major road development project worth Rs. 50 crores for our constituency. The project will cover 25 km of roads and is expected to be completed within 18 months.",
                "content_kn": "ನಮ್ಮ ಕ್ಷೇತ್ರಕ್ಕೆ 50 ಕೋಟಿ ರೂಪಾಯಿಗಳ ಪ್ರಮುಖ ರಸ್ತೆ ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗೆ ಸರ್ಕಾರ ಅನುಮೋದನೆ ನೀಡಿದೆ.",
                "category": "Development"
            },
            {
                "title_en": "Healthcare Initiative Launched for Senior Citizens",
                "title_kn": "ಹಿರಿಯ ನಾಗರಿಕರಿಗೆ ಆರೋಗ್ಯ ಕಾರ್ಯಕ್ರಮ ಪ್ರಾರಂಭ",
                "content_en": "A new healthcare program providing free medical checkups and medicines for senior citizens has been launched. Mobile health units will visit all wards.",
                "content_kn": "ಹಿರಿಯ ನಾಗರಿಕರಿಗೆ ಉಚಿತ ವೈದ್ಯಕೀಯ ತಪಾಸಣೆ ಮತ್ತು ಔಷಧಿಗಳನ್ನು ಒದಗಿಸುವ ಹೊಸ ಆರೋಗ್ಯ ಕಾರ್ಯಕ್ರಮ ಪ್ರಾರಂಭವಾಗಿದೆ.",
                "category": "Healthcare"
            },
            {
                "title_en": "Education Scholarship Program Announced",
                "title_kn": "ಶಿಕ್ಷಣ ವಿದ್ಯಾರ್ಥಿವೇತನ ಕಾರ್ಯಕ್ರಮ ಘೋಷಣೆ",
                "content_en": "Merit-based scholarships worth Rs. 1000 per month will be provided to 500 students from economically weaker sections.",
                "content_kn": "ಆರ್ಥಿಕವಾಗಿ ದುರ್ಬಲ ವರ್ಗದ 500 ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ತಿಂಗಳಿಗೆ 1000 ರೂಪಾಯಿಗಳ ಅರ್ಹತಾ ಆಧಾರಿತ ವಿದ್ಯಾರ್ಥಿವೇತನ ನೀಡಲಾಗುವುದು.",
                "category": "Education"
            },
            {
                "title_en": "Water Supply Improvement Project Completed",
                "title_kn": "ನೀರು ಪೂರೈಕೆ ಸುಧಾರಣೆ ಯೋಜನೆ ಪೂರ್ಣಗೊಂಡಿದೆ",
                "content_en": "Major water supply improvement work has been completed. All wards will now receive 24x7 water supply with improved pressure.",
                "content_kn": "ಪ್ರಮುಖ ನೀರು ಪೂರೈಕೆ ಸುಧಾರಣೆ ಕಾರ್ಯ ಪೂರ್ಣಗೊಂಡಿದೆ. ಎಲ್ಲಾ ವಾರ್ಡ್‌ಗಳಿಗೆ ಈಗ 24x7 ನೀರು ಪೂರೈಕೆ ಲಭ್ಯವಾಗುತ್ತದೆ.",
                "category": "Infrastructure"
            },
            {
                "title_en": "Solar Street Lights Installation Begins",
                "title_kn": "ಸೌರ ಬೀದಿ ದೀಪಗಳ ಅಳವಡಿಕೆ ಆರಂಭ",
                "content_en": "Installation of 500 solar-powered street lights has begun across all wards to improve safety and reduce electricity costs.",
                "content_kn": "ಸುರಕ್ಷತೆ ಸುಧಾರಿಸಲು ಮತ್ತು ವಿದ್ಯುತ್ ವೆಚ್ಚ ಕಡಿಮೆ ಮಾಡಲು ಎಲ್ಲಾ ವಾರ್ಡ್‌ಗಳಲ್ಲಿ 500 ಸೌರ ಶಕ್ತಿಯ ಬೀದಿ ದೀಪಗಳ ಅಳವಡಿಕೆ ಪ್ರಾರಂಭವಾಗಿದೆ.",
                "category": "Infrastructure"
            },
            {
                "title_en": "Employment Fair to be Organized Next Month",
                "title_kn": "ಮುಂದಿನ ತಿಂಗಳು ಉದ್ಯೋಗ ಮೇಳ ಆಯೋಜನೆ",
                "content_en": "A mega employment fair will be organized on 15th December with over 50 companies participating, offering 2000+ job opportunities.",
                "content_kn": "50 ಕ್ಕೂ ಹೆಚ್ಚು ಕಂಪನಿಗಳು ಭಾಗವಹಿಸುವ ಮೆಗಾ ಉದ್ಯೋಗ ಮೇಳವನ್ನು ಡಿಸೆಂಬರ್ 15 ರಂದು ಆಯೋಜಿಸಲಾಗುತ್ತದೆ.",
                "category": "Employment"
            },
            {
                "title_en": "Public Library Renovation Completed",
                "title_kn": "ಸಾರ್ವಜನಿಕ ಗ್ರಂಥಾಲಯ ನವೀಕರಣ ಪೂರ್ಣಗೊಂಡಿದೆ",
                "content_en": "The constituency public library has been renovated with modern facilities, digital library, and reading rooms.",
                "content_kn": "ಕ್ಷೇತ್ರದ ಸಾರ್ವಜನಿಕ ಗ್ರಂಥಾಲಯವನ್ನು ಆಧುನಿಕ ಸೌಕರ್ಯಗಳೊಂದಿಗೆ ನವೀಕರಿಸಲಾಗಿದೆ.",
                "category": "Education"
            },
            {
                "title_en": "Free Skill Development Training Program",
                "title_kn": "ಉಚಿತ ಕೌಶಲ್ಯ ಅಭಿವೃದ್ಧಿ ತರಬೇತಿ ಕಾರ್ಯಕ್ರಮ",
                "content_en": "Free skill development training in various trades will be provided to 1000 youth. Registration starts from next week.",
                "content_kn": "1000 ಯುವಕರಿಗೆ ವಿವಿಧ ವ್ಯಾಪಾರಗಳಲ್ಲಿ ಉಚಿತ ಕೌಶಲ್ಯ ಅಭಿವೃದ್ಧಿ ತರಬೇತಿ ನೀಡಲಾಗುವುದು.",
                "category": "Employment"
            }
        ]
        
        for i, data in enumerate(news_data):
            for constituency in constituencies:
                news = News(
                    id=uuid.uuid4(),
                    constituency_id=constituency.id,
                    title_en=data["title_en"],
                    title_kn=data["title_kn"],
                    content_en=data["content_en"],
                    content_kn=data["content_kn"],
                    category=data["category"],
                    is_published=True,
                    published_at=random_date(30),
                    views_count=random.randint(50, 500),
                    created_by=random.choice([m for m in mla_users if m.constituency_id == constituency.id]).id if mla_users else None
                )
                db.add(news)
                news_articles.append(news)
        
        db.flush()
        print(f"✅ Created {len(news_articles)} news articles")
        
        # ========================================
        # 5. CREATE MLA SCHEDULES
        # ========================================
        print("\n📅 Creating MLA schedules...")
        
        schedule_types = ["public_meeting", "office_hours", "field_visit", "grievance_day"]
        schedules = []
        
        for mla in mla_users:
            for i in range(10):  # 10 events per MLA
                start_date = datetime.utcnow() + timedelta(days=random.randint(-10, 30))
                
                schedule = MLASchedule(
                    id=uuid.uuid4(),
                    constituency_id=mla.constituency_id,
                    title_en=f"MLA {random.choice(['Public Meeting', 'Office Hours', 'Field Visit', 'Grievance Day'])}",
                    title_kn=f"ಶಾಸಕರ {random.choice(['ಸಾರ್ವಜನಿಕ ಸಭೆ', 'ಕಚೇರಿ ಸಮಯ', 'ಕ್ಷೇತ್ರ ಭೇಟಿ', 'ದೂರು ದಿನ'])}",
                    description_en=f"Join us for an important community meeting at ward office.",
                    description_kn=f"ವಾರ್ಡ್ ಕಚೇರಿಯಲ್ಲಿ ಪ್ರಮುಖ ಸಮುದಾಯ ಸಭೆಗೆ ಸೇರಿ.",
                    event_type=random.choice(schedule_types),
                    start_time=start_date,
                    end_time=start_date + timedelta(hours=2),
                    location=f"Ward Office, {random.choice([w for w in wards if w.constituency_id == mla.constituency_id]).name}",
                    is_public=True,
                    max_participants=random.choice([50, 100, 200, None])
                )
                db.add(schedule)
                schedules.append(schedule)
        
        db.flush()
        print(f"✅ Created {len(schedules)} MLA schedule events")
        
        # ========================================
        # 6. CREATE TICKER ITEMS
        # ========================================
        print("\n📢 Creating news ticker items...")
        
        ticker_messages = [
            ("Water supply will be interrupted from 10 AM to 2 PM on Sunday for maintenance work in Ward 1-5",
             "ವಾರ್ಡ್ 1-5 ರಲ್ಲಿ ನಿರ್ವಹಣಾ ಕಾಮಗಾರಿಗಾಗಿ ಭಾನುವಾರ ಬೆಳಿಗ್ಗೆ 10 ರಿಂದ 2 ರವರೆಗೆ ನೀರು ಪೂರೈಕೆ ಸ್ಥಗಿತಗೊಳ್ಳುತ್ತದೆ"),
            ("Vaccination camp for children on 10th Nov at Primary Health Center. Time: 9 AM to 4 PM",
             "ನವೆಂಬರ್ 10 ರಂದು ಪ್ರಾಥಮಿಕ ಆರೋಗ್ಯ ಕೇಂದ್ರದಲ್ಲಿ ಮಕ್ಕಳಿಗೆ ಲಸಿಕೆ ಶಿಬಿರ. ಸಮಯ: 9 AM ರಿಂದ 4 PM"),
            ("Road repair work on Main Street from 12th to 15th Nov. Please use alternate routes",
             "ನವೆಂಬರ್ 12 ರಿಂದ 15 ರವರೆಗೆ ಮುಖ್ಯ ರಸ್ತೆಯಲ್ಲಿ ರಸ್ತೆ ದುರಸ್ತಿ ಕಾಮಗಾರಿ. ದಯವಿಟ್ಟು ಪರ್ಯಾಯ ಮಾರ್ಗಗಳನ್ನು ಬಳಸಿ"),
            ("Free health checkup camp for senior citizens on 8th Nov at Community Hall",
             "ನವೆಂಬರ್ 8 ರಂದು ಸಮುದಾಯ ಭವನದಲ್ಲಿ ಹಿರಿಯ ನಾಗರಿಕರಿಗೆ ಉಚಿತ ಆರೋಗ್ಯ ತಪಾಸಣೆ ಶಿಬಿರ"),
            ("Property tax payment deadline extended till 30th November. Pay online to avoid penalty",
             "ಆಸ್ತಿ ತೆರಿಗೆ ಪಾವತಿ ಗಡುವು ನವೆಂಬರ್ 30 ರವರೆಗೆ ವಿಸ್ತರಿಸಲಾಗಿದೆ"),
        ]
        
        tickers = []
        for constituency in constituencies:
            for msg_en, msg_kn in ticker_messages:
                ticker = TickerItem(
                    id=uuid.uuid4(),
                    constituency_id=constituency.id,
                    message_en=msg_en,
                    message_kn=msg_kn,
                    priority=random.choice(["low", "medium", "high"]),
                    is_active=True,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=random.randint(7, 30))
                )
                db.add(ticker)
                tickers.append(ticker)
        
        db.flush()
        print(f"✅ Created {len(tickers)} ticker items")
        
        # ========================================
        # 7. CREATE POLLS
        # ========================================
        print("\n📊 Creating polls...")
        
        poll_data = [
            {
                "question": "What should be our top priority for development?",
                "options": [
                    "Better Roads and Infrastructure",
                    "24x7 Water Supply",
                    "Healthcare Facilities",
                    "Education and Schools",
                ]
            },
            {
                "question": "How satisfied are you with garbage collection services?",
                "options": [
                    "Very Satisfied",
                    "Satisfied",
                    "Neutral",
                    "Needs Improvement",
                ]
            },
            {
                "question": "Which time is convenient for MLA office hours?",
                "options": [
                    "Morning (9 AM - 12 PM)",
                    "Afternoon (2 PM - 5 PM)",
                    "Evening (5 PM - 8 PM)",
                    "Weekend Only",
                ]
            }
        ]
        
        polls = []
        for constituency in constituencies:
            for data in poll_data:
                mla = [m for m in mla_users if m.constituency_id == constituency.id][0] if mla_users else None
                
                poll = Poll(
                    id=uuid.uuid4(),
                    constituency_id=constituency.id,
                    title=data["question"],
                    description="Poll to gather citizen feedback and preferences",
                    is_active=True,
                    start_date=random_date(20),
                    end_date=datetime.utcnow() + timedelta(days=30),
                    created_by=mla.id if mla else citizens[0].id
                )
                db.add(poll)
                db.flush()
                
                # Add poll options
                for opt_text in data["options"]:
                    option = PollOption(
                        id=uuid.uuid4(),
                        poll_id=poll.id,
                        option_text=opt_text,
                        vote_count=0
                    )
                    db.add(option)
                    db.flush()
                    
                    # Add random votes
                    num_votes = random.randint(20, 100)
                    eligible_citizens = [c for c in citizens if c.constituency_id == constituency.id]
                    voters = random.sample(eligible_citizens, min(num_votes, len(eligible_citizens)))
                    
                    for voter in voters:
                        vote = Vote(
                            id=uuid.uuid4(),
                            poll_id=poll.id,
                            option_id=option.id,
                            user_id=voter.id
                        )
                        db.add(vote)
                
                polls.append(poll)
        
        db.flush()
        print(f"✅ Created {len(polls)} polls with options and votes")
        
        # ========================================
        # 8. CREATE CITIZEN FEEDBACK
        # ========================================
        print("\n💬 Creating citizen feedback...")
        
        feedback_categories = ["General", "Development", "Service", "Suggestion", "Appreciation"]
        feedback_subjects = [
            "Great work on road repairs",
            "Need more street lights in our area",
            "Water supply has improved significantly",
            "Garbage collection needs attention",
            "Appreciation for quick complaint resolution",
            "Suggestion for mobile health clinic",
            "Request for children's park",
            "Traffic management needed at junction"
        ]
        
        feedbacks = []
        for i in range(50):
            citizen = random.choice(citizens)
            
            feedback = CitizenFeedback(
                id=uuid.uuid4(),
                user_id=citizen.id,
                constituency_id=citizen.constituency_id,
                ward_id=citizen.ward_id,
                category=random.choice(feedback_categories),
                subject=random.choice(feedback_subjects),
                message=f"Detailed feedback message about the subject. This is an important input from citizen perspective.",
                sentiment=random.choice(["positive", "neutral", "negative"]),
                is_public=random.choice([True, False]),
                status=random.choice(["new", "reviewed", "responded"]),
                created_at=random_date(45)
            )
            db.add(feedback)
            feedbacks.append(feedback)
        
        db.flush()
        print(f"✅ Created {len(feedbacks)} citizen feedback entries")
        
        # ========================================
        # 9. CREATE VIDEO CONFERENCES
        # ========================================
        print("\n🎥 Creating video conference sessions...")
        
        conferences = []
        for constituency in constituencies:
            for i in range(3):
                conf = VideoConference(
                    id=uuid.uuid4(),
                    constituency_id=constituency.id,
                    title_en=f"Monthly Review Meeting - {['January', 'February', 'March'][i]} 2025",
                    title_kn=f"ಮಾಸಿಕ ಪರಿಶೀಲನಾ ಸಭೆ - {['ಜನವರಿ', 'ಫೆಬ್ರವರಿ', 'ಮಾರ್ಚ್'][i]} 2025",
                    description_en="Monthly constituency review meeting to discuss ongoing projects and citizen issues.",
                    description_kn="ನಡೆಯುತ್ತಿರುವ ಯೋಜನೆಗಳು ಮತ್ತು ನಾಗರಿಕ ಸಮಸ್ಯೆಗಳನ್ನು ಚರ್ಚಿಸಲು ಮಾಸಿಕ ಕ್ಷೇತ್ರ ಪರಿಶೀಲನಾ ಸಭೆ.",
                    scheduled_at=datetime.utcnow() + timedelta(days=random.randint(-30, 30)),
                    duration_minutes=60,
                    meeting_link=f"https://meet.example.com/{uuid.uuid4().hex[:10]}",
                    max_participants=100,
                    status=random.choice(["scheduled", "in_progress", "completed"]),
                    created_by=random.choice([m for m in mla_users if m.constituency_id == constituency.id]).id if mla_users else None
                )
                db.add(conf)
                conferences.append(conf)
        
        db.flush()
        print(f"✅ Created {len(conferences)} video conference sessions")
        
        # Commit all changes
        db.commit()
        
        # ========================================
        # FINAL SUMMARY
        # ========================================
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE DEMO DATA CREATED SUCCESSFULLY!")
        print("="*80)
        print("\n📊 SUMMARY:")
        print(f"   ✅ {len(citizens)} Citizen Users")
        print(f"   ✅ {len(dept_users)} Department Users")
        print(f"   ✅ {len(complaints)} Complaints (across all categories)")
        print(f"   ✅ {len(news_articles)} News Articles")
        print(f"   ✅ {len(schedules)} MLA Schedule Events")
        print(f"   ✅ {len(tickers)} News Ticker Items")
        print(f"   ✅ {len(polls)} Polls with Options and Votes")
        print(f"   ✅ {len(feedbacks)} Citizen Feedback Entries")
        print(f"   ✅ {len(conferences)} Video Conference Sessions")
        print("\n" + "="*80)
        print("\n📈 STATISTICS:")
        
        # Calculate statistics
        status_counts = {}
        for complaint in complaints:
            status_counts[complaint.status] = status_counts.get(complaint.status, 0) + 1
        
        print("\n   Complaint Status Distribution:")
        for status, count in status_counts.items():
            print(f"      • {status.title()}: {count}")
        
        category_counts = {}
        for complaint in complaints:
            category_counts[complaint.category] = category_counts.get(complaint.category, 0) + 1
        
        print("\n   Top Complaint Categories:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      • {category}: {count}")
        
        print("\n" + "="*80)
        print("\n🎯 DEMO SCENARIOS YOU CAN SHOW:")
        print("\n   1. Citizen Portal:")
        print("      - Login as any citizen (phone: +9198XXXXXXXX)")
        print("      - View and file complaints")
        print("      - Participate in polls")
        print("      - Submit feedback")
        print("      - View news and MLA schedule")
        
        print("\n   2. MLA Dashboard:")
        print("      - Login as MLA (Puttur: +918242226666)")
        print("      - View complaint statistics and trends")
        print("      - Review citizen feedback")
        print("      - Manage news and announcements")
        print("      - Schedule public meetings")
        
        print("\n   3. Department Portal:")
        print("      - Login as department user")
        print("      - View assigned complaints")
        print("      - Update complaint status")
        print("      - Track resolution metrics")
        
        print("\n   4. Analytics & Reports:")
        print("      - Constituency-wise complaint analysis")
        print("      - Category-wise trends")
        print("      - Response time metrics")
        print("      - Citizen satisfaction polls")
        
        print("\n" + "="*80)
        print("\n🚀 NEXT STEPS:")
        print("   1. Access API docs: http://localhost:8000/docs")
        print("   2. Login to frontend: http://localhost:3000")
        print("   3. Test OTP with any user phone number")
        print("   4. Explore all features with rich demo data")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error creating demo data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
