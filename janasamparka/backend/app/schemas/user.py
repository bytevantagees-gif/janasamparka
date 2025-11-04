"""
User schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    locale_pref: str = Field(default="kn", pattern=r'^(en|kn)$')


class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    locale_pref: Optional[str] = Field(None, pattern=r'^(en|kn)$')


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    role: str
    is_active: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OTPRequest(BaseModel):
    """Schema for OTP request"""
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')


class OTPVerify(BaseModel):
    """Schema for OTP verification"""
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    otp: str = Field(..., min_length=4, max_length=6)


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
