"""API endpoints for case management - notes, routing, and escalations."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.case_note import CaseNote, DepartmentRouting, ComplaintEscalation
from app.models.complaint import Complaint
from app.models.department import Department
from app.models.user import User
from app.schemas.case_management import (
    CaseNoteCreate,
    CaseNoteResponse,
    DepartmentRoutingCreate,
    DepartmentRoutingAccept,
    DepartmentRoutingResponse,
    ComplaintEscalationCreate,
    ComplaintEscalationResolve,
    ComplaintEscalationResponse,
    DepartmentSuggestionRequest,
    DepartmentSuggestionResponse
)
from app.services.department_suggestion import DepartmentSuggestionService
from app.services.clustering_service import ClusteringService
from app.services.predictive_planning_service import PredictivePlanningService
from datetime import datetime, timezone


router = APIRouter(prefix="/api/v1/case-management", tags=["case-management"])


# ===== Case Notes =====

@router.post("/complaints/{complaint_id}/notes", response_model=CaseNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_case_note(
    complaint_id: UUID,
    note_data: CaseNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a case note for a complaint."""
    # Verify complaint exists
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    # Create case note
    case_note = CaseNote(
        complaint_id=complaint_id,
        note=note_data.note,
        note_type=note_data.note_type,
        created_by=current_user.id,
        is_public=note_data.is_public,
        resets_idle_timer=note_data.resets_idle_timer
    )
    
    db.add(case_note)
    
    # Reset idle timer if applicable
    if note_data.resets_idle_timer:
        complaint.last_activity_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(case_note)
    
    # Add creator name
    response = CaseNoteResponse.model_validate(case_note)
    response.creator_name = current_user.name
    
    return response


