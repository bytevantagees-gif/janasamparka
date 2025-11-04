"""
Pydantic schemas for News, Schedule, and Ticker APIs
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.news import NewsCategory, NewsPriority, ScheduleType, ScheduleStatus


# News Schemas
class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=1000)
    category: NewsCategory
    priority: NewsPriority = NewsPriority.MEDIUM
    featured_image_url: Optional[str] = Field(None, max_length=500)
    image_urls: Optional[List[str]] = []
    is_published: bool = False
    is_featured: bool = False
    show_in_ticker: bool = False
    expires_at: Optional[datetime] = None
    source: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = []
    
    @validator('image_urls')
    def validate_image_urls(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 image URLs allowed')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        return v


class NewsCreate(NewsBase):
    mla_id: Optional[str] = None  # Required if not MLA


class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=1000)
    category: Optional[NewsCategory] = None
    priority: Optional[NewsPriority] = None
    featured_image_url: Optional[str] = Field(None, max_length=500)
    image_urls: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    show_in_ticker: Optional[bool] = None
    expires_at: Optional[datetime] = None
    source: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = None
    is_archived: Optional[bool] = None


class NewsResponse(NewsBase):
    id: str
    constituency_id: str
    mla_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    view_count: int
    is_archived: bool
    
    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    items: List[NewsResponse]
    total: int
    page: int
    size: int
    pages: int


# Schedule Schemas
class ScheduleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    schedule_type: ScheduleType
    venue: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = None
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    start_datetime: datetime
    end_datetime: datetime
    is_all_day: bool = False
    is_public: bool = True
    is_featured: bool = False
    expected_attendees: Optional[int] = Field(None, ge=0)
    max_attendees: Optional[int] = Field(None, ge=1)
    registration_required: bool = False
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=200)
    agenda: Optional[str] = None
    requirements: Optional[str] = None
    external_links: Optional[List[str]] = []
    
    @validator('end_datetime')
    def validate_end_datetime(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End datetime must be after start datetime')
        return v
    
    @validator('max_attendees')
    def validate_max_attendees(cls, v, values):
        if v and 'expected_attendees' in values and values['expected_attendees']:
            if v < values['expected_attendees']:
                raise ValueError('Max attendees must be greater than or equal to expected attendees')
        return v
    
    @validator('external_links')
    def validate_external_links(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 external links allowed')
        return v


class ScheduleCreate(ScheduleBase):
    mla_id: Optional[str] = None  # Required if not MLA


class ScheduleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    venue: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = None
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    is_all_day: Optional[bool] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    status: Optional[ScheduleStatus] = None
    expected_attendees: Optional[int] = Field(None, ge=0)
    max_attendees: Optional[int] = Field(None, ge=1)
    registration_required: Optional[bool] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=200)
    agenda: Optional[str] = None
    requirements: Optional[str] = None
    external_links: Optional[List[str]] = None


class ScheduleResponse(ScheduleBase):
    id: str
    mla_id: str
    constituency_id: str
    created_by: str
    status: ScheduleStatus
    created_at: datetime
    updated_at: datetime
    reminder_sent: bool
    reminder_minutes_before: int
    
    class Config:
        from_attributes = True


class ScheduleListResponse(BaseModel):
    items: List[ScheduleResponse]
    total: int
    page: int
    size: int
    pages: int


# Ticker Schemas
class TickerItemBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    content_type: str = Field("text", max_length=50)
    related_item_type: Optional[str] = Field(None, max_length=50)
    related_item_id: Optional[str] = Field(None, max_length=50)
    priority: int = Field(1, ge=1, le=10)
    is_active: bool = True
    end_time: Optional[datetime] = None
    background_color: str = Field("#007bff", max_length=20)
    text_color: str = Field("#ffffff", max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ['text', 'link', 'announcement', 'alert', 'info']
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of: {allowed_types}')
        return v
    
    @validator('background_color', 'text_color')
    def validate_colors(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color (e.g., #007bff)')
        return v


class TickerItemCreate(TickerItemBase):
    mla_id: Optional[str] = None  # Required if not MLA
    start_time: Optional[datetime] = None


class TickerItemUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    content_type: Optional[str] = Field(None, max_length=50)
    related_item_type: Optional[str] = Field(None, max_length=50)
    related_item_id: Optional[str] = Field(None, max_length=50)
    priority: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    background_color: Optional[str] = Field(None, max_length=20)
    text_color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)


class TickerItemResponse(TickerItemBase):
    id: str
    constituency_id: str
    mla_id: str
    created_by: str
    start_time: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TickerItemListResponse(BaseModel):
    items: List[TickerItemResponse]


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_news: int
    published_news: int
    featured_news: int
    upcoming_schedules: int
    active_ticker_items: int


class DashboardContent(BaseModel):
    featured_news: List[NewsResponse]
    latest_news: List[NewsResponse]
    upcoming_schedules: List[ScheduleResponse]
    ticker_items: List[TickerItemResponse]
    stats: DashboardStats


# Analytics Schemas
class NewsAnalytics(BaseModel):
    total_views: int
    views_by_category: dict
    published_by_month: dict
    most_viewed: List[NewsResponse]


class ScheduleAnalytics(BaseModel):
    total_events: int
    events_by_type: dict
    upcoming_events: int
    completed_events: int
    cancelled_events: int


class TickerAnalytics(BaseModel):
    total_impressions: int
    active_items: int
    click_through_rate: float


class ContentAnalytics(BaseModel):
    news: NewsAnalytics
    schedule: ScheduleAnalytics
    ticker: TickerAnalytics
    period_start: datetime
    period_end: datetime
