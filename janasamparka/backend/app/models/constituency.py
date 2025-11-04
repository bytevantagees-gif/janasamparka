"""
Constituency model for multi-tenant support
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Constituency(Base):
    """
    Constituency model - represents a single MLA constituency
    This is the tenant in our multi-tenant architecture
    """
    __tablename__ = "constituencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False, unique=True)  # e.g., "Puttur"
    code = Column(String(50), unique=True, nullable=False)  # e.g., "PUT001"
    district = Column(String(255), nullable=False)
    state = Column(String(100), default="Karnataka")
    
    # MLA information
    mla_name = Column(String(255))
    mla_party = Column(String(100))
    mla_contact_phone = Column(String(15))
    mla_contact_email = Column(String(255))
    
    # Constituency details
    total_population = Column(Integer, default=0)
    total_wards = Column(Integer, default=0)
    assembly_number = Column(Integer)  # Assembly constituency number
    
    # Configuration
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50), default="basic")  # basic, premium, enterprise
    
    # Metadata
    description = Column(Text)
    logo_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Constituency {self.code}: {self.name}>"
