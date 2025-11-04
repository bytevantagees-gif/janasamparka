"""
Polls router - CRUD operations for public polls
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.poll import Poll, PollOption, Vote
from app.models.ward import Ward
from app.models.user import User
from app.schemas.poll import PollCreate, PollResponse, VoteCreate, VoteResponse

router = APIRouter()


@router.post("/", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
async def create_poll(
    poll: PollCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new poll with options
    """
    # Create poll
    new_poll = Poll(
        title=poll.title,
        description=poll.description,
        ward_id=poll.ward_id,
        start_date=poll.start_date,
        end_date=poll.end_date,
        is_active=True
    )
    
    db.add(new_poll)
    db.flush()  # Get poll ID without committing
    
    # Create poll options
    for option_data in poll.options:
        poll_option = PollOption(
            poll_id=new_poll.id,
            option_text=option_data.option_text,
            vote_count=0
        )
        db.add(poll_option)
    
    db.commit()
    db.refresh(new_poll)
    
    return new_poll


@router.get("/", response_model=List[PollResponse])
async def get_polls(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    ward_id: Optional[UUID] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get list of polls
    Non-admin users only see polls from their own constituency
    """
    query = db.query(Poll).join(Ward, Poll.ward_id == Ward.id)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Ward.constituency_id == constituency_filter)
    
    if is_active is not None:
        query = query.filter(Poll.is_active == is_active)
    
    if ward_id:
        query = query.filter(Poll.ward_id == ward_id)
    
    polls = query.order_by(Poll.created_at.desc()).offset(skip).limit(limit).all()
    return polls


@router.get("/{poll_id}", response_model=PollResponse)
async def get_poll(
    poll_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific poll by ID
    """
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    return poll


@router.post("/{poll_id}/vote", response_model=VoteResponse, status_code=status.HTTP_201_CREATED)
async def vote_on_poll(
    poll_id: UUID,
    vote_data: VoteCreate,
    db: Session = Depends(get_db)
):
    """
    Cast a vote on a poll
    TODO: Add user authentication to get user_id
    """
    # Check if poll exists and is active
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    if not poll.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Poll is not active"
        )
    
    # Check if poll has ended
    if datetime.utcnow() > poll.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Poll has ended"
        )
    
    # Check if option exists
    option = db.query(PollOption).filter(PollOption.id == vote_data.option_id).first()
    
    if not option or option.poll_id != poll_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll option not found"
        )
    
    # TODO: Check if user has already voted (requires authentication)
    # For now, using placeholder user_id
    user_id = UUID("00000000-0000-0000-0000-000000000000")
    
    # Check if user already voted
    existing_vote = db.query(Vote).filter(
        Vote.poll_id == poll_id,
        Vote.user_id == user_id
    ).first()
    
    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted on this poll"
        )
    
    # Create vote
    new_vote = Vote(
        poll_id=poll_id,
        option_id=vote_data.option_id,
        user_id=user_id
    )
    
    # Increment vote count
    option.vote_count += 1
    
    # Update poll total votes
    poll.total_votes += 1
    
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    
    return new_vote


@router.post("/{poll_id}/end", response_model=PollResponse)
async def end_poll(
    poll_id: UUID,
    db: Session = Depends(get_db)
):
    """
    End a poll (set is_active to False)
    TODO: Add authorization - only MLA/Admin can end polls
    """
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    poll.is_active = False
    poll.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(poll)
    
    return poll


@router.get("/{poll_id}/results")
async def get_poll_results(
    poll_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get poll results with detailed statistics
    """
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    options = db.query(PollOption).filter(PollOption.poll_id == poll_id).all()
    
    results = {
        "poll_id": str(poll.id),
        "title": poll.title,
        "total_votes": poll.total_votes,
        "is_active": poll.is_active,
        "end_date": poll.end_date.isoformat(),
        "options": [
            {
                "option_id": str(option.id),
                "option_text": option.option_text,
                "vote_count": option.vote_count,
                "percentage": round((option.vote_count / poll.total_votes * 100), 2) if poll.total_votes > 0 else 0
            }
            for option in options
        ]
    }
    
    return results
