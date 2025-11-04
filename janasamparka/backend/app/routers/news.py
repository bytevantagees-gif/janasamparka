"""
News, MLA Schedule, and Ticker API routes
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.news import News, NewsCategory, NewsPriority, MLASchedule, ScheduleType, ScheduleStatus, TickerItem
from app.schemas.news import (
    NewsCreate, NewsUpdate, NewsResponse, NewsListResponse,
    ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleListResponse,
    TickerItemCreate, TickerItemUpdate, TickerItemResponse, TickerItemListResponse
)
from app.services.realtime_service import realtime_service
from app.core.logging import business_logger
from app.core.cache import cache_constituency_data, cache_complaint_stats
import uuid

router = APIRouter()


# News Routes
@router.post("/news", response_model=NewsResponse)
async def create_news(
    news_data: NewsCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new news item"""
    
    # Check permissions - MLA, Moderator, Admin can create news
    if current_user.role not in ["mla", "moderator", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Generate news ID
    news_id = str(uuid.uuid4())
    
    # Create news object
    news = News(
        id=news_id,
        title=news_data.title,
        content=news_data.content,
        summary=news_data.summary,
        category=news_data.category,
        priority=news_data.priority,
        constituency_id=current_user.constituency_id,
        mla_id=current_user.id if current_user.role == "mla" else news_data.mla_id,
        created_by=current_user.id,
        featured_image_url=news_data.featured_image_url,
        image_urls=",".join(news_data.image_urls) if news_data.image_urls else None,
        is_published=news_data.is_published,
        is_featured=news_data.is_featured,
        show_in_ticker=news_data.show_in_ticker,
        published_at=datetime.utcnow() if news_data.is_published else None,
        expires_at=news_data.expires_at,
        source=news_data.source,
        author=news_data.author,
        tags=",".join(news_data.tags) if news_data.tags else None
    )
    
    db.add(news)
    db.commit()
    db.refresh(news)
    
    # Log business event
    business_logger.log_complaint_created(
        complaint_id=news_id,
        user_id=current_user.id,
        constituency_id=current_user.constituency_id,
        category="news_created"
    )
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(current_user.constituency_id).__aexit__
    )
    
    # Send real-time notification if published
    if news.is_published:
        background_tasks.add_task(
            realtime_service.notify_system_notification,
            {
                "title": "News Published",
                "message": news.title,
                "type": "news",
                "data": news.to_dict()
            },
            target_role="citizen",
            constituency_id=current_user.constituency_id
        )
    
    return NewsResponse(**news.to_dict())


