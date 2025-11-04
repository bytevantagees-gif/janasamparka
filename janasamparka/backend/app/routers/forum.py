"""
Knowledge Forum API Routes - Discussion and Collaboration
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.forum import (
    ForumTopic, ForumPost, ForumLike, ForumSubscription,
    ForumCategory, TopicStatus
)

router = APIRouter()


# ============== Pydantic Schemas ==============

class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    tags: Optional[str] = None
    constituency_id: Optional[str] = None
    is_public: bool = True


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PostCreate(BaseModel):
    content: str
    parent_post_id: Optional[str] = None


class TopicResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    category: str
    author_name: str
    author_role: str
    status: str
    is_pinned: bool
    views_count: int
    replies_count: int
    likes_count: int
    created_at: datetime
    last_activity_at: datetime
    tags: Optional[List[str]] = []
    
    class Config:
        from_attributes = True


# ============== Topic Endpoints ==============

@router.get("/topics", response_model=List[TopicResponse])
async def get_topics(
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all forum topics with filtering"""
    
    query = db.query(ForumTopic)
    
    # Filter by category
    if category:
        query = query.filter(ForumTopic.category == category)
    
    # Filter by status
    if status:
        query = query.filter(ForumTopic.status == status)
    else:
        # By default, show open and pinned topics
        query = query.filter(ForumTopic.status.in_([TopicStatus.OPEN, TopicStatus.PINNED]))
    
    # Search
    if search:
        query = query.filter(
            or_(
                ForumTopic.title.ilike(f'%{search}%'),
                ForumTopic.description.ilike(f'%{search}%'),
                ForumTopic.tags.ilike(f'%{search}%')
            )
        )
    
    # Order by pinned first, then latest activity
    query = query.order_by(
        desc(ForumTopic.is_pinned),
        desc(ForumTopic.last_activity_at)
    )
    
    topics = query.offset(skip).limit(limit).all()
    
    # Convert tags string to list
    result = []
    for topic in topics:
        topic_dict = TopicResponse.model_validate(topic).model_dump()
        topic_dict['tags'] = topic.tags.split(',') if topic.tags else []
        result.append(TopicResponse(**topic_dict))
    
    return result


@router.post("/topics", response_model=TopicResponse)
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new forum topic"""
    
    topic = ForumTopic(
        id=str(uuid.uuid4()),
        title=topic_data.title,
        description=topic_data.description,
        category=topic_data.category,
        tags=topic_data.tags,
        author_id=current_user.id,
        author_name=current_user.name,
        author_role=current_user.role,
        constituency_id=topic_data.constituency_id or current_user.constituency_id,
        is_public=topic_data.is_public,
        status=TopicStatus.OPEN
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    # Auto-subscribe author to their own topic
    subscription = ForumSubscription(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        topic_id=topic.id
    )
    db.add(subscription)
    db.commit()
    
    topic_dict = TopicResponse.model_validate(topic).model_dump()
    topic_dict['tags'] = topic.tags.split(',') if topic.tags else []
    return TopicResponse(**topic_dict)


@router.get("/topics/{topic_id}")
async def get_topic_detail(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get topic details with all posts"""
    
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Increment view count
    topic.views_count += 1
    db.commit()
    
    # Get all approved posts
    posts = db.query(ForumPost).filter(
        and_(
            ForumPost.topic_id == topic_id,
            ForumPost.is_approved == True,
            ForumPost.is_deleted == False
        )
    ).order_by(ForumPost.created_at).all()
    
    # Check if user is subscribed
    is_subscribed = db.query(ForumSubscription).filter(
        and_(
            ForumSubscription.user_id == current_user.id,
            ForumSubscription.topic_id == topic_id
        )
    ).first() is not None
    
    return {
        "topic": {
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "category": topic.category,
            "author_name": topic.author_name,
            "author_role": topic.author_role,
            "status": topic.status,
            "is_pinned": topic.is_pinned,
            "views_count": topic.views_count,
            "replies_count": topic.replies_count,
            "likes_count": topic.likes_count,
            "created_at": topic.created_at,
            "tags": topic.tags.split(',') if topic.tags else []
        },
        "posts": [
            {
                "id": post.id,
                "content": post.content,
                "author_name": post.author_name,
                "author_role": post.author_role,
                "is_solution": post.is_solution,
                "likes_count": post.likes_count,
                "reply_level": post.reply_level,
                "parent_post_id": post.parent_post_id,
                "created_at": post.created_at,
                "edited_at": post.edited_at
            }
            for post in posts
        ],
        "is_subscribed": is_subscribed
    }


