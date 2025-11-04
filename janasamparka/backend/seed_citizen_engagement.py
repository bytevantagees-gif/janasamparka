#!/usr/bin/env python3
"""
Seed script for Citizen Engagement features
- Video Conferences (Virtual Office Hours, Town Halls)
- Citizen Feedback
- Scheduled Broadcasts
"""

from datetime import datetime, timedelta
import uuid
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.constituency import Constituency
from app.models.citizen_engagement import (
    VideoConference, VideoConferenceType, VideoConferenceStatus,
    ConferenceParticipant,
    ScheduledBroadcast, BroadcastType, BroadcastStatus
)

def seed_video_conferences():
    """Seed video conferences - office hours and town halls"""
    print("🎥 Seeding video conferences...")
    
    db = SessionLocal()
    try:
        # Get constituency and users
        constituency = db.execute(select(Constituency).limit(1)).scalar_one_or_none()
        
        if not constituency:
            print("❌ No constituency found. Please seed constituencies first.")
            return
            
        # Get MLA user (admin or mla role)
        mla = db.execute(select(User).where(User.role.in_(['admin', 'mla'])).limit(1)).scalar_one_or_none()
        
        if not mla:
            print("❌ No MLA user found.")
            return
        
        # Get some citizens
        citizens = db.execute(select(User).where(User.role == 'citizen').limit(10)).scalars().all()
        
        now = datetime.utcnow()
        
        # 1. Virtual Office Hours - Multiple slots
        office_hours_dates = [
            now + timedelta(days=2, hours=10),
            now + timedelta(days=4, hours=14),
            now + timedelta(days=6, hours=10)
        ]
        
        conferences = []
        for idx, start_time in enumerate(office_hours_dates):
            conference = VideoConference(
                id=uuid.uuid4(),
                title=f"Virtual Office Hours - {start_time.strftime('%b %d, %Y')}",
                description="Book a 10-minute slot to discuss your issues directly with the MLA",
                conference_type=VideoConferenceType.OFFICE_HOURS,
                status=VideoConferenceStatus.SCHEDULED,
                host_id=mla.id,
                constituency_id=constituency.id,
                scheduled_start=start_time,
                scheduled_end=start_time + timedelta(hours=2),
                max_participants=12,
                is_public=True,
                requires_registration=True,
                is_recorded=False,
                platform="Zoom",
                meeting_id=f"OFFICE-{start_time.strftime('%Y%m%d')}-{idx+1}",
                meeting_url=f"https://zoom.us/j/12345678{idx}",
                registered_participants=8 if idx == 0 else 12 if idx == 1 else 5
            )
            conferences.append(conference)
            db.add(conference)
        
        # 2. Upcoming Town Halls
        town_halls = [
            {
                "title": "Budget Discussion & Q&A",
                "description": "Join us for an interactive session on next quarter's budget allocation and development plans. Ask your questions live!",
                "date_offset": 9,
                "time": 18,  # 6 PM
                "duration": 90,
                "registered": 234
            },
            {
                "title": "Infrastructure Development Update",
                "description": "Updates on ongoing infrastructure projects including roads, water supply, and community centers.",
                "date_offset": 14,
                "time": 17,  # 5 PM
                "duration": 60,
                "registered": 156
            },
            {
                "title": "Healthcare Improvements Discussion",
                "description": "Discussing improvements to local healthcare facilities and new health initiatives.",
                "date_offset": 20,
                "time": 18,
                "duration": 75,
                "registered": 189
            }
        ]
        
        for hall in town_halls:
            start_time = now + timedelta(days=hall["date_offset"], hours=hall["time"])
            conference = VideoConference(
                id=uuid.uuid4(),
                title=hall["title"],
                description=hall["description"],
                conference_type=VideoConferenceType.TOWN_HALL,
                status=VideoConferenceStatus.SCHEDULED,
                host_id=mla.id,
                constituency_id=constituency.id,
                scheduled_start=start_time,
                scheduled_end=start_time + timedelta(minutes=hall["duration"]),
                max_participants=500,
                is_public=True,
                requires_registration=True,
                is_recorded=True,
                platform="YouTube Live",
                meeting_id=f"TOWNHALL-{start_time.strftime('%Y%m%d')}",
                meeting_url=f"https://youtube.com/live/{hall['title'].replace(' ', '-').lower()}",
                registered_participants=hall["registered"]
            )
            conferences.append(conference)
            db.add(conference)
        
        # 3. Past Town Hall with recording
        past_hall_time = now - timedelta(days=7, hours=-18)
        past_conference = VideoConference(
            id=uuid.uuid4(),
            title="Education Initiatives & Scholarship Programs",
            description="Discussion on new scholarship programs and improvements to local schools.",
            conference_type=VideoConferenceType.TOWN_HALL,
            status=VideoConferenceStatus.ENDED,
            host_id=mla.id,
            constituency_id=constituency.id,
            scheduled_start=past_hall_time,
            scheduled_end=past_hall_time + timedelta(minutes=75),
            actual_start=past_hall_time + timedelta(minutes=5),
            actual_end=past_hall_time + timedelta(minutes=80),
            max_participants=500,
            is_public=True,
            requires_registration=False,
            is_recorded=True,
            platform="YouTube Live",
            meeting_id="TOWNHALL-20241025",
            meeting_url="https://youtube.com/watch?v=education-2024",
            recording_url="https://youtube.com/watch?v=education-2024",
            registered_participants=187,
            actual_participants=164
        )
        conferences.append(past_conference)
        db.add(past_conference)
        
        db.commit()
        
        # Add participants to some conferences
        if citizens:
            for conf_idx, conference in enumerate(conferences[:2]):  # First 2 conferences
                for citizen in citizens[:5]:  # First 5 citizens
                    participant = ConferenceParticipant(
                        id=uuid.uuid4(),
                        conference_id=conference.id,
                        participant_id=citizen.id,
                        registered_at=now - timedelta(days=1),
                        role="participant",
                        status="registered",
                        email=citizen.email,
                        phone=citizen.phone
                    )
                    db.add(participant)
            
            db.commit()
        
        print(f"✅ Created {len(conferences)} video conferences")
        print(f"   - Virtual Office Hours: 3 sessions")
        print(f"   - Town Halls: {len(town_halls)} upcoming + 1 past")
        
    finally:
        db.close()

