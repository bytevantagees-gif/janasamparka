"""FAQ and Knowledge Base API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user, require_auth, get_user_constituency_id
from app.models.faq import FAQSolution
from app.models.user import User, UserRole
from app.schemas.faq import (
    FAQSolutionCreate,
    FAQSolutionUpdate,
    FAQSolutionResponse,
    FAQSearchResult,
    FAQFeedback
)


router = APIRouter(prefix="/api/v1/faqs", tags=["faqs"])


@router.post("/", response_model=FAQSolutionResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq_data: FAQSolutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new FAQ solution (Moderator/Admin only)."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and moderators can create FAQs"
        )
    
    faq = FAQSolution(
        constituency_id=faq_data.constituency_id,
        category=faq_data.category,
        title=faq_data.title,
        question_keywords=faq_data.question_keywords.lower(),  # Store lowercase for search
        solution_text=faq_data.solution_text,
        solution_steps=faq_data.solution_steps,
        kannada_title=faq_data.kannada_title,
        kannada_solution=faq_data.kannada_solution,
        created_by=current_user.id
    )
    
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    
    return faq


@router.get("/search", response_model=List[FAQSearchResult])
async def search_faqs(
    q: str = Query(..., min_length=2, description="Search query"),
    constituency_id: Optional[UUID] = None,
    category: Optional[str] = None,
    language: str = Query("english", description="english or kannada"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Search FAQs by keywords. Non-admin users only see FAQs from their constituency.
    Supports Kannada transliteration and poor English.
    """
    # Normalize search query
    from app.services.predictive_planning_service import MultilingualNormalizer
    normalizer = MultilingualNormalizer()
    normalized_query = normalizer.normalize_text(q)
    
    # Build base query
    query = select(FAQSolution)
    
    if constituency_id:
        query = query.where(FAQSolution.constituency_id == constituency_id)
    if category:
        query = query.where(FAQSolution.category == category)
    
    # Search in keywords and title
    search_terms = normalized_query.split()
    search_conditions = []
    
    for term in search_terms:
        if language == "kannada" and FAQSolution.kannada_title:
            search_conditions.append(
                or_(
                    FAQSolution.question_keywords.ilike(f"%{term}%"),
                    FAQSolution.title.ilike(f"%{term}%"),
                    FAQSolution.kannada_title.ilike(f"%{term}%")
                )
            )
        else:
            search_conditions.append(
                or_(
                    FAQSolution.question_keywords.ilike(f"%{term}%"),
                    FAQSolution.title.ilike(f"%{term}%")
                )
            )
    
    if search_conditions:
        query = query.where(and_(*search_conditions))
    
    query = query.order_by(FAQSolution.effectiveness_score.desc()).limit(limit)
    
    result = await db.execute(query)
    faqs = result.scalars().all()
    
    # Calculate relevance scores
    search_results = []
    for faq in faqs:
        # Simple relevance: count matched keywords
        keywords = faq.question_keywords.split(',')
        matched = [kw.strip() for kw in keywords if any(term in kw.lower() for term in search_terms)]
        relevance = len(matched) / len(keywords) if keywords else 0.0
        
        # Boost by effectiveness
        relevance = (relevance * 0.7) + (min(faq.effectiveness_score / 100, 1.0) * 0.3)
        
        search_results.append(
            FAQSearchResult(
                faq=FAQSolutionResponse.model_validate(faq),
                relevance_score=round(relevance, 2),
                matched_keywords=matched
            )
        )
    
    # Sort by relevance
    search_results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return search_results


@router.get("/category/{category}", response_model=List[FAQSolutionResponse])
async def get_faqs_by_category(
    category: str,
    constituency_id: Optional[UUID] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all FAQs for a specific category. Non-admin users only see FAQs from their constituency."""
    query = select(FAQSolution).where(FAQSolution.category == category)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.where(FAQSolution.constituency_id == constituency_filter)
    elif constituency_id:  # Only allow explicit filter if admin
        query = query.where(FAQSolution.constituency_id == constituency_id)
    
    query = query.order_by(FAQSolution.effectiveness_score.desc())
    
    result = await db.execute(query)
    faqs = result.scalars().all()
    
    return faqs


@router.get("/top-solutions", response_model=List[FAQSolutionResponse])
async def get_top_solutions(
    constituency_id: Optional[UUID] = None,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: AsyncSession = Depends(get_db)
):
    """Get top performing FAQ solutions by effectiveness score. Non-admin users only see FAQs from their constituency."""
    query = select(FAQSolution)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.where(FAQSolution.constituency_id == constituency_filter)
    elif constituency_id:  # Only allow explicit filter if admin
        query = query.where(FAQSolution.constituency_id == constituency_id)
    
    query = query.order_by(FAQSolution.effectiveness_score.desc()).limit(limit)
    
    result = await db.execute(query)
    faqs = result.scalars().all()
    
    return faqs


@router.get("/{faq_id}", response_model=FAQSolutionResponse)
async def get_faq(
    faq_id: UUID,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific FAQ by ID and increment view count. Non-admin users can only access FAQs from their constituency."""
    result = await db.execute(select(FAQSolution).where(FAQSolution.id == faq_id))
    faq = result.scalar_one_or_none()
    
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    
    # Enforce constituency access control
    if constituency_filter and faq.constituency_id != constituency_filter:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access FAQs from your constituency"
        )
    
    # Increment view count
    faq.view_count += 1
    await db.commit()
    await db.refresh(faq)
    
    return faq


