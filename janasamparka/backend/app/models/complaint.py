"""
Complaint, Media, and StatusLog models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ComplaintStatus(str, enum.Enum):
    """Complaint status enumeration"""
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class ComplaintPriority(str, enum.Enum):
    """Complaint priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Complaint(Base):
    """Complaint/Grievance model"""
    __tablename__ = "complaints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Multi-tenant: Each complaint belongs to one constituency
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False, index=True)
    
    # User who filed the complaint
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Complaint details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))  # e.g., 'road', 'water', 'electricity'
    
    # Location
    lat = Column(Numeric(precision=10, scale=7))
    lng = Column(Numeric(precision=10, scale=7))
    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id"))
    location_description = Column(String(500))
    
    # Assignment and status
    dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # Department officer
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.SUBMITTED)
    priority = Column(Enum(ComplaintPriority), default=ComplaintPriority.MEDIUM)
    
    # Voice transcript (if submitted via voice)
    voice_transcript = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Complaint {self.id}: {self.title[:50]}>"


class MediaType(str, enum.Enum):
    """Media type enumeration"""
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class Media(Base):
    """Media attachments for complaints"""
    __tablename__ = "media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False)
    
    url = Column(String(500), nullable=False)
    media_type = Column(Enum(MediaType), nullable=False)
    file_size = Column(Numeric)  # in bytes
    
    # Optional: geo-tag for before/after photos
    lat = Column(Numeric(precision=10, scale=7))
    lng = Column(Numeric(precision=10, scale=7))
    
    # For department: mark as 'before' or 'after' proof
    proof_type = Column(String(20))  # 'before', 'after', 'evidence'
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<Media {self.media_type}: {self.url}>"


class StatusLog(Base):
    """Status change history for complaints"""
    __tablename__ = "status_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False)
    
    old_status = Column(String(50))
    new_status = Column(String(50), nullable=False)
    
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<StatusLog {self.old_status} → {self.new_status}>"
