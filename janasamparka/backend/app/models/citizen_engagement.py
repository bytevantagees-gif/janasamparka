"""
Citizen Engagement Models - Feedback, Ideas, Video Conferencing, and Scheduled Messages
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from app.core.database import Base


class FeedbackType(str, Enum):
    """Feedback and engagement types"""
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    IDEA = "idea"
    APPRECIATION = "appreciation"
    QUERY = "query"
    GRIEVANCE = "grievance"
    REQUEST = "request"


class FeedbackStatus(str, Enum):
    """Feedback processing status"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CLOSED = "closed"


class FeedbackPriority(str, Enum):
    """Feedback priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CitizenFeedback(Base):
    """Citizen feedback, complaints, and ideas model"""
    __tablename__ = "citizen_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Classification
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False, index=True)
    status = Column(SQLEnum(FeedbackStatus), default=FeedbackStatus.PENDING, index=True)
    priority = Column(SQLEnum(FeedbackPriority), default=FeedbackPriority.MEDIUM, index=True)
    
    # Relationships
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)  # Staff/MLA assigned
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True, index=True)
    
    # Categorization
    category = Column(String(100), index=True)  # Infrastructure, Health, Education, etc.
    subcategory = Column(String(100), index=True)
    tags = Column(Text)  # JSON array of tags
    
    # Location information
    location_address = Column(Text)
    latitude = Column(String(50))
    longitude = Column(String(50))
    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id"), nullable=True, index=True)
    
    # Media attachments
    attachment_urls = Column(Text)  # JSON array of file URLs
    video_url = Column(String(500))  # Video explanation
    
    # Voting and engagement
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    vote_count = Column(Integer, default=0)  # Cached total votes
    
    # Visibility
    is_public = Column(Boolean, default=False, index=True)  # Public visibility
    is_anonymous = Column(Boolean, default=False)  # Anonymous submission
    
    # Response tracking
    response_required = Column(Boolean, default=True)
    response_deadline = Column(DateTime)
    last_response_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Additional metadata
    source = Column(String(50), default="web")  # web, mobile, email, phone
    reference_number = Column(String(50), unique=True, index=True)  # Auto-generated
    
    # Relationships
    citizen = relationship("User", foreign_keys=[citizen_id], back_populates="feedback_submissions")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_feedback")
    constituency = relationship("Constituency")
    department = relationship("Department")
    ward = relationship("Ward")
    responses = relationship("FeedbackResponse", back_populates="feedback", cascade="all, delete-orphan")
    votes = relationship("FeedbackVote", back_populates="feedback", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CitizenFeedback(id={self.id}, type={self.feedback_type}, status={self.status})>"

    def to_dict(self):
        """Convert to dictionary with additional fields"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "feedback_type": self.feedback_type.value if self.feedback_type else None,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "citizen_id": self.citizen_id,
            "constituency_id": self.constituency_id,
            "assigned_to": self.assigned_to,
            "department_id": self.department_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "tags": self.tags.split(',') if self.tags else [],
            "location_address": self.location_address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "ward_id": self.ward_id,
            "attachment_urls": self.attachment_urls.split(',') if self.attachment_urls else [],
            "video_url": self.video_url,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "vote_count": self.vote_count,
            "is_public": self.is_public,
            "is_anonymous": self.is_anonymous,
            "response_required": self.response_required,
            "response_deadline": self.response_deadline.isoformat() if self.response_deadline else None,
            "last_response_at": self.last_response_at.isoformat() if self.last_response_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "source": self.source,
            "reference_number": self.reference_number
        }


