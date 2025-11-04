"""
MLA Social Feed API Routes - Twitter-like posts with moderated comments
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.social_feed import (
    SocialPost, SocialComment, SocialLike, MeetingRegistration,
    PostType, PostStatus
)

router = APIRouter()


# ============== Pydantic Schemas ==============

class PostCreate(BaseModel):
    content: str
    post_type: str = "text"
    media_urls: Optional[str] = None
    media_types: Optional[str] = None
    meeting_title: Optional[str] = None
    meeting_date: Optional[datetime] = None
    meeting_location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_capacity: Optional[int] = None
    allow_public: bool = True
    tags: Optional[str] = None
    is_global: bool = False


class PostUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    is_pinned: Optional[bool] = None


class CommentCreate(BaseModel):
    content: str
    parent_comment_id: Optional[str] = None


class MeetingRegister(BaseModel):
    attendee_name: str
    attendee_phone: Optional[str] = None
    attendee_email: Optional[str] = None


# ============== Post Endpoints ==============

@router.get("/posts")
async def get_posts(
    post_type: Optional[str] = None,
    status: str = "published",
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all social posts"""
    
    query = db.query(SocialPost)
    
    # Filter by status
    query = query.filter(SocialPost.status == status)
    
    # Filter by type
    if post_type:
        query = query.filter(SocialPost.post_type == post_type)
    
    # Show user's constituency or global posts
    if current_user.role != UserRole.ADMIN:
        query = query.filter(
            or_(
                SocialPost.is_global == True,
                SocialPost.constituency_id == current_user.constituency_id
            )
        )
    
    # Order by pinned first, then newest
    query = query.order_by(
        desc(SocialPost.is_pinned),
        desc(SocialPost.published_at)
    )
    
    posts = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": post.id,
            "author_name": post.author_name,
            "author_role": post.author_role,
            "content": post.content,
            "post_type": post.post_type,
            "has_media": post.has_media,
            "media_urls": post.media_urls,
            "media_types": post.media_types,
            "meeting_title": post.meeting_title,
            "meeting_date": post.meeting_date,
            "meeting_location": post.meeting_location,
            "meeting_link": post.meeting_link,
            "meeting_capacity": post.meeting_capacity,
            "allow_public": post.allow_public,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "views_count": post.views_count,
            "is_pinned": post.is_pinned,
            "is_featured": post.is_featured,
            "tags": post.tags.split(',') if post.tags else [],
            "created_at": post.created_at,
            "published_at": post.published_at
        }
        for post in posts
    ]


@router.post("/posts")
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Create a new social post (MLAs, Admins, Moderators only)"""
    
    post = SocialPost(
        id=str(uuid.uuid4()),
        author_id=current_user.id,
        author_name=current_user.name,
        author_role=current_user.role,
        content=post_data.content,
        post_type=post_data.post_type,
        has_media=bool(post_data.media_urls),
        media_urls=post_data.media_urls,
        media_types=post_data.media_types,
        meeting_title=post_data.meeting_title,
        meeting_date=post_data.meeting_date,
        meeting_location=post_data.meeting_location,
        meeting_link=post_data.meeting_link,
        meeting_capacity=post_data.meeting_capacity,
        allow_public=post_data.allow_public,
        tags=post_data.tags,
        is_global=post_data.is_global,
        constituency_id=None if post_data.is_global else current_user.constituency_id,
        status=PostStatus.PUBLISHED,
        published_at=datetime.utcnow()
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return {"message": "Post created successfully", "post_id": post.id}


@router.get("/posts/{post_id}")
async def get_post_detail(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get post details with approved comments"""
    
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    post.views_count += 1
    db.commit()
    
    # Get approved comments
    comments = db.query(SocialComment).filter(
        and_(
            SocialComment.post_id == post_id,
            SocialComment.is_approved == True,
            SocialComment.is_deleted == False
        )
    ).order_by(SocialComment.created_at).all()
    
    return {
        "post": {
            "id": post.id,
            "author_name": post.author_name,
            "author_role": post.author_role,
            "content": post.content,
            "post_type": post.post_type,
            "has_media": post.has_media,
            "media_urls": post.media_urls,
            "media_types": post.media_types,
            "meeting_title": post.meeting_title,
            "meeting_date": post.meeting_date,
            "meeting_location": post.meeting_location,
            "meeting_link": post.meeting_link,
            "meeting_capacity": post.meeting_capacity,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "views_count": post.views_count,
            "tags": post.tags.split(',') if post.tags else [],
            "created_at": post.created_at
        },
        "comments": [
            {
                "id": comment.id,
                "author_name": comment.author_name,
                "author_role": comment.author_role,
                "content": comment.content,
                "likes_count": comment.likes_count,
                "reply_level": comment.reply_level,
                "created_at": comment.created_at
            }
            for comment in comments
        ]
    }