@router.get("/news", response_model=NewsListResponse)
async def get_news(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[NewsCategory] = None,
    priority: Optional[NewsPriority] = None,
    is_featured: Optional[bool] = None,
    is_published: Optional[bool] = True,
    constituency_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get news list with filters"""
    
    # Build query
    query = db.query(News)
    
    # Filter by constituency (based on user role)
    if current_user.role == "admin":
        if constituency_id:
            query = query.filter(News.constituency_id == constituency_id)
    else:
        query = query.filter(News.constituency_id == current_user.constituency_id)
    
    # Apply filters
    if category:
        query = query.filter(News.category == category)
    if priority:
        query = query.filter(News.priority == priority)
    if is_featured is not None:
        query = query.filter(News.is_featured == is_featured)
    if is_published is not None:
        query = query.filter(News.is_published == is_published)
    
    # Filter out expired news
    query = query.filter(
        or_(
            News.expires_at.is_(None),
            News.expires_at > datetime.utcnow()
        )
    )
    
    # Order by priority and creation date
    query = query.order_by(
        desc(News.priority),
        desc(News.created_at)
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    news_items = query.offset(offset).limit(size).all()
    
    return NewsListResponse(
        items=[NewsResponse(**news.to_dict()) for news in news_items],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news_item(
    news_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific news item"""
    
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Check constituency access
    if (current_user.role != "admin" and 
        news.constituency_id != current_user.constituency_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Increment view count
    news.view_count += 1
    db.commit()
    
    return NewsResponse(**news.to_dict())


@router.put("/news/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: str,
    news_data: NewsUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update news item"""
    
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Check permissions
    if (current_user.role not in ["admin", "moderator"] and 
        news.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update fields
    update_data = news_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "image_urls" and value:
            setattr(news, field, ",".join(value))
        elif field == "tags" and value:
            setattr(news, field, ",".join(value))
        else:
            setattr(news, field, value)
    
    # Update published_at if being published
    if update_data.get("is_published") and not news.published_at:
        news.published_at = datetime.utcnow()
    
    news.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(news)
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(news.constituency_id).__aexit__
    )
    
    return NewsResponse(**news.to_dict())


@router.delete("/news/{news_id}")
async def delete_news(
    news_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete news item"""
    
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Check permissions
    if (current_user.role not in ["admin", "moderator"] and 
        news.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    constituency_id = news.constituency_id
    db.delete(news)
    db.commit()
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(constituency_id).__aexit__
    )
    
    return {"message": "News deleted successfully"}


# Schedule Routes
@router.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new MLA schedule item"""
    
    # Check permissions - MLA, Moderator, Admin can create schedules
    if current_user.role not in ["mla", "moderator", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Generate schedule ID
    schedule_id = str(uuid.uuid4())
    
    # Create schedule object
    schedule = MLASchedule(
        id=schedule_id,
        title=schedule_data.title,
        description=schedule_data.description,
        mla_id=current_user.id if current_user.role == "mla" else schedule_data.mla_id,
        constituency_id=current_user.constituency_id,
        created_by=current_user.id,
        schedule_type=schedule_data.schedule_type,
        venue=schedule_data.venue,
        address=schedule_data.address,
        latitude=schedule_data.latitude,
        longitude=schedule_data.longitude,
        start_datetime=schedule_data.start_datetime,
        end_datetime=schedule_data.end_datetime,
        is_all_day=schedule_data.is_all_day,
        is_public=schedule_data.is_public,
        is_featured=schedule_data.is_featured,
        expected_attendees=schedule_data.expected_attendees,
        max_attendees=schedule_data.max_attendees,
        registration_required=schedule_data.registration_required,
        contact_person=schedule_data.contact_person,
        contact_phone=schedule_data.contact_phone,
        contact_email=schedule_data.contact_email,
        agenda=schedule_data.agenda,
        requirements=schedule_data.requirements,
        external_links=",".join(schedule_data.external_links) if schedule_data.external_links else None
    )
    
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(current_user.constituency_id).__aexit__
    )
    
    # Send real-time notification if public
    if schedule.is_public:
        background_tasks.add_task(
            realtime_service.notify_system_notification,
            {
                "title": "New Event Scheduled",
                "message": schedule.title,
                "type": "schedule",
                "data": schedule.to_dict()
            },
            target_role="citizen",
            constituency_id=current_user.constituency_id
        )
    
    return ScheduleResponse(**schedule.to_dict())


@router.get("/schedule", response_model=ScheduleListResponse)
async def get_schedules(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    schedule_type: Optional[ScheduleType] = None,
    status: Optional[ScheduleStatus] = None,
    is_featured: Optional[bool] = None,
    is_public: Optional[bool] = True,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    constituency_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get MLA schedule list with filters"""
    
    # Build query
    query = db.query(MLASchedule)
    
    # Filter by constituency (based on user role)
    if current_user.role == "admin":
        if constituency_id:
            query = query.filter(MLASchedule.constituency_id == constituency_id)
    else:
        query = query.filter(MLASchedule.constituency_id == current_user.constituency_id)
    
    # Apply filters
    if schedule_type:
        query = query.filter(MLASchedule.schedule_type == schedule_type)
    if status:
        query = query.filter(MLASchedule.status == status)
    if is_featured is not None:
        query = query.filter(MLASchedule.is_featured == is_featured)
    if is_public is not None:
        query = query.filter(MLASchedule.is_public == is_public)
    
    # Date filters
    if from_date:
        query = query.filter(MLASchedule.start_datetime >= from_date)
    if to_date:
        query = query.filter(MLASchedule.start_datetime <= to_date)
    
    # By default, show upcoming events
    if not from_date and not to_date:
        query = query.filter(MLASchedule.start_datetime >= datetime.utcnow())
    
    # Order by start datetime
    query = query.order_by(asc(MLASchedule.start_datetime))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    schedules = query.offset(offset).limit(size).all()
    
    return ScheduleListResponse(
        items=[ScheduleResponse(**schedule.to_dict()) for schedule in schedules],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/schedule/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule_item(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific schedule item"""
    
    schedule = db.query(MLASchedule).filter(MLASchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check constituency access
    if (current_user.role != "admin" and 
        schedule.constituency_id != current_user.constituency_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ScheduleResponse(**schedule.to_dict())


@router.put("/schedule/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update schedule item"""
    
    schedule = db.query(MLASchedule).filter(MLASchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check permissions
    if (current_user.role not in ["admin", "moderator"] and 
        schedule.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update fields
    update_data = schedule_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "external_links" and value:
            setattr(schedule, field, ",".join(value))
        else:
            setattr(schedule, field, value)
    
    schedule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(schedule)
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(schedule.constituency_id).__aexit__
    )
    
    return ScheduleResponse(**schedule.to_dict())


@router.delete("/schedule/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete schedule item"""
    
    schedule = db.query(MLASchedule).filter(MLASchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check permissions
    if (current_user.role not in ["admin", "moderator"] and 
        schedule.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    constituency_id = schedule.constituency_id
    db.delete(schedule)
    db.commit()
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(constituency_id).__aexit__
    )
    
    return {"message": "Schedule deleted successfully"}


# Ticker Routes
@router.post("/ticker", response_model=TickerItemResponse)
async def create_ticker_item(
    ticker_data: TickerItemCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new ticker item"""
    
    # Check permissions - MLA, Moderator, Admin can create ticker items
    if current_user.role not in ["mla", "moderator", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Generate ticker ID
    ticker_id = str(uuid.uuid4())
    
    # Create ticker item
    ticker = TickerItem(
        id=ticker_id,
        content=ticker_data.content,
        content_type=ticker_data.content_type,
        constituency_id=current_user.constituency_id,
        mla_id=current_user.id if current_user.role == "mla" else ticker_data.mla_id,
        created_by=current_user.id,
        related_item_type=ticker_data.related_item_type,
        related_item_id=ticker_data.related_item_id,
        priority=ticker_data.priority,
        is_active=ticker_data.is_active,
        start_time=ticker_data.start_time or datetime.utcnow(),
        end_time=ticker_data.end_time,
        background_color=ticker_data.background_color,
        text_color=ticker_data.text_color,
        icon=ticker_data.icon
    )
    
    db.add(ticker)
    db.commit()
    db.refresh(ticker)
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(current_user.constituency_id).__aexit__
    )
    
    # Send real-time notification
    background_tasks.add_task(
        realtime_service.notify_system_notification,
        {
            "title": "New Ticker Item",
            "message": ticker.content,
            "type": "ticker",
            "data": ticker.to_dict()
        },
        target_role="citizen",
        constituency_id=current_user.constituency_id
    )
    
    return TickerItemResponse(**ticker.to_dict())


@router.get("/ticker", response_model=TickerItemListResponse)
async def get_ticker_items(
    is_active: Optional[bool] = True,
    constituency_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active ticker items"""
    
    # Build query
    query = db.query(TickerItem)
    
    # Filter by constituency
    if current_user.role == "admin":
        if constituency_id:
            query = query.filter(TickerItem.constituency_id == constituency_id)
    else:
        query = query.filter(TickerItem.constituency_id == current_user.constituency_id)
    
    # Filter active items
    if is_active is not None:
        query = query.filter(TickerItem.is_active == is_active)
    
    # Filter by time
    now = datetime.utcnow()
    query = query.filter(
        and_(
            TickerItem.start_time <= now,
            or_(
                TickerItem.end_time.is_(None),
                TickerItem.end_time >= now
            )
        )
    )
    
    # Order by priority and creation time
    query = query.order_by(desc(TickerItem.priority), desc(TickerItem.created_at))
    
    ticker_items = query.all()
    
    return TickerItemListResponse(
        items=[TickerItemResponse(**ticker.to_dict()) for ticker in ticker_items]
    )


@router.put("/ticker/{ticker_id}", response_model=TickerItemResponse)
async def update_ticker_item(
    ticker_id: str,
    ticker_data: TickerItemUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update ticker item"""
    
    ticker = db.query(TickerItem).filter(TickerItem.id == ticker_id).first()
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker item not found")
    
    # Check permissions
    if (current_user.role not in ["admin", "moderator"] and 
        ticker.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update fields
    update_data = ticker_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticker, field, value)
    
    ticker.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticker)
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(ticker.constituency_id).__aexit__
    )
    
    return TickerItemResponse(**ticker.to_dict())


@router.delete("/ticker/{ticker_id}")
async def delete_ticker_item(
    ticker_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete ticker item"""
    
    ticker = db.query(TickerItem).filter(TickerItem.id == ticker_id).first()
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker item not found")
    
    # Check permissions
    if (current_user.role not in ["admin", "moderator"] and 
        ticker.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    constituency_id = ticker.constituency_id
    db.delete(ticker)
    db.commit()
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(constituency_id).__aexit__
    )
    
    return {"message": "Ticker item deleted successfully"}


# Dashboard Summary
@router.get("/dashboard")
async def get_dashboard_content(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard content - featured news, upcoming schedules, and ticker items"""
    
    constituency_id = current_user.constituency_id
    
    # Get featured news (limit 5)
    featured_news = db.query(News).filter(
        and_(
            News.constituency_id == constituency_id,
            News.is_published == True,
            News.is_featured == True,
            or_(
                News.expires_at.is_(None),
                News.expires_at > datetime.utcnow()
            )
        )
    ).order_by(desc(News.created_at)).limit(5).all()
    
    # Get latest news (limit 10)
    latest_news = db.query(News).filter(
        and_(
            News.constituency_id == constituency_id,
            News.is_published == True,
            or_(
                News.expires_at.is_(None),
                News.expires_at > datetime.utcnow()
            )
        )
    ).order_by(desc(News.created_at)).limit(10).all()
    
    # Get upcoming schedules (next 7 days)
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming_schedules = db.query(MLASchedule).filter(
        and_(
            MLASchedule.constituency_id == constituency_id,
            MLASchedule.is_public == True,
            MLASchedule.start_datetime >= datetime.utcnow(),
            MLASchedule.start_datetime <= next_week,
            MLASchedule.status == ScheduleStatus.SCHEDULED
        )
    ).order_by(asc(MLASchedule.start_datetime)).limit(5).all()
    
    # Get active ticker items
    ticker_items = db.query(TickerItem).filter(
        and_(
            TickerItem.constituency_id == constituency_id,
            TickerItem.is_active == True,
            TickerItem.start_time <= datetime.utcnow(),
            or_(
                TickerItem.end_time.is_(None),
                TickerItem.end_time >= datetime.utcnow()
            )
        )
    ).order_by(desc(TickerItem.priority), desc(TickerItem.created_at)).all()
    
    return {
        "featured_news": [news.to_dict() for news in featured_news],
        "latest_news": [news.to_dict() for news in latest_news],
        "upcoming_schedules": [schedule.to_dict() for schedule in upcoming_schedules],
        "ticker_items": [ticker.to_dict() for ticker in ticker_items]
    }
