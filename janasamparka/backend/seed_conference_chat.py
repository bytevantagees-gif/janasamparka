#!/usr/bin/env python3
"""
Seed script for Conference Chat Messages
- Demonstrates moderation workflow
- Includes approved, pending, and rejected messages
"""

from datetime import datetime, timedelta
import uuid
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.citizen_engagement import VideoConference, ConferenceChatMessage

def seed_chat_messages():
    """Seed sample chat messages for video conferences"""
    print("💬 Seeding conference chat messages...")
    
    db = SessionLocal()
    try:
        # Get a conference
        conference = db.execute(select(VideoConference).where(
            VideoConference.status == 'SCHEDULED'
        ).limit(1)).scalar_one_or_none()
        
        if not conference:
            print("❌ No scheduled conference found. Please seed conferences first.")
            return
        
        print(f"   Using conference: {conference.title}")
        
        # Get users
        moderator = db.execute(select(User).where(User.role.in_(['admin', 'mla', 'moderator'])).limit(1)).scalar_one_or_none()
        citizens = db.execute(select(User).where(User.role == 'citizen').limit(5)).scalars().all()
        
        if not moderator or not citizens:
            print("❌ Need moderator and citizens. Please seed users first.")
            return
        
        now = datetime.utcnow()
        
        # Sample chat messages with different statuses
        chat_samples = [
            # APPROVED MESSAGES (visible to all)
            {
                "sender": citizens[0],
                "message": "Great initiative! When will the road work start?",
                "is_approved": True,
                "moderated_by": moderator.id,
                "moderated_at": now - timedelta(minutes=10),
                "sent_at": now - timedelta(minutes=15),
                "likes_count": 5
            },
            {
                "sender": citizens[1],
                "message": "Thank you for addressing water supply issues",
                "is_approved": True,
                "moderated_by": moderator.id,
                "moderated_at": now - timedelta(minutes=8),
                "sent_at": now - timedelta(minutes=12),
                "likes_count": 3
            },
            {
                "sender": citizens[2],
                "message": "Can we get more street lights in Ward 5?",
                "is_question": True,
                "is_approved": True,
                "is_answered": True,
                "moderated_by": moderator.id,
                "moderated_at": now - timedelta(minutes=5),
                "sent_at": now - timedelta(minutes=10),
                "likes_count": 8
            },
            {
                "sender": moderator,
                "message": "Welcome everyone! Please use the Q&A feature for questions.",
                "is_approved": True,  # Moderator messages auto-approved
                "is_pinned": True,
                "sent_at": now - timedelta(minutes=20),
                "moderated_by": moderator.id,
                "moderated_at": now - timedelta(minutes=20)
            },
            
            # PENDING MESSAGES (waiting for approval)
            {
                "sender": citizens[3],
                "message": "What about the drainage system improvement?",
                "is_approved": False,
                "is_rejected": False,
                "sent_at": now - timedelta(minutes=2)
            },
            {
                "sender": citizens[4],
                "message": "Can you provide update on school infrastructure?",
                "is_question": True,
                "is_approved": False,
                "is_rejected": False,
                "sent_at": now - timedelta(minutes=1)
            },
            {
                "sender": citizens[0],
                "message": "How is the budget being allocated?",
                "is_approved": False,
                "is_rejected": False,
                "sent_at": now - timedelta(seconds=30)
            },
            
            # REJECTED MESSAGES (inappropriate content)
            {
                "sender": citizens[1],
                "message": "This is spam content",
                "is_approved": False,
                "is_rejected": True,
                "moderated_by": moderator.id,
                "moderated_at": now - timedelta(minutes=3),
                "rejection_reason": "Spam/irrelevant content",
                "sent_at": now - timedelta(minutes=5)
            }
        ]
        
        # Create chat messages
        for chat_data in chat_samples:
            sender = chat_data.pop("sender")
            message = ConferenceChatMessage(
                id=str(uuid.uuid4()),
                conference_id=conference.id,
                sender_id=sender.id,
                sender_name=sender.name,
                sender_role=sender.role,
                **chat_data
            )
            db.add(message)
        
        db.commit()
        
        print(f"✅ Created {len(chat_samples)} chat messages")
        print(f"   - {sum(1 for m in chat_samples if m.get('is_approved'))} approved (visible)")
        print(f"   - {sum(1 for m in chat_samples if not m.get('is_approved') and not m.get('is_rejected'))} pending moderation")
        print(f"   - {sum(1 for m in chat_samples if m.get('is_rejected'))} rejected")
        print(f"   - {sum(1 for m in chat_samples if m.get('is_question'))} questions")
        print(f"   - {sum(1 for m in chat_samples if m.get('is_pinned'))} pinned")
        
    finally:
        db.close()


def main():
    """Run all seed functions"""
    print("\n" + "="*60)
    print("🌱 SEEDING CONFERENCE CHAT DATA")
    print("="*60 + "\n")
    
    seed_chat_messages()
    
    print("\n" + "="*60)
    print("✅ CHAT SEEDING COMPLETE!")
    print("="*60 + "\n")
    print("You now have:")
    print("  💬 Live chat messages with moderation workflow")
    print("  ✅ Approved messages (visible to all)")
    print("  ⏳ Pending messages (waiting for moderator)")
    print("  ❌ Rejected messages (spam filtered)")
    print("  ❓ Q&A questions (marked and answered)")
    print("  📌 Pinned messages (important announcements)")
    print()

if __name__ == "__main__":
    main()
