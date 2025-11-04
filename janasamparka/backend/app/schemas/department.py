"""
Department schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class DepartmentBase(BaseModel):
    name: str
    code: str
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    complaint_count: Optional[int] = 0

    class Config:
        from_attributes = True
