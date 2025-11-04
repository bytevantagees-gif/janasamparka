"""Pydantic schemas for budget tracking."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Budget Schemas

class BudgetBase(BaseModel):
    """Base budget schema."""
    financial_year: str = Field(..., description="Financial year e.g., '2024-2025'")
    category: str = Field(..., description="Category: roads, water, electricity, etc.")
    allocated: int = Field(..., ge=0, description="Total allocated budget in rupees")
    notes: Optional[str] = None


class WardBudgetCreate(BudgetBase):
    """Schema for creating ward budget."""
    ward_id: UUID


class WardBudgetUpdate(BaseModel):
    """Schema for updating ward budget."""
    allocated: Optional[int] = Field(None, ge=0)
    spent: Optional[int] = Field(None, ge=0)
    committed: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class WardBudgetResponse(BudgetBase):
    """Ward budget response schema."""
    id: UUID
    ward_id: UUID
    spent: int
    committed: int
    remaining: int
    utilization_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DepartmentBudgetCreate(BudgetBase):
    """Schema for creating department budget."""
    department_id: UUID
    constituency_id: UUID


class DepartmentBudgetUpdate(BaseModel):
    """Schema for updating department budget."""
    allocated: Optional[int] = Field(None, ge=0)
    spent: Optional[int] = Field(None, ge=0)
    committed: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class DepartmentBudgetResponse(BudgetBase):
    """Department budget response schema."""
    id: UUID
    department_id: UUID
    constituency_id: UUID
    spent: int
    committed: int
    remaining: int
    utilization_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Transaction Schemas

class BudgetTransactionCreate(BaseModel):
    """Schema for creating budget transaction."""
    transaction_type: str = Field(..., description="allocation, commitment, expense, or refund")
    amount: int = Field(..., gt=0, description="Transaction amount in rupees")
    description: str = Field(..., min_length=1)
    complaint_id: Optional[UUID] = None


class BudgetTransactionResponse(BaseModel):
    """Budget transaction response schema."""
    id: UUID
    ward_budget_id: Optional[UUID]
    department_budget_id: Optional[UUID]
    transaction_type: str
    amount: int
    description: str
    complaint_id: Optional[UUID]
    performed_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Schemas

class BudgetSummary(BaseModel):
    """Budget summary for dashboard."""
    category: str
    allocated: int
    spent: int
    committed: int
    remaining: int
    utilization_percentage: float
    complaint_count: int = 0  # Number of complaints in this category


class ConstituencyBudgetOverview(BaseModel):
    """Overall budget overview for a constituency."""
    constituency_id: UUID
    financial_year: str
    total_allocated: int
    total_spent: int
    total_committed: int
    total_remaining: int
    overall_utilization: float
    by_category: List[BudgetSummary]
    by_ward: Optional[List[dict]] = None
    by_department: Optional[List[dict]] = None


class BudgetTransparencyReport(BaseModel):
    """Public transparency report."""
    constituency_id: UUID
    constituency_name: str
    financial_year: str
    total_budget: int
    spent_to_date: int
    projects_completed: int
    projects_ongoing: int
    top_spending_categories: List[dict]
    recent_transactions: List[BudgetTransactionResponse]
    utilization_by_month: List[dict]
