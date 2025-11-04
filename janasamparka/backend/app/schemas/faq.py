"""Pydantic schemas for FAQ/Knowledge base."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FAQSolutionCreate(BaseModel):
    """Schema for creating FAQ solution."""
    constituency_id: UUID
    category: str = Field(..., description="Category: roads, water, electricity, etc.")
    title: str = Field(..., min_length=1, max_length=500)
    question_keywords: str = Field(..., description="Keywords for search (comma-separated)")
    solution_text: str = Field(..., min_length=1)
    solution_steps: Optional[str] = None
    kannada_title: Optional[str] = None
    kannada_solution: Optional[str] = None


class FAQSolutionUpdate(BaseModel):
    """Schema for updating FAQ solution."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    question_keywords: Optional[str] = None
    solution_text: Optional[str] = Field(None, min_length=1)
    solution_steps: Optional[str] = None
    kannada_title: Optional[str] = None
    kannada_solution: Optional[str] = None


class FAQSolutionResponse(BaseModel):
    """FAQ solution response schema."""
    id: UUID
    constituency_id: UUID
    category: str
    title: str
    question_keywords: str
    solution_text: str
    solution_steps: Optional[str]
    kannada_title: Optional[str]
    kannada_solution: Optional[str]
    view_count: int
    helpful_count: int
    not_helpful_count: int
    prevented_complaints_count: int
    success_rate: float
    effectiveness_score: float
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FAQSearchResult(BaseModel):
    """FAQ search result with relevance score."""
    faq: FAQSolutionResponse
    relevance_score: float = Field(..., description="Search relevance score 0-1")
    matched_keywords: List[str] = Field(default_factory=list)


class FAQFeedback(BaseModel):
    """Schema for submitting FAQ feedback."""
    helpful: bool = Field(..., description="Was this FAQ helpful?")
    prevented_complaint: bool = Field(default=False, description="Did this prevent you from filing a complaint?")