@router.patch("/topics/{topic_id}")
async def update_topic(
    topic_id: str,
    topic_data: TopicUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Update topic (admin/mla/moderator only)"""
    
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Update fields
    if topic_data.title:
        topic.title = topic_data.title
    if topic_data.description:
        topic.description = topic_data.description
    if topic_data.status:
        topic.status = topic_data.status
        if topic_data.status == TopicStatus.CLOSED:
            topic.closed_at = datetime.utcnow()
    
    topic.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Topic updated successfully"}


@router.post("/topics/{topic_id}/pin")
async def pin_topic(
    topic_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Pin/unpin a topic"""
    
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic.is_pinned = not topic.is_pinned
    db.commit()
    
    return {"message": f"Topic {'pinned' if topic.is_pinned else 'unpinned'}"}


# ============== Post Endpoints ==============

@router.post("/topics/{topic_id}/posts")
async def create_post(
    topic_id: str,
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a post/reply in a topic"""
    
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if topic.status == TopicStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Topic is closed")
    
    # Calculate reply level
    reply_level = 0
    if post_data.parent_post_id:
        parent = db.query(ForumPost).filter(ForumPost.id == post_data.parent_post_id).first()
        if parent:
            reply_level = parent.reply_level + 1
    
    post = ForumPost(
        id=str(uuid.uuid4()),
        topic_id=topic_id,
        content=post_data.content,
        author_id=current_user.id,
        author_name=current_user.name,
        author_role=current_user.role,
        parent_post_id=post_data.parent_post_id,
        reply_level=reply_level,
        is_approved=False  # Needs moderation
    )
    
    db.add(post)
    db.commit()
    
    return {
        "message": "Post submitted for moderation",
        "post_id": post.id,
        "needs_approval": True
    }


@router.post("/posts/{post_id}/moderate")
async def moderate_post(
    post_id: str,
    action: str,  # 'approve' or 'reject'
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Approve or reject a post"""
    
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if action == 'approve':
        post.is_approved = True
        post.moderated_by = current_user.id
        post.moderated_at = datetime.utcnow()
        
        # Update topic stats
        topic = db.query(ForumTopic).filter(ForumTopic.id == post.topic_id).first()
        if topic:
            topic.replies_count += 1
            topic.last_activity_at = datetime.utcnow()
        
        db.commit()
        return {"message": "Post approved"}
    
    elif action == 'reject':
        post.is_deleted = True
        post.moderated_by = current_user.id
        post.moderated_at = datetime.utcnow()
        db.commit()
        return {"message": "Post rejected"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")


@router.get("/posts/pending")
async def get_pending_posts(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Get posts pending moderation"""
    
    posts = db.query(ForumPost).filter(
        and_(
            ForumPost.is_approved == False,
            ForumPost.is_deleted == False
        )
    ).order_by(ForumPost.created_at).all()
    
    return [
        {
            "id": post.id,
            "topic_id": post.topic_id,
            "content": post.content,
            "author_name": post.author_name,
            "author_role": post.author_role,
            "created_at": post.created_at
        }
        for post in posts
    ]


@router.post("/posts/{post_id}/mark-solution")
async def mark_as_solution(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a post as the solution (topic author only)"""
    
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if current user is topic author
    topic = db.query(ForumTopic).filter(ForumTopic.id == post.topic_id).first()
    if topic.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only topic author can mark solution")
    
    # Unmark all other solutions in this topic
    db.query(ForumPost).filter(
        and_(
            ForumPost.topic_id == post.topic_id,
            ForumPost.is_solution == True
        )
    ).update({"is_solution": False})
    
    # Mark this as solution
    post.is_solution = True
    db.commit()
    
    return {"message": "Post marked as solution"}


# ============== Statistics ==============

@router.get("/stats")
async def get_forum_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get forum statistics"""
    
    total_topics = db.query(func.count(ForumTopic.id)).scalar()
    open_topics = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.status == TopicStatus.OPEN
    ).scalar()
    total_posts = db.query(func.count(ForumPost.id)).filter(
        ForumPost.is_approved == True
    ).scalar()
    pending_posts = db.query(func.count(ForumPost.id)).filter(
        and_(
            ForumPost.is_approved == False,
            ForumPost.is_deleted == False
        )
    ).scalar()
    
    # Category breakdown
    categories = db.query(
        ForumTopic.category,
        func.count(ForumTopic.id).label('count')
    ).group_by(ForumTopic.category).all()
    
    return {
        "total_topics": total_topics,
        "open_topics": open_topics,
        "total_posts": total_posts,
        "pending_moderation": pending_posts,
        "by_category": [
            {"category": cat.category, "count": cat.count}
            for cat in categories
        ]
    }