def seed_broadcasts():
    """Seed scheduled broadcasts/announcements"""
    print("📢 Seeding broadcasts...")
    
    db = SessionLocal()
    try:
        constituency = db.execute(select(Constituency).limit(1)).scalar_one_or_none()
        
        mla = db.execute(select(User).where(User.role.in_(['admin', 'mla'])).limit(1)).scalar_one_or_none()
        
        if not constituency or not mla:
            print("❌ Missing constituency or MLA")
            return
        
        now = datetime.utcnow()
        
        broadcasts = [
            {
                "title": "Emergency: Water Supply Disruption Alert",
                "message": "Due to maintenance work, water supply will be temporarily disrupted in Wards 5-7 tomorrow from 10 AM to 2 PM. Tanker service will be available.",
                "type": BroadcastType.EMERGENCY,
                "status": BroadcastStatus.SENT,
                "sent_at": now - timedelta(hours=6),
                "sent_count": 1247,
                "delivered_count": 1198
            },
            {
                "title": "Town Hall Meeting Reminder",
                "message": "Don't forget! Join our Budget Discussion Town Hall tomorrow at 6 PM. Register now: http://link.to/townhall",
                "type": BroadcastType.REMINDER,
                "status": BroadcastStatus.SCHEDULED,
                "scheduled_at": now + timedelta(days=1, hours=9),
                "link_url": "http://link.to/townhall",
                "link_text": "Register Now"
            },
            {
                "title": "New Street Lights Installed",
                "message": "Great news! 89 new street lights have been installed across 5 wards. Your safety is our priority.",
                "type": BroadcastType.UPDATE,
                "status": BroadcastStatus.SENT,
                "sent_at": now - timedelta(days=2),
                "sent_count": 2341,
                "delivered_count": 2287,
                "read_count": 1456
            },
            {
                "title": "Free Health Camp - Nov 15",
                "message": "Free health checkup camp on November 15 at Community Center. All citizens welcome. Timings: 10 AM - 4 PM",
                "type": BroadcastType.ANNOUNCEMENT,
                "status": BroadcastStatus.SCHEDULED,
                "scheduled_at": now + timedelta(days=5, hours=8)
            }
        ]
        
        for b in broadcasts:
            broadcast = ScheduledBroadcast(
                id=uuid.uuid4(),
                title=b["title"],
                message=b["message"],
                broadcast_type=b["type"],
                status=b["status"],
                sender_id=mla.id,
                constituency_id=constituency.id,
                scheduled_at=b.get("scheduled_at", now),
                sent_at=b.get("sent_at"),
                target_all=True,
                send_push=True,
                send_sms=True,
                send_email=False,
                show_in_app=True,
                link_url=b.get("link_url"),
                link_text=b.get("link_text"),
                priority=5 if b["type"] == BroadcastType.EMERGENCY else 3,
                sent_count=b.get("sent_count", 0),
                delivered_count=b.get("delivered_count", 0),
                read_count=b.get("read_count", 0)
            )
            db.add(broadcast)
        
        db.commit()
        print(f"✅ Created {len(broadcasts)} broadcasts")
    finally:
        db.close()

def main():
    """Run all seed functions"""
    print("\n" + "="*60)
    print("🌱 SEEDING CITIZEN ENGAGEMENT DATA")
    print("="*60 + "\n")
    
    seed_video_conferences()
    seed_broadcasts()
    
    print("\n" + "="*60)
    print("✅ CITIZEN ENGAGEMENT SEEDING COMPLETE!")
    print("="*60 + "\n")
    print("You now have:")
    print("  📹 3 Virtual Office Hours sessions")
    print("  🏛️ 3 Upcoming Town Halls + 1 Past Recording")
    print("  📢 4 Broadcasts (emergency, updates, reminders)")
    print()

if __name__ == "__main__":
    main()