@router.patch("/posts/{post_id}")
async def update_post(
    post_id: str,
    post_data: PostUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Update a post"""
    
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Only author or admin can update
    if post.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if post_data.content:
        post.content = post_data.content
    if post_data.status:
        post.status = post_data.status
    if post_data.is_pinned is not None:
        post.is_pinned = post_data.is_pinned
    
    post.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Post updated successfully"}


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like/unlike a post"""
    
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already liked
    existing_like = db.query(SocialLike).filter(
        and_(
            SocialLike.post_id == post_id,
            SocialLike.user_id == current_user.id
        )
    ).first()
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        db.commit()
        return {"message": "Post unliked", "liked": False}
    else:
        # Like
        like = SocialLike(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            post_id=post_id
        )
        db.add(like)
        post.likes_count += 1
        db.commit()
        return {"message": "Post liked", "liked": True}


# ============== Comment Endpoints ==============

@router.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Calculate reply level
    reply_level = 0
    if comment_data.parent_comment_id:
        parent = db.query(SocialComment).filter(
            SocialComment.id == comment_data.parent_comment_id
        ).first()
        if parent:
            reply_level = parent.reply_level + 1
    
    comment = SocialComment(
        id=str(uuid.uuid4()),
        post_id=post_id,
        author_id=current_user.id,
        author_name=current_user.name,
        author_role=current_user.role,
        content=comment_data.content,
        parent_comment_id=comment_data.parent_comment_id,
        reply_level=reply_level,
        is_approved=False  # Needs moderation
    )
    
    db.add(comment)
    db.commit()
    
    return {
        "message": "Comment submitted for moderation",
        "comment_id": comment.id,
        "needs_approval": True
    }


@router.get("/comments/pending")
async def get_pending_comments(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Get comments pending moderation"""
    
    comments = db.query(SocialComment).filter(
        and_(
            SocialComment.is_approved == False,
            SocialComment.is_deleted == False
        )
    ).order_by(SocialComment.created_at).all()
    
    return [
        {
            "id": comment.id,
            "post_id": comment.post_id,
            "author_name": comment.author_name,
            "author_role": comment.author_role,
            "content": comment.content,
            "created_at": comment.created_at
        }
        for comment in comments
    ]


@router.post("/comments/{comment_id}/moderate")
async def moderate_comment(
    comment_id: str,
    action: str,  # 'approve' or 'reject'
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Approve or reject a comment"""
    
    comment = db.query(SocialComment).filter(SocialComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if action == 'approve':
        comment.is_approved = True
        comment.moderated_by = current_user.id
        comment.moderated_at = datetime.utcnow()
        
        # Update post comment count
        post = db.query(SocialPost).filter(SocialPost.id == comment.post_id).first()
        if post:
            post.comments_count += 1
        
        db.commit()
        return {"message": "Comment approved"}
    
    elif action == 'reject':
        comment.is_rejected = True
        comment.is_deleted = True
        comment.moderated_by = current_user.id
        comment.moderated_at = datetime.utcnow()
        db.commit()
        return {"message": "Comment rejected"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")


# ============== Meeting Registration ==============

@router.post("/posts/{post_id}/register")
async def register_for_meeting(
    post_id: str,
    registration_data: MeetingRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register for a public meeting"""
    
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.post_type == PostType.MEETING
        )
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not post.allow_public and current_user.role == UserRole.CITIZEN:
        raise HTTPException(status_code=403, detail="This meeting is not open to public")
    
    # Check capacity
    current_registrations = db.query(func.count(MeetingRegistration.id)).filter(
        and_(
            MeetingRegistration.post_id == post_id,
            MeetingRegistration.is_cancelled == False
        )
    ).scalar()
    
    if post.meeting_capacity and current_registrations >= post.meeting_capacity:
        raise HTTPException(status_code=400, detail="Meeting is full")
    
    # Check if already registered
    existing = db.query(MeetingRegistration).filter(
        and_(
            MeetingRegistration.post_id == post_id,
            MeetingRegistration.user_id == current_user.id,
            MeetingRegistration.is_cancelled == False
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")
    
    registration = MeetingRegistration(
        id=str(uuid.uuid4()),
        post_id=post_id,
        user_id=current_user.id,
        attendee_name=registration_data.attendee_name,
        attendee_phone=registration_data.attendee_phone,
        attendee_email=registration_data.attendee_email
    )
    
    db.add(registration)
    db.commit()
    
    return {"message": "Successfully registered for meeting"}


@router.get("/posts/{post_id}/registrations")
async def get_meeting_registrations(
    post_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Get meeting registrations (moderators only)"""
    
    registrations = db.query(MeetingRegistration).filter(
        and_(
            MeetingRegistration.post_id == post_id,
            MeetingRegistration.is_cancelled == False
        )
    ).all()
    
    return [
        {
            "id": reg.id,
            "attendee_name": reg.attendee_name,
            "attendee_phone": reg.attendee_phone,
            "attendee_email": reg.attendee_email,
            "registered_at": reg.registered_at
        }
        for reg in registrations
    ]


# ============== Statistics ==============

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social feed statistics"""
    
    total_posts = db.query(func.count(SocialPost.id)).filter(
        SocialPost.status == PostStatus.PUBLISHED
    ).scalar()
    
    total_comments = db.query(func.count(SocialComment.id)).filter(
        SocialComment.is_approved == True
    ).scalar()
    
    pending_comments = db.query(func.count(SocialComment.id)).filter(
        and_(
            SocialComment.is_approved == False,
            SocialComment.is_deleted == False
        )
    ).scalar()
    
    upcoming_meetings = db.query(func.count(SocialPost.id)).filter(
        and_(
            SocialPost.post_type == PostType.MEETING,
            SocialPost.meeting_date >= datetime.utcnow()
        )
    ).scalar()
    
    return {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "pending_moderation": pending_comments,
        "upcoming_meetings": upcoming_meetings
    }