class FeedbackResponse(Base):
    """Responses to citizen feedback"""
    __tablename__ = "feedback_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("citizen_feedback.id"), nullable=False, index=True)
    
    # Response content
    content = Column(Text, nullable=False)
    response_type = Column(String(50), default="official")  # official, mla, department, system
    
    # Author information
    responder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    responder_name = Column(String(200))  # Cached name for anonymous feedback
    responder_role = Column(String(50))
    
    # Media attachments
    attachment_urls = Column(Text)  # JSON array of file URLs
    video_url = Column(String(500))
    
    # Visibility
    is_public = Column(Boolean, default=True)
    is_internal_note = Column(Boolean, default=False)
    
    # Status changes
    status_change = Column(String(50))  # New status if this response changes status
    old_status = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedback = relationship("CitizenFeedback", back_populates="responses")
    responder = relationship("User")

    def __repr__(self):
        return f"<FeedbackResponse(id={self.id}, feedback_id={self.feedback_id})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "feedback_id": self.feedback_id,
            "content": self.content,
            "response_type": self.response_type,
            "responder_id": self.responder_id,
            "responder_name": self.responder_name,
            "responder_role": self.responder_role,
            "attachment_urls": self.attachment_urls.split(',') if self.attachment_urls else [],
            "video_url": self.video_url,
            "is_public": self.is_public,
            "is_internal_note": self.is_internal_note,
            "status_change": self.status_change,
            "old_status": self.old_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class FeedbackVote(Base):
    """Votes on citizen feedback (for ideas and suggestions)"""
    __tablename__ = "feedback_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("citizen_feedback.id"), nullable=False, index=True)
    voter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    vote_type = Column(String(10), nullable=False)  # up, down
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    feedback = relationship("CitizenFeedback", back_populates="votes")
    voter = relationship("User")

    def __repr__(self):
        return f"<FeedbackVote(id={self.id}, feedback_id={self.feedback_id}, vote_type={self.vote_type})>"


class VideoConferenceType(str, Enum):
    """Video conference types"""
    ONE_ON_ONE = "one_on_one"
    GROUP_MEETING = "group_meeting"
    PUBLIC_HEARING = "public_hearing"
    PRESS_CONFERENCE = "press_conference"
    TOWN_HALL = "town_hall"
    OFFICE_HOURS = "office_hours"


class VideoConferenceStatus(str, Enum):
    """Video conference status"""
    SCHEDULED = "scheduled"
    STARTED = "started"
    ENDED = "ended"
    CANCELLED = "cancelled"


