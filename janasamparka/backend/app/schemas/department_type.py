"""
Department Type schemas for request/response validation
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class DepartmentTypeBase(BaseModel):
    name: str = Field(..., max_length=255, description="Department type name")
    code: str = Field(..., max_length=50, description="Department type code")
    description: Optional[str] = Field(None, description="Department type description")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name")
    color: Optional[str] = Field(None, max_length=20, description="Color code")
    display_order: int = Field(default=0, description="Display order")
    is_active: bool = Field(default=True, description="Is active")


class DepartmentTypeCreate(DepartmentTypeBase):
    pass


class DepartmentTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class DepartmentTypeResponse(DepartmentTypeBase):
    id: UUID
    instance_count: Optional[int] = Field(default=0, description="Number of department instances")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentTypeListResponse(BaseModel):
    total: int
    items: list[DepartmentTypeResponse]