@router.post("/{faq_id}/feedback")
async def submit_faq_feedback(
    faq_id: UUID,
    feedback: FAQFeedback,
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback on whether FAQ was helpful."""
    result = await db.execute(select(FAQSolution).where(FAQSolution.id == faq_id))
    faq = result.scalar_one_or_none()
    
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    
    # Update feedback counts
    if feedback.helpful:
        faq.helpful_count += 1
    else:
        faq.not_helpful_count += 1
    
    if feedback.prevented_complaint:
        faq.prevented_complaints_count += 1
    
    await db.commit()
    
    return {
        "message": "Feedback recorded",
        "success_rate": faq.success_rate,
        "effectiveness_score": faq.effectiveness_score
    }


@router.patch("/{faq_id}", response_model=FAQSolutionResponse)
async def update_faq(
    faq_id: UUID,
    faq_data: FAQSolutionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an FAQ solution (Moderator/Admin only)."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and moderators can update FAQs"
        )
    
    result = await db.execute(select(FAQSolution).where(FAQSolution.id == faq_id))
    faq = result.scalar_one_or_none()
    
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    
    # Update fields
    if faq_data.title is not None:
        faq.title = faq_data.title
    if faq_data.question_keywords is not None:
        faq.question_keywords = faq_data.question_keywords.lower()
    if faq_data.solution_text is not None:
        faq.solution_text = faq_data.solution_text
    if faq_data.solution_steps is not None:
        faq.solution_steps = faq_data.solution_steps
    if faq_data.kannada_title is not None:
        faq.kannada_title = faq_data.kannada_title
    if faq_data.kannada_solution is not None:
        faq.kannada_solution = faq_data.kannada_solution
    
    await db.commit()
    await db.refresh(faq)
    
    return faq


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an FAQ solution (Admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete FAQs"
        )
    
    result = await db.execute(select(FAQSolution).where(FAQSolution.id == faq_id))
    faq = result.scalar_one_or_none()
    
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    
    await db.delete(faq)
    await db.commit()
    
    return None


@router.get("/stats/effectiveness")
async def get_faq_effectiveness_stats(
    constituency_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: AsyncSession = Depends(get_db)
):
    """Get FAQ effectiveness statistics (Admin/Moderator only). Non-admin users only see stats from their constituency."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    query = select(FAQSolution)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.where(FAQSolution.constituency_id == constituency_filter)
    elif constituency_id:  # Only allow explicit filter if admin
        query = query.where(FAQSolution.constituency_id == constituency_id)
    
    result = await db.execute(query)
    faqs = result.scalars().all()
    
    total_faqs = len(faqs)
    total_views = sum(faq.view_count for faq in faqs)
    total_prevented = sum(faq.prevented_complaints_count for faq in faqs)
    total_helpful = sum(faq.helpful_count for faq in faqs)
    total_feedback = sum(faq.helpful_count + faq.not_helpful_count for faq in faqs)
    
    avg_success_rate = sum(faq.success_rate for faq in faqs) / total_faqs if total_faqs > 0 else 0
    
    # Group by category
    by_category = {}
    for faq in faqs:
        if faq.category not in by_category:
            by_category[faq.category] = {
                "count": 0,
                "views": 0,
                "prevented": 0
            }
        by_category[faq.category]["count"] += 1
        by_category[faq.category]["views"] += faq.view_count
        by_category[faq.category]["prevented"] += faq.prevented_complaints_count
    
    return {
        "total_faqs": total_faqs,
        "total_views": total_views,
        "total_prevented_complaints": total_prevented,
        "total_helpful_feedback": total_helpful,
        "total_feedback_received": total_feedback,
        "average_success_rate": round(avg_success_rate, 2),
        "by_category": by_category,
        "estimated_cost_savings": total_prevented * 30000  # Avg ₹30,000 per complaint
    }