class VideoConference(Base):
    """Video conference sessions model"""
    __tablename__ = "video_conferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    
    # Conference details
    conference_type = Column(SQLEnum(VideoConferenceType), nullable=False, index=True)
    status = Column(SQLEnum(VideoConferenceStatus), default=VideoConferenceStatus.SCHEDULED, index=True)
    
    # Relationships
    host_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)  # MLA or authorized staff
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Timing
    scheduled_start = Column(DateTime, nullable=False, index=True)
    scheduled_end = Column(DateTime, nullable=False, index=True)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    
    # Conference settings
    max_participants = Column(Integer, default=100)
    is_public = Column(Boolean, default=False, index=True)
    requires_registration = Column(Boolean, default=True)
    is_recorded = Column(Boolean, default=False)
    
    # Platform integration
    platform = Column(String(50), default="zoom")  # zoom, google_meet, teams, custom
    meeting_id = Column(String(100), unique=True, index=True)  # Platform meeting ID
    meeting_url = Column(String(500))  # Join URL
    meeting_password = Column(String(50))  # Meeting password
    host_url = Column(String(500))  # Host start URL
    
    # Location (for hybrid meetings)
    venue = Column(String(500))
    address = Column(Text)
    latitude = Column(String(50))
    longitude = Column(String(50))
    
    # Participants
    registered_participants = Column(Integer, default=0)
    actual_participants = Column(Integer, default=0)
    
    # Recording and resources
    recording_url = Column(String(500))
    transcript_url = Column(String(500))
    attachment_urls = Column(Text)  # JSON array of presentation files
    
    # Access control
    allowed_roles = Column(Text)  # JSON array of roles that can join
    invite_only = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    host = relationship("User", back_populates="hosted_conferences")
    constituency = relationship("Constituency")
    participants = relationship("ConferenceParticipant", back_populates="conference", cascade="all, delete-orphan")
    chat_messages = relationship("ConferenceChatMessage", back_populates="conference", cascade="all, delete-orphan", order_by="ConferenceChatMessage.sent_at")

    def __repr__(self):
        return f"<VideoConference(id={self.id}, title='{self.title[:50]}...', type={self.conference_type})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "conference_type": self.conference_type.value if self.conference_type else None,
            "status": self.status.value if self.status else None,
            "host_id": self.host_id,
            "constituency_id": self.constituency_id,
            "scheduled_start": self.scheduled_start.isoformat() if self.scheduled_start else None,
            "scheduled_end": self.scheduled_end.isoformat() if self.scheduled_end else None,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
            "max_participants": self.max_participants,
            "is_public": self.is_public,
            "requires_registration": self.requires_registration,
            "is_recorded": self.is_recorded,
            "platform": self.platform,
            "meeting_id": self.meeting_id,
            "meeting_url": self.meeting_url,
            "venue": self.venue,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "registered_participants": self.registered_participants,
            "actual_participants": self.actual_participants,
            "recording_url": self.recording_url,
            "transcript_url": self.transcript_url,
            "attachment_urls": self.attachment_urls.split(',') if self.attachment_urls else [],
            "allowed_roles": self.allowed_roles.split(',') if self.allowed_roles else [],
            "invite_only": self.invite_only,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ConferenceParticipant(Base):
    """Video conference participants"""
    __tablename__ = "conference_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conference_id = Column(UUID(as_uuid=True), ForeignKey("video_conferences.id"), nullable=False, index=True)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Registration details
    registered_at = Column(DateTime, default=datetime.utcnow)
    joined_at = Column(DateTime)
    left_at = Column(DateTime)
    
    # Participant role
    role = Column(String(50), default="participant")  # host, co_host, participant, panelist
    
    # Status
    status = Column(String(50), default="registered")  # registered, joined, left, no_show
    
    # Contact information
    email = Column(String(200))
    phone = Column(String(20))
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    conference = relationship("VideoConference", back_populates="participants")
    participant = relationship("User")

    def __repr__(self):
        return f"<ConferenceParticipant(id={self.id}, conference_id={self.conference_id}, participant_id={self.participant_id})>"


