"""
Conference Chat API Routes - Live chat during video conferences with moderation
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.citizen_engagement import ConferenceChatMessage, VideoConference

router = APIRouter()


# Pydantic Schemas
class ChatMessageCreate(BaseModel):
    message: str
    message_type: Optional[str] = "text"
    is_question: Optional[bool] = False
    reply_to_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: str
    conference_id: str
    sender_id: str
    sender_name: str
    sender_role: str
    message: str
    message_type: str
    is_pinned: bool
    is_question: bool
    is_answered: bool
    is_approved: bool
    is_rejected: bool
    likes_count: int
    reply_to_id: Optional[str]
    sent_at: datetime
    
    class Config:
        from_attributes = True


class ModerationAction(BaseModel):
    action: str  # "approve" or "reject"
    rejection_reason: Optional[str] = None


# ==========================================
# CITIZEN ENDPOINTS - Send messages
# ==========================================

@router.post("/conferences/{conference_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    conference_id: str,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a chat message during a live conference.
    Message goes to moderation queue and is not visible until approved.
    """
    
    # Verify conference exists
    conference = db.query(VideoConference).filter(VideoConference.id == conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    # Create chat message (pending moderation)
    chat_message = ConferenceChatMessage(
        id=str(uuid.uuid4()),
        conference_id=conference_id,
        sender_id=current_user.id,
        sender_name=current_user.name,
        sender_role=current_user.role,
        message=message_data.message,
        message_type=message_data.message_type,
        is_question=message_data.is_question or False,
        reply_to_id=message_data.reply_to_id,
        is_approved=False,  # Pending moderation
        sent_at=datetime.utcnow()
    )
    
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    return chat_message


@router.get("/conferences/{conference_id}/chat", response_model=List[ChatMessageResponse])
async def get_approved_messages(
    conference_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all approved chat messages for a conference.
    Citizens only see approved messages.
    """
    
    # Get only approved messages
    messages = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_approved == True,
            ConferenceChatMessage.is_deleted == False
        )
    ).order_by(ConferenceChatMessage.sent_at).offset(skip).limit(limit).all()
    
    return messages


# ==========================================
# MODERATOR ENDPOINTS - Approve/Reject messages
# ==========================================

@router.get("/conferences/{conference_id}/chat/pending", response_model=List[ChatMessageResponse])
async def get_pending_messages(
    conference_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """
    Get all pending messages waiting for moderation.
    Only accessible to moderators.
    """
    
    pending_messages = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_approved == False,
            ConferenceChatMessage.is_rejected == False,
            ConferenceChatMessage.is_deleted == False
        )
    ).order_by(ConferenceChatMessage.sent_at).all()
    
    return pending_messages


@router.post("/conferences/{conference_id}/chat/{message_id}/moderate")
async def moderate_message(
    conference_id: str,
    message_id: str,
    action_data: ModerationAction,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """
    Approve or reject a chat message.
    Only moderators can perform this action.
    """
    
    # Get the message
    message = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.id == message_id,
            ConferenceChatMessage.conference_id == conference_id
        )
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Update moderation status
    if action_data.action == "approve":
        message.is_approved = True
        message.is_rejected = False
        message.moderated_by = current_user.id
        message.moderated_at = datetime.utcnow()
    elif action_data.action == "reject":
        message.is_approved = False
        message.is_rejected = True
        message.moderated_by = current_user.id
        message.moderated_at = datetime.utcnow()
        message.rejection_reason = action_data.rejection_reason
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")
    
    db.commit()
    db.refresh(message)
    
    return {
        "message": f"Message {action_data.action}d successfully",
        "message_id": message_id,
        "action": action_data.action,
        "moderated_by": current_user.name,
        "moderated_at": message.moderated_at
    }


@router.post("/conferences/{conference_id}/chat/{message_id}/pin")
async def pin_message(
    conference_id: str,
    message_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Pin an important message to the top of chat"""
    
    message = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.id == message_id,
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_approved == True
        )
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not approved")
    
    message.is_pinned = not message.is_pinned
    db.commit()
    
    return {"message": f"Message {'pinned' if message.is_pinned else 'unpinned'}", "is_pinned": message.is_pinned}


@router.post("/conferences/{conference_id}/chat/{message_id}/answer")
async def mark_question_answered(
    conference_id: str,
    message_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Mark a Q&A question as answered"""
    
    message = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.id == message_id,
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_question == True
        )
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Question not found")
    
    message.is_answered = True
    db.commit()
    
    return {"message": "Question marked as answered", "is_answered": True}


@router.get("/conferences/{conference_id}/chat/stats")
async def get_chat_stats(
    conference_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR)),
    db: Session = Depends(get_db)
):
    """Get chat moderation statistics for a conference"""
    
    total_messages = db.query(ConferenceChatMessage).filter(
        ConferenceChatMessage.conference_id == conference_id
    ).count()
    
    approved = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_approved == True
        )
    ).count()
    
    pending = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_approved == False,
            ConferenceChatMessage.is_rejected == False
        )
    ).count()
    
    rejected = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_rejected == True
        )
    ).count()
    
    questions = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_question == True,
            ConferenceChatMessage.is_approved == True
        )
    ).count()
    
    answered_questions = db.query(ConferenceChatMessage).filter(
        and_(
            ConferenceChatMessage.conference_id == conference_id,
            ConferenceChatMessage.is_question == True,
            ConferenceChatMessage.is_answered == True
        )
    ).count()
    
    return {
        "total_messages": total_messages,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "questions": questions,
        "answered_questions": answered_questions,
        "approval_rate": f"{(approved/total_messages*100) if total_messages > 0 else 0:.1f}%"
    }
