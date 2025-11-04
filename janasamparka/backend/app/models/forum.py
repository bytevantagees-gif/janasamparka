"""
Knowledge Forum Models - Discussion and Knowledge Sharing
Allows MLAs, Citizens, Officials, and Bureaucrats to collaborate
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid
from app.core.database import Base


class ForumCategory(str, Enum):
    """Forum categories for organizing discussions"""
    BEST_PRACTICES = "best_practices"
    POLICY_DISCUSSION = "policy_discussion"
    CITIZEN_ISSUES = "citizen_issues"
    DEVELOPMENT_IDEAS = "development_ideas"
    TECHNICAL_HELP = "technical_help"
    SCHEME_INFORMATION = "scheme_information"
    SUCCESS_STORIES = "success_stories"
    GENERAL = "general"


class TopicStatus(str, Enum):
    """Topic status"""
    OPEN = "open"
    CLOSED = "closed"
    PINNED = "pinned"
    ARCHIVED = "archived"


class ForumTopic(Base):
    """Forum discussion topics"""
    __tablename__ = "forum_topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Topic details
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    category = Column(SQLEnum(ForumCategory), nullable=False, index=True)
    
    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    author_name = Column(String(200))
    author_role = Column(String(50))
    
    # Context (optional - link to specific items)
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=True, index=True)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
    gram_panchayat_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Status and moderation
    status = Column(SQLEnum(TopicStatus), default=TopicStatus.OPEN, index=True)
    is_pinned = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False)
    is_moderated = Column(Boolean, default=True)  # All posts moderated
    
    # Visibility
    is_public = Column(Boolean, default=True)  # Public or role-restricted
    allowed_roles = Column(Text)  # Comma-separated roles if restricted
    
    # Tags for better search
    tags = Column(Text)  # Comma-separated tags
    
    # Statistics
    views_count = Column(Integer, default=0)
    replies_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow, index=True)
    closed_at = Column(DateTime)
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    constituency = relationship("Constituency")
    posts = relationship("ForumPost", back_populates="topic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ForumTopic(id={self.id}, title='{self.title[:50]}...')>"


class ForumPost(Base):
    """Replies/posts in forum topics"""
    __tablename__ = "forum_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("forum_topics.id"), nullable=False, index=True)
    
    # Post content
    content = Column(Text, nullable=False)
    
    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    author_name = Column(String(200))
    author_role = Column(String(50))
    
    # Thread structure (for nested replies)
    parent_post_id = Column(UUID(as_uuid=True), ForeignKey("forum_posts.id"), nullable=True)
    reply_level = Column(Integer, default=0)  # 0 = top level, 1 = reply, 2 = reply to reply
    
    # Moderation
    is_approved = Column(Boolean, default=False, index=True)
    is_deleted = Column(Boolean, default=False)
    moderated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime)
    
    # Engagement
    is_solution = Column(Boolean, default=False)  # Marked as solution by author
    is_helpful = Column(Boolean, default=False)  # Marked as helpful by others
    likes_count = Column(Integer, default=0)
    
    # Attachments
    has_attachments = Column(Boolean, default=False)
    attachment_urls = Column(Text)  # Comma-separated URLs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited_at = Column(DateTime)
    
    # Relationships
    topic = relationship("ForumTopic", back_populates="posts")
    author = relationship("User", foreign_keys=[author_id])
    moderator = relationship("User", foreign_keys=[moderated_by])
    replies = relationship("ForumPost", backref="parent_post", remote_side=[id])
    
    def __repr__(self):
        return f"<ForumPost(id={self.id}, topic_id={self.topic_id})>"


class ForumLike(Base):
    """User likes on topics and posts"""
    __tablename__ = "forum_likes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Can like either topic or post
    topic_id = Column(UUID(as_uuid=True), ForeignKey("forum_topics.id"), nullable=True, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("forum_posts.id"), nullable=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    topic = relationship("ForumTopic")
    post = relationship("ForumPost")
    
    def __repr__(self):
        return f"<ForumLike(user_id={self.user_id})>"


class ForumSubscription(Base):
    """User subscriptions to topics for notifications"""
    __tablename__ = "forum_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("forum_topics.id"), nullable=False, index=True)
    
    # Notification preferences
    notify_on_reply = Column(Boolean, default=True)
    notify_on_solution = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    topic = relationship("ForumTopic")
    
    def __repr__(self):
        return f"<ForumSubscription(user_id={self.user_id}, topic_id={self.topic_id})>"