class ConferenceChatMessage(Base):
    """Live chat messages during video conferences"""
    __tablename__ = "conference_chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conference_id = Column(UUID(as_uuid=True), ForeignKey("video_conferences.id"), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Message content
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, question, poll, announcement
    
    # Metadata
    sender_name = Column(String(200))
    sender_role = Column(String(50))  # host, participant, moderator
    
    # Moderation - All messages need approval before showing publicly
    is_approved = Column(Boolean, default=False, index=True)  # Moderator approved
    is_rejected = Column(Boolean, default=False)
    moderated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime)
    rejection_reason = Column(String(500))
    
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_question = Column(Boolean, default=False)  # Marked as Q&A question
    is_answered = Column(Boolean, default=False)
    
    # Reactions
    likes_count = Column(Integer, default=0)
    
    # Reply tracking
    reply_to_id = Column(UUID(as_uuid=True), ForeignKey("conference_chat_messages.id"), nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    edited_at = Column(DateTime)
    deleted_at = Column(DateTime)
    
    # Relationships
    conference = relationship("VideoConference", back_populates="chat_messages")
    sender = relationship("User", foreign_keys=[sender_id])
    moderator = relationship("User", foreign_keys=[moderated_by])
    replies = relationship("ConferenceChatMessage", backref="parent_message", remote_side=[id])
    
    def __repr__(self):
        return f"<ConferenceChatMessage(id={self.id}, conference_id={self.conference_id}, sender={self.sender_name})>"


class BroadcastType(str, Enum):
    """Message broadcast types"""
    ANNOUNCEMENT = "announcement"
    EMERGENCY = "emergency"
    UPDATE = "update"
    INVITATION = "invitation"
    REMINDER = "reminder"
    CELEBRATION = "celebration"
    INFORMATION = "information"


class BroadcastStatus(str, Enum):
    """Broadcast status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledBroadcast(Base):
    """Scheduled message broadcasts by MLAs"""
    __tablename__ = "scheduled_broadcasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Broadcast details
    broadcast_type = Column(SQLEnum(BroadcastType), nullable=False, index=True)
    status = Column(SQLEnum(BroadcastStatus), default=BroadcastStatus.DRAFT, index=True)
    
    # Relationships
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)  # MLA
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=False, index=True)
    sent_at = Column(DateTime)
    
    # Targeting
    target_roles = Column(Text)  # JSON array of roles to target
    target_wards = Column(Text)  # JSON array of ward IDs
    target_departments = Column(Text)  # JSON array of department IDs
    target_all = Column(Boolean, default=True)  # Send to all constituents
    
    # Delivery channels
    send_push = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    send_email = Column(Boolean, default=False)
    send_whatsapp = Column(Boolean, default=False)
    show_in_app = Column(Boolean, default=True)
    
    # Content
    attachment_urls = Column(Text)  # JSON array of file URLs
    video_url = Column(String(500))
    link_url = Column(String(500))
    link_text = Column(String(200))
    
    # Personalization
    personalization_data = Column(Text)  # JSON object with personalization variables
    
    # Analytics
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    
    # Priority and expiration
    priority = Column(Integer, default=1)  # 1-10, higher = more important
    expires_at = Column(DateTime)  # When to stop showing in app
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="broadcasts")
    constituency = relationship("Constituency")
    approver = relationship("User", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<ScheduledBroadcast(id={self.id}, title='{self.title[:50]}...', scheduled_at={self.scheduled_at})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "broadcast_type": self.broadcast_type.value if self.broadcast_type else None,
            "status": self.status.value if self.status else None,
            "sender_id": self.sender_id,
            "constituency_id": self.constituency_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "target_roles": self.target_roles.split(',') if self.target_roles else [],
            "target_wards": self.target_wards.split(',') if self.target_wards else [],
            "target_departments": self.target_departments.split(',') if self.target_departments else [],
            "target_all": self.target_all,
            "send_push": self.send_push,
            "send_sms": self.send_sms,
            "send_email": self.send_email,
            "send_whatsapp": self.send_whatsapp,
            "show_in_app": self.show_in_app,
            "attachment_urls": self.attachment_urls.split(',') if self.attachment_urls else [],
            "video_url": self.video_url,
            "link_url": self.link_url,
            "link_text": self.link_text,
            "sent_count": self.sent_count,
            "delivered_count": self.delivered_count,
            "read_count": self.read_count,
            "click_count": self.click_count,
            "priority": self.priority,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class BroadcastDelivery(Base):
    """Track delivery status of broadcasts to individual users"""
    __tablename__ = "broadcast_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    broadcast_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_broadcasts.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Delivery status per channel
    push_sent = Column(Boolean, default=False)
    push_delivered = Column(Boolean, default=False)
    push_read = Column(Boolean, default=False)
    
    sms_sent = Column(Boolean, default=False)
    sms_delivered = Column(Boolean, default=False)
    
    email_sent = Column(Boolean, default=False)
    email_delivered = Column(Boolean, default=False)
    email_read = Column(Boolean, default=False)
    
    whatsapp_sent = Column(Boolean, default=False)
    whatsapp_delivered = Column(Boolean, default=False)
    whatsapp_read = Column(Boolean, default=False)
    
    # App display
    shown_in_app = Column(Boolean, default=False)
    clicked_in_app = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    broadcast = relationship("ScheduledBroadcast")
    user = relationship("User")

    def __repr__(self):
        return f"<BroadcastDelivery(id={self.id}, broadcast_id={self.broadcast_id}, user_id={self.user_id})>"
