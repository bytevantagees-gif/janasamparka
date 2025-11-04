"""
Ward model with PostGIS support
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.core.database import Base


class Ward(Base):
    """Ward model with geographic boundaries"""
    __tablename__ = "wards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    ward_number = Column(Integer, nullable=False)
    taluk = Column(String(255), nullable=False)
    
    # Multi-tenant: Each ward belongs to one constituency
    constituency_id = Column(UUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False)
    
    # PostGIS geometry column for ward boundaries
    geom = Column(Geometry('POLYGON', srid=4326))
    
    population = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Ward {self.ward_number}: {self.name}>"
