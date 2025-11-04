"""Budget tracking models for wards and departments."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class WardBudget(Base):
    """Budget allocation and tracking for wards."""
    
    __tablename__ = "ward_budgets"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    ward_id = Column(PGUUID(as_uuid=True), ForeignKey("wards.id"), nullable=False)
    financial_year = Column(String, nullable=False)  # e.g., "2024-2025"
    category = Column(String, nullable=False)  # roads, water, electricity, etc.
    
    # Budget amounts in rupees
    allocated = Column(Integer, nullable=False, default=0)  # Total allocated budget
    spent = Column(Integer, nullable=False, default=0)  # Amount actually spent
    committed = Column(Integer, nullable=False, default=0)  # Committed to ongoing projects
    
    # Calculated field: remaining = allocated - spent - committed
    # Not stored, computed dynamically
    
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    ward = relationship("Ward", back_populates="budgets")
    transactions = relationship("BudgetTransaction", back_populates="ward_budget", cascade="all, delete-orphan")
    
    @property
    def remaining(self) -> int:
        """Calculate remaining budget."""
        return self.allocated - self.spent - self.committed
    
    @property
    def utilization_percentage(self) -> float:
        """Calculate budget utilization percentage."""
        if self.allocated == 0:
            return 0.0
        return ((self.spent + self.committed) / self.allocated) * 100
    
    def __repr__(self):
        return f"<WardBudget {self.ward_id} {self.financial_year} {self.category}: ₹{self.remaining:,} remaining>"


class DepartmentBudget(Base):
    """Budget allocation and tracking for departments."""
    
    __tablename__ = "department_budgets"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    department_id = Column(PGUUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    constituency_id = Column(PGUUID(as_uuid=True), ForeignKey("constituencies.id"), nullable=False)
    financial_year = Column(String, nullable=False)
    category = Column(String, nullable=False)
    
    # Budget amounts in rupees
    allocated = Column(Integer, nullable=False, default=0)
    spent = Column(Integer, nullable=False, default=0)
    committed = Column(Integer, nullable=False, default=0)
    
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="budgets")
    constituency = relationship("Constituency")
    transactions = relationship("BudgetTransaction", back_populates="department_budget", cascade="all, delete-orphan")
    
    @property
    def remaining(self) -> int:
        """Calculate remaining budget."""
        return self.allocated - self.spent - self.committed
    
    @property
    def utilization_percentage(self) -> float:
        """Calculate budget utilization percentage."""
        if self.allocated == 0:
            return 0.0
        return ((self.spent + self.committed) / self.allocated) * 100
    
    def __repr__(self):
        return f"<DepartmentBudget {self.department_id} {self.financial_year} {self.category}: ₹{self.remaining:,} remaining>"


class BudgetTransaction(Base):
    """Track individual budget transactions."""
    
    __tablename__ = "budget_transactions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Link to either ward or department budget
    ward_budget_id = Column(PGUUID(as_uuid=True), ForeignKey("ward_budgets.id"), nullable=True)
    department_budget_id = Column(PGUUID(as_uuid=True), ForeignKey("department_budgets.id"), nullable=True)
    
    # Transaction details
    transaction_type = Column(String, nullable=False)  # allocation, commitment, expense, refund
    amount = Column(Integer, nullable=False)  # Amount in rupees
    description = Column(String, nullable=False)
    
    # Optional link to complaint
    complaint_id = Column(PGUUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
    
    # Who performed the transaction
    performed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ward_budget = relationship("WardBudget", back_populates="transactions")
    department_budget = relationship("DepartmentBudget", back_populates="transactions")
    complaint = relationship("Complaint")
    user = relationship("User")
    
    def __repr__(self):
        return f"<BudgetTransaction {self.transaction_type} ₹{self.amount:,}>"
