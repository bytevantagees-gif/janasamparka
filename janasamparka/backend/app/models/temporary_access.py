"""
Temporary Access Model
For backup login when users' phones are broken/lost
"""
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column, Session
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import random
import string

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class TemporaryAccess(Base):
    """Model for temporary access codes (backup login mechanism)"""
    
    __tablename__ = "temporary_access"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign Keys
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Access Code
    access_code: Mapped[str] = mapped_column(String(6), nullable=False, unique=True, comment="6-digit access code")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="Code expires 24 hours after creation")
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="When code was used for login")
    
    # Relationship
    user: Mapped["User"] = relationship("User", backref="temporary_access_codes")
    
    @staticmethod
    def generate_code() -> str:
        """Generate a random 6-digit access code"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_for_user(user_id: UUID, db: Session) -> "TemporaryAccess":
        """Create a new temporary access code for a user"""
        # Generate unique code
        while True:
            code = TemporaryAccess.generate_code()
            existing = db.query(TemporaryAccess).filter(TemporaryAccess.access_code == code).first()
            if not existing:
                break
        
        # Create access record
        access = TemporaryAccess(
            user_id=user_id,
            access_code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        
        db.add(access)
        db.commit()
        db.refresh(access)
        
        return access
    
    def is_valid(self) -> bool:
        """Check if access code is still valid (not expired and not used)"""
        if self.used_at is not None:
            return False
        if self.expires_at < datetime.now(timezone.utc):
            return False
        return True
    
    def mark_as_used(self, db: Session) -> None:
        """Mark access code as used"""
        self.used_at = datetime.now(timezone.utc)
        db.commit()
    
    def __repr__(self) -> str:
        return f"<TemporaryAccess(code={self.access_code}, user_id={self.user_id}, valid={self.is_valid()})>"
