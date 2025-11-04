"""
MLA Social Feed Models - Twitter-like posts with images/videos and moderated comments
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid
from app.core.database import Base


class PostType(str, Enum):
    """Post content types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MIXED = "mixed"  # Text + media
    MEETING = "meeting"  # Meeting announcement


class PostStatus(str, Enum):
    """Post status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SocialPost(Base):
    """MLA Social posts - like tweets"""
    __tablename__ = "social_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Author (MLAs, Admins can post)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    author_name = Column(String(200))
    author_role = Column(String(50))
    
    # Content
    content = Column(Text, nullable=False)  # The tweet text
    post_type = Column(SQLEnum(PostType), default=PostType.TEXT, index=True)
    
    # Media attachments
    has_media = Column(Boolean, default=False)
    media_urls = Column(Text)  # JSON array of media URLs
    media_types = Column(Text)  # JSON array: ["image", "video"]
    
    # Meeting information (if post_type = meeting)
    meeting_title = Column(String(500))
    meeting_date = Column(DateTime)
    meeting_location = Column(String(500))
    meeting_link = Column(String(500))  # Virtual meeting link
    meeting_capacity = Column(Integer)  # Max attendees
    allow_public = Column(Boolean, default=True)  # Public can attend
    
    # Engagement
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Visibility
    status = Column(SQLEnum(PostStatus), default=PostStatus.PUBLISHED, index=True)
    is_pinned = Column(Boolean, default=False, index=True)  # Pin to top
    is_featured = Column(Boolean, default=False)  # Featured on homepage
    
    # Constituency targeting
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=True, index=True)
    is_global = Column(Boolean, default=False)  # Show to all constituencies
    
    # Tags for categorization
    tags = Column(Text)  # Comma-separated: development,infrastructure,education
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, index=True)
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    constituency = relationship("Constituency")
    comments = relationship("SocialComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("SocialLike", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SocialPost(id={self.id}, author={self.author_name})>"


class SocialComment(Base):
    """Comments on social posts - with moderation"""
    __tablename__ = "social_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("social_posts.id"), nullable=False, index=True)
    
    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    author_name = Column(String(200))
    author_role = Column(String(50))
    
    # Content
    content = Column(Text, nullable=False)
    
    # Threading support
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("social_comments.id"), nullable=True)
    reply_level = Column(Integer, default=0)  # 0 = top level, 1 = reply
    
    # Moderation - All comments need approval
    is_approved = Column(Boolean, default=False, index=True)
    is_rejected = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    moderated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime)
    rejection_reason = Column(String(500))
    
    # Engagement
    likes_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited_at = Column(DateTime)
    
    # Relationships
    post = relationship("SocialPost", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])
    moderator = relationship("User", foreign_keys=[moderated_by])
    replies = relationship("SocialComment", backref="parent_comment", remote_side=[id])
    
    def __repr__(self):
        return f"<SocialComment(id={self.id}, post_id={self.post_id})>"


class SocialLike(Base):
    """Likes on posts"""
    __tablename__ = "social_likes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("social_posts.id"), nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    post = relationship("SocialPost", back_populates="likes")
    
    def __repr__(self):
        return f"<SocialLike(user_id={self.user_id}, post_id={self.post_id})>"


class MeetingRegistration(Base):
    """Public registration for MLA meetings"""
    __tablename__ = "meeting_registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("social_posts.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Registration details
    attendee_name = Column(String(200), nullable=False)
    attendee_phone = Column(String(15))
    attendee_email = Column(String(200))
    
    # Status
    is_confirmed = Column(Boolean, default=True)
    is_attended = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    
    # Timestamps
    registered_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime)
    
    # Relationships
    post = relationship("SocialPost")
    user = relationship("User")
    
    def __repr__(self):
        return f"<MeetingRegistration(post_id={self.post_id}, user={self.attendee_name})>"
