"""
Pydantic schemas for Citizen Engagement APIs
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.citizen_engagement import (
    FeedbackType, FeedbackStatus, FeedbackPriority,
    VideoConferenceType, VideoConferenceStatus,
    BroadcastType, BroadcastStatus
)


# Feedback Schemas
class FeedbackBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    feedback_type: FeedbackType
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = []
    location_address: Optional[str] = None
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    ward_id: Optional[str] = None
    attachment_urls: Optional[List[str]] = []
    video_url: Optional[str] = Field(None, max_length=500)
    is_public: bool = False
    is_anonymous: bool = False
    response_required: bool = True
    response_deadline: Optional[datetime] = None
    source: Optional[str] = Field("web", max_length=50)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        return v
    
    @validator('attachment_urls')
    def validate_attachment_urls(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 attachment URLs allowed')
        return v


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    feedback_type: Optional[FeedbackType] = None
    status: Optional[FeedbackStatus] = None
    priority: Optional[FeedbackPriority] = None
    assigned_to: Optional[str] = None
    department_id: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    location_address: Optional[str] = None
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    ward_id: Optional[str] = None
    attachment_urls: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    is_anonymous: Optional[bool] = None
    response_required: Optional[bool] = None
    response_deadline: Optional[datetime] = None


class FeedbackResponse(FeedbackBase):
    id: str
    citizen_id: str
    constituency_id: str
    assigned_to: Optional[str]
    department_id: Optional[str]
    upvotes: int
    downvotes: int
    vote_count: int
    response_required: bool
    response_deadline: Optional[datetime]
    last_response_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    reference_number: str
    
    class Config:
        from_attributes = True


class FeedbackListResponse(BaseModel):
    items: List[FeedbackResponse]
    total: int
    page: int
    size: int
    pages: int


# Feedback Response Schemas
class FeedbackResponseBase(BaseModel):
    content: str = Field(..., min_length=1)
    response_type: str = Field("official", max_length=50)
    attachment_urls: Optional[List[str]] = []
    video_url: Optional[str] = Field(None, max_length=500)
    is_public: bool = True
    is_internal_note: bool = False
    status_change: Optional[str] = Field(None, max_length=50)
    
    @validator('attachment_urls')
    def validate_attachment_urls(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 attachment URLs allowed')
        return v


class FeedbackResponseCreate(FeedbackResponseBase):
    pass


class FeedbackResponseUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    response_type: Optional[str] = Field(None, max_length=50)
    attachment_urls: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    is_internal_note: Optional[bool] = None


class FeedbackResponseResponse(FeedbackResponseBase):
    id: str
    feedback_id: str
    responder_id: str
    responder_name: Optional[str]
    responder_role: Optional[str]
    old_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Video Conference Schemas
class VideoConferenceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    conference_type: VideoConferenceType
    scheduled_start: datetime
    scheduled_end: datetime
    max_participants: int = Field(100, ge=1, le=1000)
    is_public: bool = False
    requires_registration: bool = True
    is_recorded: bool = False
    venue: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = None
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    allowed_roles: Optional[List[str]] = []
    invite_only: bool = False
    
    @validator('scheduled_end')
    def validate_scheduled_end(cls, v, values):
        if 'scheduled_start' in values and v <= values['scheduled_start']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('allowed_roles')
    def validate_allowed_roles(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 allowed roles')
        return v


class VideoConferenceCreate(VideoConferenceBase):
    pass


class VideoConferenceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    conference_type: Optional[VideoConferenceType] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, ge=1, le=1000)
    is_public: Optional[bool] = None
    requires_registration: Optional[bool] = None
    is_recorded: Optional[bool] = None
    status: Optional[VideoConferenceStatus] = None
    venue: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = None
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    allowed_roles: Optional[List[str]] = None
    invite_only: Optional[bool] = None


class VideoConferenceResponse(VideoConferenceBase):
    id: str
    host_id: str
    constituency_id: str
    status: VideoConferenceStatus
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    platform: str
    meeting_id: str
    meeting_url: Optional[str]
    meeting_password: Optional[str]
    host_url: Optional[str]
    registered_participants: int
    actual_participants: int
    recording_url: Optional[str]
    transcript_url: Optional[str]
    attachment_urls: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VideoConferenceListResponse(BaseModel):
    items: List[VideoConferenceResponse]
    total: int
    page: int
    size: int
    pages: int


# Conference Participant Schema
class ConferenceParticipantResponse(BaseModel):
    id: str
    conference_id: str
    participant_id: str
    registered_at: datetime
    joined_at: Optional[datetime]
    left_at: Optional[datetime]
    role: str
    status: str
    email: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


# Broadcast Schemas
class BroadcastBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    message: str = Field(..., min_length=1)
    broadcast_type: BroadcastType
    scheduled_at: datetime
    target_roles: Optional[List[str]] = []
    target_wards: Optional[List[str]] = []
    target_departments: Optional[List[str]] = []
    target_all: bool = True
    send_push: bool = True
    send_sms: bool = False
    send_email: bool = False
    send_whatsapp: bool = False
    show_in_app: bool = True
    attachment_urls: Optional[List[str]] = []
    video_url: Optional[str] = Field(None, max_length=500)
    link_url: Optional[str] = Field(None, max_length=500)
    link_text: Optional[str] = Field(None, max_length=200)
    priority: int = Field(1, ge=1, le=10)
    expires_at: Optional[datetime] = None
    requires_approval: bool = False
    
    @validator('scheduled_at')
    def validate_scheduled_at(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v
    
    @validator('target_roles', 'target_wards', 'target_departments')
    def validate_target_lists(cls, v):
        if v and len(v) > 50:
            raise ValueError('Maximum 50 items allowed in target lists')
        return v
    
    @validator('attachment_urls')
    def validate_attachment_urls(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 attachment URLs allowed')
        return v


class BroadcastCreate(BroadcastBase):
    pass


class BroadcastUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    message: Optional[str] = Field(None, min_length=1)
    broadcast_type: Optional[BroadcastType] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[BroadcastStatus] = None
    target_roles: Optional[List[str]] = None
    target_wards: Optional[List[str]] = None
    target_departments: Optional[List[str]] = None
    target_all: Optional[bool] = None
    send_push: Optional[bool] = None
    send_sms: Optional[bool] = None
    send_email: Optional[bool] = None
    send_whatsapp: Optional[bool] = None
    show_in_app: Optional[bool] = None
    attachment_urls: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=500)
    link_url: Optional[str] = Field(None, max_length=500)
    link_text: Optional[str] = Field(None, max_length=200)
    priority: Optional[int] = Field(None, ge=1, le=10)
    expires_at: Optional[datetime] = None
    requires_approval: Optional[bool] = None


class BroadcastResponse(BroadcastBase):
    id: str
    sender_id: str
    constituency_id: str
    status: BroadcastStatus
    sent_at: Optional[datetime]
    sent_count: int
    delivered_count: int
    read_count: int
    click_count: int
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BroadcastListResponse(BaseModel):
    items: List[BroadcastResponse]
    total: int
    page: int
    size: int
    pages: int


# Broadcast Delivery Schema
class BroadcastDeliveryResponse(BaseModel):
    id: str
    broadcast_id: str
    user_id: str
    push_sent: bool
    push_delivered: bool
    push_read: bool
    sms_sent: bool
    sms_delivered: bool
    email_sent: bool
    email_delivered: bool
    email_read: bool
    whatsapp_sent: bool
    whatsapp_delivered: bool
    whatsapp_read: bool
    shown_in_app: bool
    clicked_in_app: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Analytics Schemas
class FeedbackStats(BaseModel):
    type: str
    status: str
    count: int


class EngagementDashboard(BaseModel):
    feedback_stats: List[FeedbackStats]
    upcoming_conferences: List[VideoConferenceResponse]
    scheduled_broadcasts: List[BroadcastResponse]
    recent_feedback: List[FeedbackResponse]


# Vote Schema
class FeedbackVoteResponse(BaseModel):
    id: str
    feedback_id: str
    voter_id: str
    vote_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Join Conference Response
class JoinConferenceResponse(BaseModel):
    message: str
    join_url: str
    meeting_url: str
    meeting_password: Optional[str]
    conference: VideoConferenceResponse


# Quick Actions Schema
class QuickActionRequest(BaseModel):
    action_type: str = Field(..., pattern="^(complaint|suggestion|idea|appointment)$")
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    category: Optional[str] = None
    priority: Optional[str] = "medium"
    attachment_urls: Optional[List[str]] = []


class QuickActionResponse(BaseModel):
    message: str
    feedback_id: Optional[str] = None
    conference_id: Optional[str] = None
    reference_number: Optional[str] = None
    next_steps: Optional[str] = None
