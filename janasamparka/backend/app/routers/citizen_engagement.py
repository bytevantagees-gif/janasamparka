"""
Citizen Engagement API Routes - Feedback, Video Conferencing, and Scheduled Broadcasts
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.citizen_engagement import (
    CitizenFeedback, FeedbackType, FeedbackStatus, FeedbackPriority,
    FeedbackResponse, FeedbackVote, VideoConference, VideoConferenceType, 
    VideoConferenceStatus, ConferenceParticipant, ScheduledBroadcast,
    BroadcastType, BroadcastStatus, BroadcastDelivery
)
from app.schemas.citizen_engagement import (
    FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackListResponse,
    FeedbackResponseCreate, FeedbackResponseUpdate, FeedbackResponseResponse,
    VideoConferenceCreate, VideoConferenceUpdate, VideoConferenceResponse,
    VideoConferenceListResponse, BroadcastCreate, BroadcastUpdate,
    BroadcastResponse, BroadcastListResponse
)
from app.services.realtime_service import realtime_service
from app.services.video_service import video_conference_service
from app.services.notification_service import notification_service
from app.core.logging import business_logger
from app.core.cache import cache_constituency_data
import uuid

router = APIRouter()


# Citizen Feedback Routes
@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new citizen feedback/complaint/idea"""
    
    # Generate feedback ID and reference number
    feedback_id = str(uuid.uuid4())
    reference_number = f"FBK{datetime.utcnow().strftime('%Y%m%d')}{feedback_id[:8].upper()}"
    
    # Create feedback object
    feedback = CitizenFeedback(
        id=feedback_id,
        reference_number=reference_number,
        title=feedback_data.title,
        content=feedback_data.content,
        feedback_type=feedback_data.feedback_type,
        priority=feedback_data.priority,
        citizen_id=current_user.id,
        constituency_id=current_user.constituency_id,
        category=feedback_data.category,
        subcategory=feedback_data.subcategory,
        tags=",".join(feedback_data.tags) if feedback_data.tags else None,
        location_address=feedback_data.location_address,
        latitude=feedback_data.latitude,
        longitude=feedback_data.longitude,
        ward_id=feedback_data.ward_id,
        attachment_urls=",".join(feedback_data.attachment_urls) if feedback_data.attachment_urls else None,
        video_url=feedback_data.video_url,
        is_public=feedback_data.is_public,
        is_anonymous=feedback_data.is_anonymous,
        response_required=feedback_data.response_required,
        response_deadline=feedback_data.response_deadline,
        source=feedback_data.source or "web"
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    # Log business event
    business_logger.log_complaint_created(
        complaint_id=feedback_id,
        user_id=current_user.id,
        constituency_id=current_user.constituency_id,
        category=f"feedback_{feedback_data.feedback_type.value}"
    )
    
    # Invalidate cache
    background_tasks.add_task(
        cache_constituency_data(current_user.constituency_id).__aexit__
    )
    
    # Send notifications to MLA and moderators
    if feedback_data.feedback_type in [FeedbackType.COMPLAINT, FeedbackType.GRIEVANCE, FeedbackType.URGENT]:
        background_tasks.add_task(
            realtime_service.notify_system_notification,
            {
                "title": f"New {feedback_data.feedback_type.value.title()} Received",
                "message": feedback.title,
                "type": "feedback",
                "priority": feedback_data.priority.value,
                "data": feedback.to_dict()
            },
            target_role="mla",
            constituency_id=current_user.constituency_id
        )
    
    return FeedbackResponse(**feedback.to_dict())


@router.get("/feedback", response_model=FeedbackListResponse)
async def get_feedback(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    feedback_type: Optional[FeedbackType] = None,
    status: Optional[FeedbackStatus] = None,
    priority: Optional[FeedbackPriority] = None,
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    my_feedback: Optional[bool] = False,
    assigned_to_me: Optional[bool] = False,
    constituency_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback list with filters"""
    
    # Build query
    query = db.query(CitizenFeedback)
    
    # Filter based on user role and permissions
    if current_user.role == "admin":
        if constituency_id:
            query = query.filter(CitizenFeedback.constituency_id == constituency_id)
    elif current_user.role in ["mla", "moderator"]:
        query = query.filter(CitizenFeedback.constituency_id == current_user.constituency_id)
    else:
        # Citizens can only see public feedback or their own
        query = query.filter(
            and_(
                CitizenFeedback.constituency_id == current_user.constituency_id,
                or_(
                    CitizenFeedback.is_public == True,
                    CitizenFeedback.citizen_id == current_user.id
                )
            )
        )
    
    # Apply filters
    if my_feedback:
        query = query.filter(CitizenFeedback.citizen_id == current_user.id)
    
    if assigned_to_me and current_user.role in ["mla", "moderator", "department_officer"]:
        query = query.filter(CitizenFeedback.assigned_to == current_user.id)
    
    if feedback_type:
        query = query.filter(CitizenFeedback.feedback_type == feedback_type)
    if status:
        query = query.filter(CitizenFeedback.status == status)
    if priority:
        query = query.filter(CitizenFeedback.priority == priority)
    if category:
        query = query.filter(CitizenFeedback.category == category)
    if is_public is not None:
        query = query.filter(CitizenFeedback.is_public == is_public)
    
    # Order by priority and creation date
    query = query.order_by(
        desc(CitizenFeedback.priority),
        desc(CitizenFeedback.created_at)
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    feedback_items = query.offset(offset).limit(size).all()
    
    return FeedbackListResponse(
        items=[FeedbackResponse(**feedback.to_dict()) for feedback in feedback_items],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_item(
    feedback_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific feedback item"""
    
    feedback = db.query(CitizenFeedback).filter(CitizenFeedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check access permissions
    if (current_user.role not in ["admin", "mla", "moderator"] and 
        feedback.constituency_id != current_user.constituency_id and
        feedback.citizen_id != current_user.id and
        not feedback.is_public):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FeedbackResponse(**feedback.to_dict())


@router.post("/feedback/{feedback_id}/vote")
async def vote_on_feedback(
    feedback_id: str,
    vote_type: str = Query(..., regex="^(up|down)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vote on feedback (for ideas and suggestions)"""
    
    feedback = db.query(CitizenFeedback).filter(CitizenFeedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check if voting is allowed
    if feedback.feedback_type not in [FeedbackType.IDEA, FeedbackType.SUGGESTION]:
        raise HTTPException(status_code=400, detail="Voting not allowed for this feedback type")
    
    # Check if user has already voted
    existing_vote = db.query(FeedbackVote).filter(
        and_(
            FeedbackVote.feedback_id == feedback_id,
            FeedbackVote.voter_id == current_user.id
        )
    ).first()
    
    if existing_vote:
        # Update existing vote
        if existing_vote.vote_type != vote_type:
            # Remove old vote count
            if existing_vote.vote_type == "up":
                feedback.upvotes -= 1
            else:
                feedback.downvotes -= 1
            
            # Add new vote count
            if vote_type == "up":
                feedback.upvotes += 1
            else:
                feedback.downvotes += 1
            
            existing_vote.vote_type = vote_type
    else:
        # Create new vote
        vote = FeedbackVote(
            id=str(uuid.uuid4()),
            feedback_id=feedback_id,
            voter_id=current_user.id,
            vote_type=vote_type
        )
        db.add(vote)
        
        # Update vote counts
        if vote_type == "up":
            feedback.upvotes += 1
        else:
            feedback.downvotes += 1
    
    # Update cached vote count
    feedback.vote_count = feedback.upvotes + feedback.downvotes
    db.commit()
    
    return {
        "message": "Vote recorded successfully",
        "upvotes": feedback.upvotes,
        "downvotes": feedback.downvotes,
        "vote_count": feedback.vote_count
    }


@router.post("/feedback/{feedback_id}/response", response_model=FeedbackResponseResponse)
async def create_feedback_response(
    feedback_id: str,
    response_data: FeedbackResponseCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create response to feedback"""
    
    feedback = db.query(CitizenFeedback).filter(CitizenFeedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check permissions for responding
    if current_user.role not in ["admin", "mla", "moderator", "department_officer"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to respond")
    
    # Create response
    response = FeedbackResponse(
        id=str(uuid.uuid4()),
        feedback_id=feedback_id,
        content=response_data.content,
        response_type=response_data.response_type,
        responder_id=current_user.id,
        responder_name=current_user.name,
        responder_role=current_user.role,
        attachment_urls=",".join(response_data.attachment_urls) if response_data.attachment_urls else None,
        video_url=response_data.video_url,
        is_public=response_data.is_public,
        is_internal_note=response_data.is_internal_note,
        status_change=response_data.status_change,
        old_status=feedback.status.value if feedback.status else None
    )
    
    db.add(response)
    
    # Update feedback status if needed
    if response_data.status_change:
        feedback.status = FeedbackStatus(response_data.status_change)
        if response_data.status_change == FeedbackStatus.RESOLVED.value:
            feedback.resolved_at = datetime.utcnow()
    
    feedback.last_response_at = datetime.utcnow()
    db.commit()
    db.refresh(response)
    
    # Send notification to feedback creator
    if not response_data.is_internal_note:
        background_tasks.add_task(
            realtime_service.send_to_user,
            feedback.citizen_id,
            {
                "type": "feedback_response",
                "data": {
                    "feedback_id": feedback_id,
                    "response": response.to_dict(),
                    "feedback_title": feedback.title
                }
            }
        )
    
    return FeedbackResponseResponse(**response.to_dict())


# Video Conference Routes
@router.post("/video-conferences", response_model=VideoConferenceResponse)
async def create_video_conference(
    conference_data: VideoConferenceCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new video conference"""
    
    # Check permissions
    if current_user.role not in ["admin", "mla", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Generate conference ID and meeting details
    conference_id = str(uuid.uuid4())
    
    # Create video conference using service
    meeting_details = await video_conference_service.create_meeting(
        title=conference_data.title,
        scheduled_start=conference_data.scheduled_start,
        scheduled_end=conference_data.scheduled_end,
        conference_type=conference_data.conference_type,
        host_id=current_user.id
    )
    
    # Create conference object
    conference = VideoConference(
        id=conference_id,
        title=conference_data.title,
        description=conference_data.description,
        conference_type=conference_data.conference_type,
        host_id=current_user.id,
        constituency_id=current_user.constituency_id,
        scheduled_start=conference_data.scheduled_start,
        scheduled_end=conference_data.scheduled_end,
        max_participants=conference_data.max_participants,
        is_public=conference_data.is_public,
        requires_registration=conference_data.requires_registration,
        is_recorded=conference_data.is_recorded,
        platform=meeting_details["platform"],
        meeting_id=meeting_details["meeting_id"],
        meeting_url=meeting_details["meeting_url"],
        meeting_password=meeting_details["password"],
        host_url=meeting_details["host_url"],
        venue=conference_data.venue,
        address=conference_data.address,
        latitude=conference_data.latitude,
        longitude=conference_data.longitude,
        allowed_roles=",".join(conference_data.allowed_roles) if conference_data.allowed_roles else None,
        invite_only=conference_data.invite_only
    )
    
    db.add(conference)
    db.commit()
    db.refresh(conference)
    
    # Send notifications if public
    if conference.is_public:
        background_tasks.add_task(
            realtime_service.notify_system_notification,
            {
                "title": "New Video Conference Scheduled",
                "message": conference.title,
                "type": "video_conference",
                "data": conference.to_dict()
            },
            target_role="citizen",
            constituency_id=current_user.constituency_id
        )
    
    return VideoConferenceResponse(**conference.to_dict())


@router.get("/video-conferences", response_model=VideoConferenceListResponse)
async def get_video_conferences(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    conference_type: Optional[VideoConferenceType] = None,
    status: Optional[VideoConferenceStatus] = None,
    is_public: Optional[bool] = None,
    upcoming: Optional[bool] = None,
    my_conferences: Optional[bool] = False,
    constituency_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get video conferences list"""
    
    # Build query
    query = db.query(VideoConference)
    
    # Filter by constituency
    if current_user.role == "admin":
        if constituency_id:
            query = query.filter(VideoConference.constituency_id == constituency_id)
    else:
        query = query.filter(VideoConference.constituency_id == current_user.constituency_id)
    
    # Apply filters
    if my_conferences:
        query = query.filter(VideoConference.host_id == current_user.id)
    
    if conference_type:
        query = query.filter(VideoConference.conference_type == conference_type)
    if status:
        query = query.filter(VideoConference.status == status)
    if is_public is not None:
        query = query.filter(VideoConference.is_public == is_public)
    
    if upcoming:
        query = query.filter(
            and_(
                VideoConference.scheduled_start >= datetime.utcnow(),
                VideoConference.status == VideoConferenceStatus.SCHEDULED
            )
        )
    
    # Order by scheduled start time
    query = query.order_by(asc(VideoConference.scheduled_start))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    conferences = query.offset(offset).limit(size).all()
    
    return VideoConferenceListResponse(
        items=[VideoConferenceResponse(**conference.to_dict()) for conference in conferences],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/video-conferences/{conference_id}/join")
async def join_video_conference(
    conference_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a video conference"""
    
    conference = db.query(VideoConference).filter(VideoConference.id == conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    # Check if user can join
    if conference.constituency_id != current_user.constituency_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not conference.is_public and current_user.role not in ["admin", "mla", "moderator"]:
        raise HTTPException(status_code=403, detail="Conference is not public")
    
    # Check if conference is active
    now = datetime.utcnow()
    if now < conference.scheduled_start - timedelta(minutes=15):
        raise HTTPException(status_code=400, detail="Conference has not started yet")
    if now > conference.scheduled_end:
        raise HTTPException(status_code=400, detail="Conference has ended")
    
    # Check or create participant record
    participant = db.query(ConferenceParticipant).filter(
        and_(
            ConferenceParticipant.conference_id == conference_id,
            ConferenceParticipant.participant_id == current_user.id
        )
    ).first()
    
    if not participant:
        if conference.requires_registration:
            raise HTTPException(status_code=400, detail="Registration required for this conference")
        
        # Create participant record
        participant = ConferenceParticipant(
            id=str(uuid.uuid4()),
            conference_id=conference_id,
            participant_id=current_user.id,
            role="participant",
            status="joined",
            joined_at=now
        )
        db.add(participant)
        conference.registered_participants += 1
    else:
        participant.status = "joined"
        participant.joined_at = now
    
    db.commit()
    
    # Generate join URL
    join_url = await video_conference_service.generate_join_url(
        meeting_id=conference.meeting_id,
        participant_name=current_user.name,
        participant_email=current_user.email,
        role="participant"
    )
    
    return {
        "message": "Successfully joined conference",
        "join_url": join_url,
        "meeting_url": conference.meeting_url,
        "meeting_password": conference.meeting_password,
        "conference": conference.to_dict()
    }


# Scheduled Broadcast Routes
@router.post("/broadcasts", response_model=BroadcastResponse)
async def create_scheduled_broadcast(
    broadcast_data: BroadcastCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create scheduled broadcast"""
    
    # Check permissions
    if current_user.role not in ["admin", "mla", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Generate broadcast ID
    broadcast_id = str(uuid.uuid4())
    
    # Create broadcast object
    broadcast = ScheduledBroadcast(
        id=broadcast_id,
        title=broadcast_data.title,
        message=broadcast_data.message,
        broadcast_type=broadcast_data.broadcast_type,
        sender_id=current_user.id,
        constituency_id=current_user.constituency_id,
        scheduled_at=broadcast_data.scheduled_at,
        target_roles=",".join(broadcast_data.target_roles) if broadcast_data.target_roles else None,
        target_wards=",".join(broadcast_data.target_wards) if broadcast_data.target_wards else None,
        target_departments=",".join(broadcast_data.target_departments) if broadcast_data.target_departments else None,
        target_all=broadcast_data.target_all,
        send_push=broadcast_data.send_push,
        send_sms=broadcast_data.send_sms,
        send_email=broadcast_data.send_email,
        send_whatsapp=broadcast_data.send_whatsapp,
        show_in_app=broadcast_data.show_in_app,
        attachment_urls=",".join(broadcast_data.attachment_urls) if broadcast_data.attachment_urls else None,
        video_url=broadcast_data.video_url,
        link_url=broadcast_data.link_url,
        link_text=broadcast_data.link_text,
        priority=broadcast_data.priority,
        expires_at=broadcast_data.expires_at,
        requires_approval=broadcast_data.requires_approval
    )
    
    # Set status based on scheduling
    if broadcast_data.scheduled_at <= datetime.utcnow():
        broadcast.status = BroadcastStatus.SENT
        broadcast.sent_at = datetime.utcnow()
        # Queue for immediate sending
        background_tasks.add_task(
            notification_service.send_broadcast,
            broadcast_id
        )
    else:
        broadcast.status = BroadcastStatus.SCHEDULED
    
    db.add(broadcast)
    db.commit()
    db.refresh(broadcast)
    
    return BroadcastResponse(**broadcast.to_dict())


@router.get("/broadcasts", response_model=BroadcastListResponse)
async def get_scheduled_broadcasts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    broadcast_type: Optional[BroadcastType] = None,
    status: Optional[BroadcastStatus] = None,
    upcoming: Optional[bool] = None,
    my_broadcasts: Optional[bool] = False,
    constituency_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scheduled broadcasts list"""
    
    # Build query
    query = db.query(ScheduledBroadcast)
    
    # Filter by constituency
    if current_user.role == "admin":
        if constituency_id:
            query = query.filter(ScheduledBroadcast.constituency_id == constituency_id)
    else:
        query = query.filter(ScheduledBroadcast.constituency_id == current_user.constituency_id)
    
    # Apply filters
    if my_broadcasts:
        query = query.filter(ScheduledBroadcast.sender_id == current_user.id)
    
    if broadcast_type:
        query = query.filter(ScheduledBroadcast.broadcast_type == broadcast_type)
    if status:
        query = query.filter(ScheduledBroadcast.status == status)
    
    if upcoming:
        query = query.filter(
            and_(
                ScheduledBroadcast.scheduled_at >= datetime.utcnow(),
                ScheduledBroadcast.status == BroadcastStatus.SCHEDULED
            )
        )
    
    # Order by scheduled time
    query = query.order_by(desc(ScheduledBroadcast.scheduled_at))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    broadcasts = query.offset(offset).limit(size).all()
    
    return BroadcastListResponse(
        items=[BroadcastResponse(**broadcast.to_dict()) for broadcast in broadcasts],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/broadcasts/{broadcast_id}/send-now")
async def send_broadcast_now(
    broadcast_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send broadcast immediately"""
    
    broadcast = db.query(ScheduledBroadcast).filter(ScheduledBroadcast.id == broadcast_id).first()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    # Check permissions
    if (current_user.role not in ["admin", "mla", "moderator"] and 
        broadcast.sender_id != current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if broadcast.status == BroadcastStatus.SENT:
        raise HTTPException(status_code=400, detail="Broadcast already sent")
    
    # Update status and send
    broadcast.status = BroadcastStatus.SENT
    broadcast.sent_at = datetime.utcnow()
    db.commit()
    
    # Queue for sending
    background_tasks.add_task(
        notification_service.send_broadcast,
        broadcast_id
    )
    
    return {"message": "Broadcast sent successfully"}


# Dashboard Summary
@router.get("/dashboard")
async def get_engagement_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get engagement dashboard summary"""
    
    constituency_id = current_user.constituency_id
    
    # Get feedback statistics
    feedback_stats = db.query(
        CitizenFeedback.feedback_type,
        CitizenFeedback.status,
        func.count(CitizenFeedback.id).label('count')
    ).filter(
        CitizenFeedback.constituency_id == constituency_id
    ).group_by(CitizenFeedback.feedback_type, CitizenFeedback.status).all()
    
    # Get upcoming conferences
    upcoming_conferences = db.query(VideoConference).filter(
        and_(
            VideoConference.constituency_id == constituency_id,
            VideoConference.scheduled_start >= datetime.utcnow(),
            VideoConference.scheduled_start <= datetime.utcnow() + timedelta(days=7),
            VideoConference.is_public == True
        )
    ).order_by(asc(VideoConference.scheduled_start)).limit(5).all()
    
    # Get scheduled broadcasts
    scheduled_broadcasts = db.query(ScheduledBroadcast).filter(
        and_(
            ScheduledBroadcast.constituency_id == constituency_id,
            ScheduledBroadcast.scheduled_at >= datetime.utcnow(),
            ScheduledBroadcast.scheduled_at <= datetime.utcnow() + timedelta(days=7),
            ScheduledBroadcast.status == BroadcastStatus.SCHEDULED
        )
    ).order_by(asc(ScheduledBroadcast.scheduled_at)).limit(5).all()
    
    # Get recent feedback
    recent_feedback = db.query(CitizenFeedback).filter(
        CitizenFeedback.constituency_id == constituency_id
    ).order_by(desc(CitizenFeedback.created_at)).limit(10).all()
    
    return {
        "feedback_stats": [
            {
                "type": stat.feedback_type.value,
                "status": stat.status.value,
                "count": stat.count
            }
            for stat in feedback_stats
        ],
        "upcoming_conferences": [conference.to_dict() for conference in upcoming_conferences],
        "scheduled_broadcasts": [broadcast.to_dict() for broadcast in scheduled_broadcasts],
        "recent_feedback": [feedback.to_dict() for feedback in recent_feedback]
    }
