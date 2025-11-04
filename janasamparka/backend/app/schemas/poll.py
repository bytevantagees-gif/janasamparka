"""
Poll schemas for request/response validation
"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class PollOptionBase(BaseModel):
    option_text: str


class PollOptionCreate(PollOptionBase):
    pass


class PollOptionResponse(PollOptionBase):
    id: UUID
    poll_id: UUID
    vote_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class PollBase(BaseModel):
    title: str
    description: str
    ward_id: Optional[UUID] = None
    start_date: datetime
    end_date: datetime


class PollCreate(PollBase):
    options: List[PollOptionCreate]


class PollResponse(PollBase):
    id: UUID
    is_active: bool
    total_votes: int
    created_at: datetime
    updated_at: datetime
    options: List[PollOptionResponse] = []

    class Config:
        from_attributes = True


class VoteCreate(BaseModel):
    option_id: UUID


class VoteResponse(BaseModel):
    id: UUID
    poll_id: UUID
    option_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
