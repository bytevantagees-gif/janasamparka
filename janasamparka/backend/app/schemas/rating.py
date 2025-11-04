"""
Citizen rating and feedback schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CitizenRatingSubmit(BaseModel):
    """Schema for citizen to submit rating"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    
    @validator('feedback')
    def validate_feedback(cls, v):
        """Trim whitespace from feedback"""
        if v:
            return v.strip()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "feedback": "Excellent work! The pothole was fixed perfectly and quickly."
            }
        }


class CitizenRatingResponse(BaseModel):
    """Schema for rating response"""
    citizen_rating: Optional[int] = None
    citizen_feedback: Optional[str] = None
    rating_submitted_at: Optional[datetime] = None
    can_rate: bool = True  # Whether user can rate this complaint
    rating_message: Optional[str] = None  # Message about rating eligibility
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "citizen_rating": 5,
                "citizen_feedback": "Great job!",
                "rating_submitted_at": "2025-10-28T10:30:00",
                "can_rate": False,
                "rating_message": "You have already rated this complaint"
            }
        }


class RatingSummary(BaseModel):
    """Summary of ratings for analytics"""
    total_ratings: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}
    satisfaction_rate: float  # Percentage of 4-5 star ratings
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_ratings": 150,
                "average_rating": 4.2,
                "rating_distribution": {
                    "1": 5,
                    "2": 10,
                    "3": 20,
                    "4": 50,
                    "5": 65
                },
                "satisfaction_rate": 76.67
            }
        }
