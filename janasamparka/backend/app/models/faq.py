"""FAQ and knowledge base models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class FAQSolution(Base):
    """Frequently asked questions and solutions."""
    
    __tablename__ = "faq_solutions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False)
    
    category = Column(String, nullable=False)  # roads, water, electricity, etc.
    title = Column(String, nullable=False)
    question_keywords = Column(Text, nullable=False)  # Searchable keywords
    solution_text = Column(Text, nullable=False)
    solution_steps = Column(Text, nullable=True)  # JSON or numbered steps
    
    # Metrics
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    prevented_complaints_count = Column(Integer, default=0)  # Citizens who found this helpful before filing
    
    # Multilingual support
    kannada_title = Column(String, nullable=True)
    kannada_solution = Column(Text, nullable=True)
    
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    constituency = relationship("Constituency")
    creator = relationship("User")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (helpful / total feedback)."""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return (self.helpful_count / total) * 100
    
    @property
    def effectiveness_score(self) -> float:
        """Overall effectiveness score combining views, helpfulness, and prevented complaints."""
        # Weighted score: views (10%), helpfulness (40%), prevented complaints (50%)
        view_score = min(self.view_count / 100, 1.0) * 10
        
        helpful_score = 0
        if self.helpful_count + self.not_helpful_count > 0:
            helpful_score = (self.helpful_count / (self.helpful_count + self.not_helpful_count)) * 40
        
        prevention_score = min(self.prevented_complaints_count / 10, 1.0) * 50
        
        return view_score + helpful_score + prevention_score
    
    def __repr__(self):
        return f"<FAQSolution {self.category}: {self.title}>"
