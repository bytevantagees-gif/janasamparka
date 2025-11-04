"""
News and MLA Schedule models for Janasamparka
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from enum import Enum
import uuid

from app.core.database import Base


class NewsCategory(str, Enum):
    """News categories"""
    LOCAL_DEVELOPMENT = "local_development"
    GOVERNMENT_INITIATIVE = "government_initiative"
    PUBLIC_SERVICE = "public_service"
    MEETING = "meeting"
    ACHIEVEMENT = "achievement"
    ANNOUNCEMENT = "announcement"
    EMERGENCY = "emergency"
    OTHER = "other"


class NewsPriority(str, Enum):
    """News priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class News(Base):
    """News and snippets model"""
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String(1000))  # Brief summary for ticker
    category = Column(SQLEnum(NewsCategory), nullable=False, index=True)
    priority = Column(SQLEnum(NewsPriority), default=NewsPriority.MEDIUM, index=True)
    
    # Relationships
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    mla_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Media attachments
    featured_image_url = Column(String(500))
    image_urls = Column(Text)  # JSON array of image URLs
    
    # Publishing control
    is_published = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False, index=True)  # For dashboard highlight
    show_in_ticker = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    expires_at = Column(DateTime)  # News expiration date
    
    # Metadata
    source = Column(String(200))  # News source
    author = Column(String(200))
    tags = Column(Text)  # JSON array of tags
    view_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False, index=True)

    # Relationships
    constituency = relationship("Constituency", back_populates="news")
    mla = relationship("User", foreign_keys=[mla_id], back_populates="news_posts")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title[:50]}...', constituency={self.constituency_id})>"

    def to_dict(self):
        """Convert to dictionary with additional fields"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "category": self.category.value if self.category else None,
            "priority": self.priority.value if self.priority else None,
            "constituency_id": self.constituency_id,
            "mla_id": self.mla_id,
            "featured_image_url": self.featured_image_url,
            "image_urls": self.image_urls.split(',') if self.image_urls else [],
            "is_published": self.is_published,
            "is_featured": self.is_featured,
            "show_in_ticker": self.show_in_ticker,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source": self.source,
            "author": self.author,
            "tags": self.tags.split(',') if self.tags else [],
            "view_count": self.view_count,
            "is_archived": self.is_archived
        }


class ScheduleType(str, Enum):
    """Schedule event types"""
    MEETING = "meeting"
    PUBLIC_EVENT = "public_event"
    OFFICE_HOURS = "office_hours"
    CAMP = "camp"
    INSPECTION = "inspection"
    PRESS_CONFERENCE = "press_conference"
    OTHER = "other"


class ScheduleStatus(str, Enum):
    """Schedule status"""
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    POSTPONED = "postponed"


class MLASchedule(Base):
    """MLA Schedule model"""
    __tablename__ = "mla_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    
    # Relationships
    mla_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Schedule details
    schedule_type = Column(SQLEnum(ScheduleType), nullable=False, index=True)
    status = Column(SQLEnum(ScheduleStatus), default=ScheduleStatus.SCHEDULED, index=True)
    
    # Location
    venue = Column(String(500))
    address = Column(Text)
    latitude = Column(String(50))
    longitude = Column(String(50))
    
    # Timing
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=False, index=True)
    is_all_day = Column(Boolean, default=False)
    
    # Visibility
    is_public = Column(Boolean, default=True, index=True)  # Public vs private schedule
    is_featured = Column(Boolean, default=False, index=True)  # Dashboard highlight
    
    # Participants
    expected_attendees = Column(Integer)  # Expected number of attendees
    max_attendees = Column(Integer)  # Maximum allowed attendees
    registration_required = Column(Boolean, default=False)
    
    # Contact information
    contact_person = Column(String(200))
    contact_phone = Column(String(20))
    contact_email = Column(String(200))
    
    # Additional information
    agenda = Column(Text)  # Meeting agenda or event details
    requirements = Column(Text)  # Special requirements or notes
    external_links = Column(Text)  # JSON array of related links
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Reminder settings
    reminder_sent = Column(Boolean, default=False)
    reminder_minutes_before = Column(Integer, default=60)  # Minutes before event to send reminder

    # Relationships
    mla = relationship("User", foreign_keys=[mla_id])
    constituency = relationship("Constituency")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<MLASchedule(id={self.id}, title='{self.title[:50]}...', mla={self.mla_id})>"

    def to_dict(self):
        """Convert to dictionary with additional fields"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "mla_id": self.mla_id,
            "constituency_id": self.constituency_id,
            "schedule_type": self.schedule_type.value if self.schedule_type else None,
            "status": self.status.value if self.status else None,
            "venue": self.venue,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "end_datetime": self.end_datetime.isoformat() if self.end_datetime else None,
            "is_all_day": self.is_all_day,
            "is_public": self.is_public,
            "is_featured": self.is_featured,
            "expected_attendees": self.expected_attendees,
            "max_attendees": self.max_attendees,
            "registration_required": self.registration_required,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "agenda": self.agenda,
            "requirements": self.requirements,
            "external_links": self.external_links.split(',') if self.external_links else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "reminder_sent": self.reminder_sent,
            "reminder_minutes_before": self.reminder_minutes_before
        }


class TickerItem(Base):
    """Ticker items for dashboard"""
    __tablename__ = "ticker_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(String(500), nullable=False)
    content_type = Column(String(50), default="text")  # text, link, announcement
    
    # Relationships
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    mla_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Link to related item (news, schedule, etc.)
    related_item_type = Column(String(50))  # news, schedule, complaint
    related_item_id = Column(String(50))
    
    # Display settings
    priority = Column(Integer, default=1)  # Higher number = higher priority
    is_active = Column(Boolean, default=True, index=True)
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow, index=True)
    end_time = Column(DateTime)  # When to stop showing in ticker
    
    # Styling
    background_color = Column(String(20), default="#007bff")
    text_color = Column(String(20), default="#ffffff")
    icon = Column(String(50))  # Icon name or emoji
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    constituency = relationship("Constituency")
    mla = relationship("User", foreign_keys=[mla_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<TickerItem(id={self.id}, content='{self.content[:30]}...')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "content_type": self.content_type,
            "constituency_id": self.constituency_id,
            "mla_id": self.mla_id,
            "related_item_type": self.related_item_type,
            "related_item_id": self.related_item_id,
            "priority": self.priority,
            "is_active": self.is_active,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "background_color": self.background_color,
            "text_color": self.text_color,
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
