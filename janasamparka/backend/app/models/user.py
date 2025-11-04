"""
User model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    CITIZEN = "citizen"
    MODERATOR = "moderator"
    MLA = "mla"
    DEPARTMENT_OFFICER = "department_officer"
    AUDITOR = "auditor"
    ADMIN = "admin"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    locale_pref = Column(String(5), default="kn")  # 'en' or 'kn'
    is_active = Column(String(10), default="true")
    
    # Multi-tenant: Link to constituency
    # A user can belong to one constituency (citizens, department officers)
    # MLAs and admins can access multiple constituencies via permissions
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.name} ({self.phone})>"