@router.get("/complaints/{complaint_id}/notes", response_model=list[CaseNoteResponse])
async def get_case_notes(
    complaint_id: UUID,
    include_internal: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all case notes for a complaint."""
    # Build query
    query = select(CaseNote).where(CaseNote.complaint_id == complaint_id)
    
    # Filter by visibility based on user role
    if current_user.role == "citizen" or not include_internal:
        query = query.where(CaseNote.is_public == True)
    
    query = query.order_by(CaseNote.created_at.desc())
    
    result = await db.execute(query)
    notes = result.scalars().all()
    
    # Fetch creator names
    creator_ids = {note.created_by for note in notes}
    creator_result = await db.execute(
        select(User.id, User.name).where(User.id.in_(creator_ids))
    )
    creator_map = {uid: name for uid, name in creator_result.fetchall()}
    
    # Build responses
    responses = []
    for note in notes:
        response = CaseNoteResponse.model_validate(note)
        response.creator_name = creator_map.get(note.created_by)
        responses.append(response)
    
    return responses


# ===== Department Routing =====

@router.post("/complaints/{complaint_id}/route", response_model=DepartmentRoutingResponse, status_code=status.HTTP_201_CREATED)
async def route_complaint_to_department(
    complaint_id: UUID,
    routing_data: DepartmentRoutingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Route a complaint to a different department."""
    # Verify complaint exists
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    # Verify target department exists
    dept_result = await db.execute(select(Department).where(Department.id == routing_data.to_dept_id))
    target_dept = dept_result.scalar_one_or_none()
    
    if not target_dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target department not found")
    
    # Check if user has permission to route (department officer or admin/moderator)
    if current_user.role not in ["admin", "moderator", "department_officer"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to route complaints")
    
    # Create routing record
    routing = DepartmentRouting(
        complaint_id=complaint_id,
        from_dept_id=complaint.dept_id,
        to_dept_id=routing_data.to_dept_id,
        reason=routing_data.reason,
        comments=routing_data.comments,
        routed_by=current_user.id
    )
    
    db.add(routing)
    
    # Update complaint department
    complaint.dept_id = routing_data.to_dept_id
    complaint.assigned_to = None  # Clear assignment when routing
    complaint.last_activity_at = datetime.now(timezone.utc)
    
    # Create a case note
    case_note = CaseNote(
        complaint_id=complaint_id,
        note=f"Complaint routed to {target_dept.name}. Reason: {routing_data.reason}. {routing_data.comments or ''}",
        note_type="department_routing",
        created_by=current_user.id,
        is_public=True,
        resets_idle_timer=True
    )
    db.add(case_note)
    
    await db.commit()
    await db.refresh(routing)
    
    # Build response with department names
    response = DepartmentRoutingResponse.model_validate(routing)
    response.to_dept_name = target_dept.name
    response.routed_by_name = current_user.name
    
    if routing.from_dept_id:
        from_dept_result = await db.execute(select(Department).where(Department.id == routing.from_dept_id))
        from_dept = from_dept_result.scalar_one_or_none()
        if from_dept:
            response.from_dept_name = from_dept.name
    
    return response


@router.get("/complaints/{complaint_id}/routing-history", response_model=list[DepartmentRoutingResponse])
async def get_routing_history(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get routing history for a complaint."""
    result = await db.execute(
        select(DepartmentRouting)
        .where(DepartmentRouting.complaint_id == complaint_id)
        .order_by(DepartmentRouting.routed_at.desc())
    )
    routings = result.scalars().all()
    
    # Fetch department and user names
    dept_ids = set()
    user_ids = set()
    for routing in routings:
        if routing.from_dept_id:
            dept_ids.add(routing.from_dept_id)
        dept_ids.add(routing.to_dept_id)
        user_ids.add(routing.routed_by)
        if routing.accepted_by:
            user_ids.add(routing.accepted_by)
    
    dept_result = await db.execute(select(Department.id, Department.name).where(Department.id.in_(dept_ids)))
    dept_map = {did: name for did, name in dept_result.fetchall()}
    
    user_result = await db.execute(select(User.id, User.name).where(User.id.in_(user_ids)))
    user_map = {uid: name for uid, name in user_result.fetchall()}
    
    # Build responses
    responses = []
    for routing in routings:
        response = DepartmentRoutingResponse.model_validate(routing)
        response.from_dept_name = dept_map.get(routing.from_dept_id) if routing.from_dept_id else None
        response.to_dept_name = dept_map.get(routing.to_dept_id)
        response.routed_by_name = user_map.get(routing.routed_by)
        response.accepted_by_name = user_map.get(routing.accepted_by) if routing.accepted_by else None
        responses.append(response)
    
    return responses


# ===== Complaint Escalations =====

@router.post("/complaints/{complaint_id}/escalate", response_model=ComplaintEscalationResponse, status_code=status.HTTP_201_CREATED)
async def escalate_complaint(
    complaint_id: UUID,
    escalation_data: ComplaintEscalationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Escalate a complaint to MLA."""
    # Verify complaint exists
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    # Only the complaint creator can escalate
    if complaint.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the complaint creator can escalate")
    
    # Check if already escalated and unresolved
    existing_result = await db.execute(
        select(ComplaintEscalation).where(
            and_(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.resolved == False
            )
        )
    )
    existing_escalation = existing_result.scalar_one_or_none()
    
    if existing_escalation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This complaint already has an unresolved escalation"
        )
    
    # Create escalation
    escalation = ComplaintEscalation(
        complaint_id=complaint_id,
        reason=escalation_data.reason,
        description=escalation_data.description,
        escalated_by=current_user.id
    )
    
    db.add(escalation)
    
    # Update complaint activity
    complaint.last_activity_at = datetime.now(timezone.utc)
    
    # Create a case note
    case_note = CaseNote(
        complaint_id=complaint_id,
        note=f"Complaint escalated to MLA. Reason: {escalation_data.reason}. {escalation_data.description}",
        note_type="escalation",
        created_by=current_user.id,
        is_public=True,
        resets_idle_timer=True
    )
    db.add(case_note)
    
    await db.commit()
    await db.refresh(escalation)
    
    # Build response
    response = ComplaintEscalationResponse.model_validate(escalation)
    response.escalated_by_name = current_user.name
    
    return response


@router.post("/escalations/{escalation_id}/resolve", response_model=ComplaintEscalationResponse)
async def resolve_escalation(
    escalation_id: UUID,
    resolution_data: ComplaintEscalationResolve,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve an escalation (admin/MLA only)."""
    # Check permissions
    if current_user.role not in ["admin", "mla"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only MLA or admin can resolve escalations")
    
    # Get escalation
    result = await db.execute(select(ComplaintEscalation).where(ComplaintEscalation.id == escalation_id))
    escalation = result.scalar_one_or_none()
    
    if not escalation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalation not found")
    
    if escalation.resolved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escalation already resolved")
    
    # Resolve escalation
    escalation.resolved = True
    escalation.resolution_notes = resolution_data.resolution_notes
    escalation.resolved_by = current_user.id
    escalation.resolved_at = datetime.now(timezone.utc)
    
    # Create case note
    case_note = CaseNote(
        complaint_id=escalation.complaint_id,
        note=f"Escalation resolved by {current_user.name}. Notes: {resolution_data.resolution_notes}",
        note_type="escalation",
        created_by=current_user.id,
        is_public=True,
        resets_idle_timer=True
    )
    db.add(case_note)
    
    await db.commit()
    await db.refresh(escalation)
    
    # Build response
    response = ComplaintEscalationResponse.model_validate(escalation)
    response.resolved_by_name = current_user.name
    
    # Get escalated_by name
    user_result = await db.execute(select(User.name).where(User.id == escalation.escalated_by))
    escalated_by_name = user_result.scalar_one_or_none()
    response.escalated_by_name = escalated_by_name
    
    return response


@router.get("/complaints/{complaint_id}/escalations", response_model=list[ComplaintEscalationResponse])
async def get_complaint_escalations(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all escalations for a complaint."""
    result = await db.execute(
        select(ComplaintEscalation)
        .where(ComplaintEscalation.complaint_id == complaint_id)
        .order_by(ComplaintEscalation.created_at.desc())
    )
    escalations = result.scalars().all()
    
    # Fetch user names
    user_ids = {esc.escalated_by for esc in escalations}
    user_ids.update({esc.resolved_by for esc in escalations if esc.resolved_by})
    
    user_result = await db.execute(select(User.id, User.name).where(User.id.in_(user_ids)))
    user_map = {uid: name for uid, name in user_result.fetchall()}
    
    # Build responses
    responses = []
    for escalation in escalations:
        response = ComplaintEscalationResponse.model_validate(escalation)
        response.escalated_by_name = user_map.get(escalation.escalated_by)
        response.resolved_by_name = user_map.get(escalation.resolved_by) if escalation.resolved_by else None
        responses.append(response)
    
    return responses


# ===== Department Suggestions =====

@router.post("/suggest-department", response_model=DepartmentSuggestionResponse)
async def suggest_department(
    request: DepartmentSuggestionRequest,
    constituency_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered department suggestions based on complaint content."""
    suggestion_service = DepartmentSuggestionService(db)
    
    suggestions = await suggestion_service.suggest_departments(
        title=request.title,
        description=request.description,
        constituency_id=constituency_id,
        category=request.category,
        location_description=request.location_description
    )
    
    return DepartmentSuggestionResponse(
        suggestions=suggestions,
        constituency_id=constituency_id
    )


# ===== Complaint Clustering =====

@router.get("/constituencies/{constituency_id}/clusters")
async def find_complaint_clusters(
    constituency_id: UUID,
    category: Optional[str] = None,
    min_cluster_size: int = 3,
    max_radius_meters: int = 500,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find clusters of nearby complaints for batch resolution."""
    clustering_service = ClusteringService(db)
    
    clusters = await clustering_service.find_complaint_clusters(
        constituency_id=constituency_id,
        category=category,
        min_cluster_size=min_cluster_size,
        max_radius_meters=max_radius_meters
    )
    
    # Convert clusters to dict format
    cluster_dicts = [
        {
            "cluster_id": cluster.cluster_id,
            "category": cluster.category,
            "complaint_ids": cluster.complaint_ids,
            "center_lat": cluster.center_lat,
            "center_lng": cluster.center_lng,
            "radius_meters": cluster.radius_meters,
            "estimated_cost_individual": cluster.estimated_cost_individual,
            "estimated_cost_batch": cluster.estimated_cost_batch,
            "savings_percentage": cluster.savings_percentage,
            "complaint_count": cluster.complaint_count,
            "location_description": cluster.location_description
        }
        for cluster in clusters
    ]
    
    return {
        "constituency_id": constituency_id,
        "clusters": cluster_dicts,
        "total_clusters": len(clusters),
        "total_complaints_clustered": sum(c.complaint_count for c in clusters),
        "total_potential_savings": sum(c.estimated_cost_individual - c.estimated_cost_batch for c in clusters)
    }


@router.get("/clusters/{cluster_id}/batch-project")
async def suggest_batch_project(
    cluster_id: str,
    constituency_id: UUID,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a batch project suggestion for a complaint cluster."""
    clustering_service = ClusteringService(db)
    
    # First find the clusters to get the matching one
    clusters = await clustering_service.find_complaint_clusters(
        constituency_id=constituency_id,
        category=category
    )
    
    # Find the requested cluster
    target_cluster = None
    for cluster in clusters:
        if cluster.cluster_id == cluster_id:
            target_cluster = cluster
            break
    
    if not target_cluster:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found")
    
    # Generate project suggestion
    project = await clustering_service.suggest_batch_project(target_cluster)
    
    return project


# ===== Predictive Planning =====

@router.get("/constituencies/{constituency_id}/seasonal-forecast")
async def get_seasonal_forecast(
    constituency_id: UUID,
    months_ahead: int = 3,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get seasonal complaint predictions for planning."""
    planning_service = PredictivePlanningService(db)
    
    predictions = await planning_service.predict_seasonal_trends(
        constituency_id=constituency_id,
        months_ahead=months_ahead
    )
    
    return {
        "constituency_id": constituency_id,
        "forecast_period": f"Next {months_ahead} months",
        "predictions": predictions
    }


@router.get("/constituencies/{constituency_id}/budget-forecast")
async def get_budget_forecast(
    constituency_id: UUID,
    months_ahead: int = 6,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Forecast budget requirements based on predicted complaints."""
    planning_service = PredictivePlanningService(db)
    
    forecast = await planning_service.forecast_budget_needs(
        constituency_id=constituency_id,
        months_ahead=months_ahead
    )
    
    return forecast


@router.get("/constituencies/{constituency_id}/proactive-maintenance")
async def suggest_proactive_maintenance(
    constituency_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proactive maintenance suggestions to prevent recurring issues."""
    planning_service = PredictivePlanningService(db)
    
    suggestions = await planning_service.suggest_proactive_maintenance(
        constituency_id=constituency_id
    )
    
    return {
        "constituency_id": constituency_id,
        "suggestions": suggestions,
        "total_suggestions": len(suggestions)
    }


@router.post("/analyze-complaint-text")
async def analyze_complaint_text(
    title: str,
    description: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze complaint text in Kannada/English with NLP.
    Handles poor spelling and mixed languages.
    """
    planning_service = PredictivePlanningService(db)
    
    analysis = await planning_service.analyze_complaint_with_nlp(
        title=title,
        description=description
    )
    
    return analysis
