"""Complaint management endpoints with authentication and workflow enforcement."""
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Query as SAQuery, Session

from app.core.auth import get_user_constituency_id, require_auth
from app.core.database import get_db
from app.core.workflow import WorkflowError, WorkflowValidator, validate_status_transition
from app.core.notifications import ComplaintNotifications
from app.core.webhooks import dispatch_event
from app.models.complaint import Complaint, ComplaintPriority, ComplaintStatus, Media, MediaType, StatusLog
from app.models.department import Department
from app.models.user import User, UserRole
from app.models.ward import Ward
from app.models.panchayat import GramPanchayat
from app.services.complaint_routing import (
    escalate_to_taluk_panchayat,
    escalate_to_zilla_panchayat,
    transfer_to_department,
    reassign_to_gram_panchayat,
)
from app.schemas.complaint import (
    ComplaintAssign,
    ComplaintCreate,
    ComplaintAdvancedAnalytics,
    ComplaintListResponse,
    ComplaintResponse,
    ComplaintUpdate,
    ComplaintTrendPoint,
    ComplaintStatusUpdate,
    DepartmentBacklog,
    PriorityCount,
    StatusCount,
)
from app.schemas.media import MediaCreate, MediaResponse
from app.schemas.workflow import WorkApproval, WorkRejection, WorkflowStatusResponse
from app.schemas.panchayat_escalation import (
    EscalationRequest,
    TransferRequest,
    ReassignRequest,
    EscalationResponse,
)
from app.schemas.ward_workflow import (
    WardAssignToDepartmentRequest,
    AddPublicNoteRequest,
    AddInternalNoteRequest,
    WardAssignmentResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(tz=timezone.utc)


def _ensure_constituency_access(complaint: Complaint, current_user: User) -> None:
    """Verify the user can access the complaint's constituency."""
    if current_user.role == UserRole.ADMIN:
        return
    if complaint.constituency_id != current_user.constituency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only operate on complaints from your constituency",
        )


def _resolve_constituency(current_user: User, requested_constituency: Optional[UUID]) -> UUID:
    """Determine the constituency for a new complaint."""
    if current_user.role == UserRole.ADMIN:
        if requested_constituency:
            return requested_constituency
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin must provide constituency_id when filing complaints",
        )
    if not current_user.constituency_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to any constituency",
        )
    if requested_constituency and requested_constituency != current_user.constituency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create complaints for other constituencies",
        )
    return current_user.constituency_id


def _validate_ward(
    db: Session,
    *,
    constituency_id: UUID,
    ward_id: Optional[UUID],
) -> Optional[UUID]:
    """Ensure ward exists and belongs to the constituency."""
    if not ward_id:
        return None
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ward not found")
    if ward.constituency_id != constituency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ward belongs to a different constituency",
        )
    return ward.id


def _resolve_priority(priority: Optional[str]) -> ComplaintPriority:
    """Convert incoming priority string into ComplaintPriority enum."""
    if not priority:
        return ComplaintPriority.MEDIUM
    try:
        return ComplaintPriority(priority)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid priority") from exc


def _ensure_owner_or_admin(complaint: Complaint, user: User) -> None:
    """Ensure the actor owns the complaint or has elevated privileges."""

    if user.role in (UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR):
        return
    if complaint.user_id == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot modify this complaint")


def _ensure_media_permissions(complaint: Complaint, user: User) -> None:
    """Validate that the actor can manage complaint media."""

    if user.role in (UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR):
        return
    if complaint.user_id == user.id:
        return
    if user.role == UserRole.DEPARTMENT_OFFICER and complaint.assigned_to == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot manage media for this complaint")


def _serialize_complaint(complaint: Complaint) -> Dict[str, Any]:
    """Serialize a complaint for webhook dispatch."""

    return ComplaintResponse.model_validate(complaint).model_dump(mode="json")


def _status_to_str(status: Optional[Union[ComplaintStatus, str]]) -> Optional[str]:
    if status is None:
        return None
    if isinstance(status, ComplaintStatus):
        return status.value
    return str(status)


def _resolve_media_type(raw: str) -> MediaType:
    try:
        return MediaType(raw.lower())
    except ValueError as exc:
        allowed = ", ".join(item.value for item in MediaType)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid media_type. Allowed: {allowed}") from exc


def _avg(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _median(values: List[float]) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 0:
        return round((ordered[mid - 1] + ordered[mid]) / 2, 2)
    return round(ordered[mid], 2)


SLA_TARGET_HOURS: Dict[ComplaintPriority, float] = {
    ComplaintPriority.URGENT: 24.0,
    ComplaintPriority.HIGH: 72.0,
    ComplaintPriority.MEDIUM: 168.0,
    ComplaintPriority.LOW: 336.0,
}


def _validate_department(
    db: Session,
    *,
    constituency_id: UUID,
    dept_id: UUID,
) -> Department:
    department = db.query(Department).filter(Department.id == dept_id).first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    if department.constituency_id != constituency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Department belongs to a different constituency",
        )
    return department


def _validate_assignee(
    db: Session,
    *,
    constituency_id: UUID,
    assigned_to: Optional[UUID],
) -> Optional[UUID]:
    if not assigned_to:
        return None
    user = db.query(User).filter(User.id == assigned_to).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned officer not found")
    if user.role not in (UserRole.DEPARTMENT_OFFICER, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user must be a department officer or moderator",
        )
    if user.constituency_id != constituency_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assigned officer belongs to a different constituency",
        )
    return user.id


def _add_status_log(
    db: Session,
    *,
    complaint_id: UUID,
    old_status: Optional[ComplaintStatus],
    new_status: ComplaintStatus,
    changed_by: UUID,
    note: Optional[str],
) -> None:
    db.add(
        StatusLog(
            complaint_id=complaint_id,
            old_status=old_status.value if old_status else None,
            new_status=new_status.value,
            changed_by=changed_by,
            note=note,
            timestamp=_utcnow(),
        )
    )


def _paginate(query: SAQuery[Complaint], *, page: int, page_size: int) -> List[Complaint]:
    return (
        query.order_by(Complaint.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    payload: ComplaintCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    constituency_id = _resolve_constituency(current_user, payload.constituency_id)
    ward_id = _validate_ward(db, constituency_id=constituency_id, ward_id=payload.ward_id)
    priority = _resolve_priority(payload.priority)

    # Analyze complaint text with NLP (supports Kannada + poor English)
    # Note: Using multilingual normalizer for category detection
    from app.services.predictive_planning_service import MultilingualNormalizer
    normalizer = MultilingualNormalizer()
    
    # Normalize text and detect category
    combined_text = f"{payload.title} {payload.description}"
    detected_category = normalizer.detect_category(combined_text)
    
    # Use detected category if none provided, or fall back to 'other'
    category = payload.category or detected_category or "other"
    
    # NEW FLOW: All complaints go to WARD first
    # Ward officers will then assign to appropriate departments
    # No direct GP/TP/ZP/Department assignment from citizens

    complaint = Complaint(
        constituency_id=constituency_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        category=category,
        priority=priority,
        lat=payload.lat,
        lng=payload.lng,
        ward_id=ward_id,
        location_description=payload.location_description,
        voice_transcript=payload.voice_transcript,
        status=ComplaintStatus.SUBMITTED,
        # NEW: Always assign to ward initially
        assignment_type="ward",
        # These will be set later by ward officer
        dept_id=None,
        assigned_to=None,
        ward_officer_id=None,
        # Keep panchayat IDs null (legacy fields)
        gram_panchayat_id=None,
        taluk_panchayat_id=None,
        zilla_panchayat_id=None,
        citizen_selected_dept=False,
        created_at=_utcnow(),
        updated_at=_utcnow(),
        last_activity_at=_utcnow(),
    )

    db.add(complaint)
    db.flush()  # ensure ID for logs

    # Calculate priority score (using simple scoring for now - async service needs async session)
    # For immediate use, set basic priority data
    if complaint.lat and complaint.lng:
        # Simple emergency detection from keywords
        desc_lower = complaint.description.lower()
        emergency_keywords = ["emergency", "urgent", "immediately", "bega", "sikkantu", "danger", "critical"]
        complaint.is_emergency = any(keyword in desc_lower for keyword in emergency_keywords)
        
        # Simple population estimate
        impact_keywords = ["entire", "whole", "all", "many", "multiple", "area"]
        affected_pop = 10 if any(kw in desc_lower for kw in impact_keywords) else 1
        complaint.affected_population_estimate = affected_pop
        
        # Simple priority score based on emergency + impact
        if complaint.is_emergency:
            complaint.priority_score = 0.9
        elif affected_pop > 5:
            complaint.priority_score = 0.7
        else:
            complaint.priority_score = 0.5

    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=None,
        new_status=ComplaintStatus.SUBMITTED,
        changed_by=current_user.id,
        note="Complaint submitted",
    )

    db.commit()
    db.refresh(complaint)
    await ComplaintNotifications.notify_complaint_created(complaint, current_user)  # type: ignore[func-returns-value]
    await dispatch_event("complaint.created", _serialize_complaint(complaint))
    return complaint


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint_details(
    complaint_id: UUID,
    payload: ComplaintUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)
    _ensure_owner_or_admin(complaint, current_user)

    if (
        current_user.role == UserRole.CITIZEN
        and complaint.status not in (ComplaintStatus.SUBMITTED, ComplaintStatus.REJECTED)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint cannot be edited after processing begins",
        )

    changes: Dict[str, Any] = {}

    if payload.title is not None and payload.title != complaint.title:
        complaint.title = payload.title
        changes["title"] = payload.title
    if payload.description is not None and payload.description != complaint.description:
        complaint.description = payload.description
        changes["description"] = payload.description
    if payload.category is not None and payload.category != complaint.category:
        complaint.category = payload.category
        changes["category"] = payload.category
    if payload.priority is not None:
        priority = _resolve_priority(payload.priority)
        if priority != complaint.priority:
            complaint.priority = priority
            changes["priority"] = priority.value

    if not changes:
        return complaint

    complaint.updated_at = _utcnow()

    db.commit()
    db.refresh(complaint)
    await dispatch_event(
        "complaint.updated",
        {"complaint": _serialize_complaint(complaint), "changes": changes},
    )
    return complaint


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)
    _ensure_owner_or_admin(complaint, current_user)

    if complaint.status not in (ComplaintStatus.SUBMITTED, ComplaintStatus.REJECTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only complaints that are not in progress can be deleted",
        )

    db.query(Media).filter(Media.complaint_id == complaint.id).delete(synchronize_session=False)
    db.query(StatusLog).filter(StatusLog.complaint_id == complaint.id).delete(synchronize_session=False)
    db.delete(complaint)
    db.commit()

    await dispatch_event("complaint.deleted", {"complaint_id": str(complaint_id)})
    return None


@router.post("/{complaint_id}/media", response_model=List[MediaResponse], status_code=status.HTTP_201_CREATED)
async def add_complaint_media(
    complaint_id: UUID,
    payload: List[MediaCreate],
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one media item is required")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)
    _ensure_media_permissions(complaint, current_user)

    created_media: List[Media] = []
    for item in payload:
        media_record = Media(
            complaint_id=complaint.id,
            url=item.url,
            media_type=_resolve_media_type(item.media_type),
            caption=item.caption,
            proof_type=item.proof_type,
            photo_type=item.photo_type,
            file_size=item.file_size,
            lat=item.lat,
            lng=item.lng,
            uploaded_at=_utcnow(),
            uploaded_by=current_user.id,
        )
        db.add(media_record)
        created_media.append(media_record)

    db.commit()
    for record in created_media:
        db.refresh(record)

    await dispatch_event(
        "complaint.media.attached",
        {
            "complaint_id": str(complaint.id),
            "media_ids": [str(record.id) for record in created_media],
        },
    )
    return created_media


@router.get("/{complaint_id}/media", response_model=List[MediaResponse])
async def list_complaint_media(
    complaint_id: UUID,
    media_type: Optional[str] = None,
    photo_type: Optional[str] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)
    _ensure_media_permissions(complaint, current_user)

    query = db.query(Media).filter(Media.complaint_id == complaint.id)

    if media_type:
        query = query.filter(Media.media_type == _resolve_media_type(media_type))
    if photo_type:
        query = query.filter(Media.photo_type == photo_type)

    media_items = query.order_by(Media.uploaded_at.asc()).all()
    return media_items


@router.delete("/{complaint_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint_media(
    complaint_id: UUID,
    media_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)
    _ensure_media_permissions(complaint, current_user)

    media_entry = db.query(Media).filter(Media.id == media_id, Media.complaint_id == complaint.id).first()
    if not media_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    if current_user.role == UserRole.CITIZEN and media_entry.uploaded_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only remove media you uploaded")

    db.delete(media_entry)
    db.commit()

    await dispatch_event(
        "complaint.media.deleted",
        {"complaint_id": str(complaint.id), "media_id": str(media_id)},
    )
    return None


@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    ward_id: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    query: SAQuery[Complaint] = db.query(Complaint)

    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)

    if status_filter:
        try:
            status_enum = ComplaintStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status") from exc
        query = query.filter(Complaint.status == status_enum)
    if category:
        query = query.filter(Complaint.category == category)
    if ward_id:
        try:
            query = query.filter(Complaint.ward_id == UUID(ward_id))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ward_id") from exc
    if search:
        like = f"%{search}%"
        query = query.filter(
            Complaint.title.ilike(like)
            | Complaint.description.ilike(like)
            | Complaint.location_description.ilike(like)
        )
    if date_from:
        query = query.filter(Complaint.created_at >= date_from)
    if date_to:
        query = query.filter(Complaint.created_at <= date_to)

    total = query.count()
    complaints = _paginate(query, page=page, page_size=page_size)
    complaint_payloads = [ComplaintResponse.model_validate(item) for item in complaints]

    return ComplaintListResponse(
        total=total,
        page=page,
        page_size=page_size,
        complaints=complaint_payloads,
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)
    return complaint


@router.post("/{complaint_id}/assign", response_model=ComplaintResponse)
async def assign_complaint(
    complaint_id: UUID,
    payload: ComplaintAssign,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)

    department = _validate_department(
        db,
        constituency_id=complaint.constituency_id,
        dept_id=payload.dept_id,
    )
    assignee_id = _validate_assignee(
        db,
        constituency_id=complaint.constituency_id,
        assigned_to=payload.assigned_to,
    )

    old_status = complaint.status
    complaint.dept_id = department.id
    complaint.assigned_to = assignee_id
    complaint.status = ComplaintStatus.ASSIGNED
    complaint.updated_at = _utcnow()

    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=ComplaintStatus.ASSIGNED,
        changed_by=current_user.id,
        note=payload.note or "Complaint assigned to department",
    )

    officer = None
    if assignee_id:
        officer = db.query(User).filter(User.id == assignee_id).first()

    db.commit()
    db.refresh(complaint)
    await ComplaintNotifications.notify_complaint_assigned(complaint, department, officer)  # type: ignore[func-returns-value]
    await dispatch_event(
        "complaint.assigned",
        {
            "complaint": _serialize_complaint(complaint),
            "dept_id": str(department.id),
            "assigned_to": str(assignee_id) if assignee_id else None,
        },
    )
    return complaint


@router.post("/{complaint_id}/sub-assign", response_model=ComplaintResponse)
async def sub_assign_complaint(
    complaint_id: UUID,
    payload: ComplaintAssign,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Allow department officers to sub-assign complaints to other officers."""
    if current_user.role not in (UserRole.DEPARTMENT_OFFICER, UserRole.MODERATOR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)

    # Check if the complaint is assigned to this officer
    if complaint.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only sub-assign complaints that are assigned to you"
        )

    # Validate the new assignee
    new_assignee_id = _validate_assignee(
        db,
        constituency_id=complaint.constituency_id,
        assigned_to=payload.assigned_to,
    )

    if new_assignee_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot sub-assign to yourself"
        )

    old_status = complaint.status
    complaint.assigned_to = new_assignee_id
    complaint.updated_at = _utcnow()

    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=old_status,  # Status doesn't change, just reassignment
        changed_by=current_user.id,
        note=payload.note or f"Sub-assigned by {current_user.name}",
    )

    new_assignee = None
    if new_assignee_id:
        new_assignee = db.query(User).filter(User.id == new_assignee_id).first()

    db.commit()
    db.refresh(complaint)

    # Notify the new assignee
    if new_assignee:
        await ComplaintNotifications.notify_complaint_assigned(
            complaint,
            db.query(Department).filter(Department.id == complaint.dept_id).first() if complaint.dept_id else None,
            new_assignee
        )  # type: ignore[func-returns-value]

    await dispatch_event(
        "complaint.sub_assigned",
        {
            "complaint": _serialize_complaint(complaint),
            "sub_assigned_by": str(current_user.id),
            "new_assignee": str(new_assignee_id) if new_assignee_id else None,
        },
    )
    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: UUID,
    payload: ComplaintStatusUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)

    old_status = complaint.status
    try:
        new_status = ComplaintStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status") from exc

    try:
        validate_status_transition(old_status.value, new_status.value, current_user.role.value)
    except WorkflowError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    complaint.status = new_status
    complaint.updated_at = _utcnow()

    if new_status is ComplaintStatus.RESOLVED:
        complaint.resolved_at = _utcnow()
    elif new_status is ComplaintStatus.CLOSED:
        complaint.closed_at = _utcnow()

    auto_note = WorkflowValidator().get_transition_reason(old_status.value, new_status.value)
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        note=payload.note or auto_note,
    )

    db.commit()
    db.refresh(complaint)
    citizen = current_user if complaint.user_id == current_user.id else db.query(User).filter(User.id == complaint.user_id).first()
    await ComplaintNotifications.notify_status_changed(  # type: ignore[func-returns-value]
        complaint,
        old_status.value,
        new_status.value,
        citizen,
    )
    await dispatch_event(
        "complaint.status_changed",
        {
            "complaint": _serialize_complaint(complaint),
            "old_status": old_status.value,
            "new_status": new_status.value,
        },
    )
    return complaint


@router.post("/{complaint_id}/approve", response_model=ComplaintResponse)
async def approve_work_completion(
    complaint_id: UUID,
    payload: WorkApproval,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)

    if complaint.status != ComplaintStatus.RESOLVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complaint must be resolved first")

    complaint.work_approved = True
    complaint.approval_comments = payload.comments
    complaint.approved_at = _utcnow()
    complaint.approved_by = current_user.id
    complaint.status = ComplaintStatus.CLOSED
    complaint.closed_at = _utcnow()
    complaint.updated_at = _utcnow()

    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=ComplaintStatus.RESOLVED,
        new_status=ComplaintStatus.CLOSED,
        changed_by=current_user.id,
        note=payload.comments or "Work approved and complaint closed",
    )

    db.commit()
    db.refresh(complaint)
    citizen = current_user if complaint.user_id == current_user.id else db.query(User).filter(User.id == complaint.user_id).first()
    await ComplaintNotifications.notify_work_approved(complaint, citizen)  # type: ignore[func-returns-value]
    await ComplaintNotifications.notify_status_changed(  # type: ignore[func-returns-value]
        complaint,
        ComplaintStatus.RESOLVED.value,
        ComplaintStatus.CLOSED.value,
        citizen,
    )
    await dispatch_event(
        "complaint.approved",
        {
            "complaint": _serialize_complaint(complaint),
            "approved_by": str(current_user.id),
        },
    )
    return complaint


@router.post("/{complaint_id}/reject", response_model=ComplaintResponse)
async def reject_work_completion(
    complaint_id: UUID,
    payload: WorkRejection,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)

    if complaint.status != ComplaintStatus.RESOLVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only resolved complaints can be rejected")

    complaint.work_approved = False
    complaint.rejection_reason = payload.reason
    complaint.rejected_at = _utcnow()
    complaint.rejected_by = current_user.id
    complaint.status = ComplaintStatus.IN_PROGRESS
    complaint.resolved_at = None
    complaint.updated_at = _utcnow()

    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=ComplaintStatus.RESOLVED,
        new_status=ComplaintStatus.IN_PROGRESS,
        changed_by=current_user.id,
        note=f"Work rejected: {payload.reason}",
    )

    db.commit()
    db.refresh(complaint)
    assigned_officer = None
    if complaint.assigned_to:
        assigned_officer = db.query(User).filter(User.id == complaint.assigned_to).first()
    await ComplaintNotifications.notify_work_rejected(complaint, payload.reason, assigned_officer)  # type: ignore[func-returns-value]
    citizen = current_user if complaint.user_id == current_user.id else db.query(User).filter(User.id == complaint.user_id).first()
    await ComplaintNotifications.notify_status_changed(  # type: ignore[func-returns-value]
        complaint,
        ComplaintStatus.RESOLVED.value,
        ComplaintStatus.IN_PROGRESS.value,
        citizen,
    )
    await dispatch_event(
        "complaint.rejected",
        {
            "complaint": _serialize_complaint(complaint),
            "reason": payload.reason,
            "rejected_by": str(current_user.id),
        },
    )
    return complaint


@router.get("/{complaint_id}/workflow", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    complaint_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    _ensure_constituency_access(complaint, current_user)

    validator = WorkflowValidator()
    allowed_for_user: List[str] = [
        status
        for status in validator.get_allowed_transitions(complaint.status.value)
    if validator.can_user_transition(complaint.status.value, status, current_user.role.value)
    ]

    return WorkflowStatusResponse(
        current_status=complaint.status.value,
        allowed_transitions=allowed_for_user,
        requires_approval=validator.requires_work_approval(complaint.status.value),
        can_reopen=validator.can_reopen(complaint.status.value),
        is_terminal=validator.is_terminal_status(complaint.status.value),
    )


@router.get("/stats/summary")
async def get_complaint_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total = db.query(Complaint).count()
    submitted = db.query(Complaint).filter(Complaint.status == ComplaintStatus.SUBMITTED).count()
    assigned = db.query(Complaint).filter(Complaint.status == ComplaintStatus.ASSIGNED).count()
    in_progress = db.query(Complaint).filter(Complaint.status == ComplaintStatus.IN_PROGRESS).count()
    resolved = db.query(Complaint).filter(Complaint.status == ComplaintStatus.RESOLVED).count()
    closed = db.query(Complaint).filter(Complaint.status == ComplaintStatus.CLOSED).count()

    approved = db.query(Complaint).filter(Complaint.work_approved.is_(True)).count()
    rejected = db.query(Complaint).filter(Complaint.work_approved.is_(False)).count()
    pending = db.query(Complaint).filter(
        Complaint.status == ComplaintStatus.RESOLVED,
        Complaint.work_approved.is_(None),
    ).count()

    return {
        "total": total,
        "by_status": {
            "submitted": submitted,
            "assigned": assigned,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed,
        },
        "work_completion": {
            "approved": approved,
            "rejected": rejected,
            "pending_approval": pending,
        },
        "resolution_rate": round((resolved + closed) / total * 100, 2) if total else 0,
        "approval_rate": round((approved / resolved * 100), 2) if resolved else 0,
    }


STATUS_ORDER: Dict[str, int] = {
    ComplaintStatus.SUBMITTED.value: 0,
    ComplaintStatus.ASSIGNED.value: 1,
    ComplaintStatus.IN_PROGRESS.value: 2,
    ComplaintStatus.RESOLVED.value: 3,
    ComplaintStatus.CLOSED.value: 4,
    ComplaintStatus.REJECTED.value: 5,
}

PRIORITY_ORDER: Dict[str, int] = {
    ComplaintPriority.URGENT.value: 0,
    ComplaintPriority.HIGH.value: 1,
    ComplaintPriority.MEDIUM.value: 2,
    ComplaintPriority.LOW.value: 3,
}


@router.get("/stats/advanced", response_model=ComplaintAdvancedAnalytics)
async def get_advanced_complaint_stats(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db),
) -> ComplaintAdvancedAnalytics:
    complaint_query = db.query(Complaint)
    if constituency_filter:
        complaint_query = complaint_query.filter(Complaint.constituency_id == constituency_filter)

    complaints = complaint_query.all()

    status_counter: Dict[str, int] = {}
    priority_counter: Dict[str, int] = {}
    resolution_durations: List[float] = []
    total_resolution_breaches = 0
    open_statuses = {ComplaintStatus.SUBMITTED, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS}

    department_rollups: Dict[UUID, Dict[str, Any]] = {}

    for complaint in complaints:
        status_value = _status_to_str(complaint.status) or "unknown"
        status_counter[status_value] = status_counter.get(status_value, 0) + 1

        priority_value = complaint.priority.value
        priority_counter[priority_value] = priority_counter.get(priority_value, 0) + 1

        sla_target = SLA_TARGET_HOURS.get(complaint.priority, 168.0)

        if complaint.resolved_at:
            duration_hours = (complaint.resolved_at - complaint.created_at).total_seconds() / 3600
            resolution_durations.append(duration_hours)
            if duration_hours > sla_target:
                total_resolution_breaches += 1

        if complaint.dept_id:
            rollup = department_rollups.setdefault(
                complaint.dept_id,
                {"open": 0, "resolved_hours": [], "resolved_total": 0, "sla_breaches": 0},
            )

            if complaint.status in open_statuses:
                rollup["open"] += 1

            if complaint.resolved_at:
                duration_hours = (complaint.resolved_at - complaint.created_at).total_seconds() / 3600
                rollup["resolved_hours"].append(duration_hours)
                rollup["resolved_total"] += 1
                if duration_hours > sla_target:
                    rollup["sla_breaches"] += 1

    department_backlog: List[DepartmentBacklog] = []
    if department_rollups:
        departments = {
            dept.id: dept
            for dept in db.query(Department).filter(Department.id.in_(department_rollups.keys())).all()
        }
        for dept_id, stats in department_rollups.items():
            department = departments.get(dept_id)
            if not department:
                continue
            breach_rate = (
                round(stats["sla_breaches"] / stats["resolved_total"] * 100, 2)
                if stats["resolved_total"]
                else None
            )
            department_backlog.append(
                DepartmentBacklog(
                    department_id=department.id,
                    department_name=department.name,
                    open_complaints=stats["open"],
                    avg_resolution_hours=_avg(stats["resolved_hours"]),
                    sla_breach_rate=breach_rate,
                )
            )

    department_backlog.sort(key=lambda item: item.open_complaints, reverse=True)

    open_complaints = sum(1 for complaint in complaints if complaint.status in open_statuses)
    resolved_count = sum(
        1
        for complaint in complaints
        if complaint.status in (ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED)
    )

    resolution_metrics: Dict[str, Optional[float]] = {
        "avg_resolution_hours": _avg(resolution_durations),
        "median_resolution_hours": _median(resolution_durations),
        "sla_breach_rate": (
            round(total_resolution_breaches / len(resolution_durations) * 100, 2)
            if resolution_durations
            else None
        ),
        "open_complaints": float(open_complaints),
        "resolution_rate": (
            round(resolved_count / len(complaints) * 100, 2) if complaints else 0.0
        ),
    }

    window_start = (_utcnow() - timedelta(days=6)).date()
    trend_window = {
        (window_start + timedelta(days=offset)): {"new": 0, "resolved": 0}
        for offset in range(7)
    }

    for complaint in complaints:
        created_day = complaint.created_at.date()
        if created_day in trend_window:
            trend_window[created_day]["new"] += 1
        if complaint.resolved_at:
            resolved_day = complaint.resolved_at.date()
            if resolved_day in trend_window:
                trend_window[resolved_day]["resolved"] += 1

    recent_trend = [
        ComplaintTrendPoint(date=day, new=counts["new"], resolved=counts["resolved"])
        for day, counts in sorted(trend_window.items())
    ]

    status_totals = [
        StatusCount(status=key, count=value)
        for key, value in sorted(
            status_counter.items(), key=lambda item: STATUS_ORDER.get(item[0], 99)
        )
    ]

    priority_totals = [
        PriorityCount(priority=key, count=value)
        for key, value in sorted(
            priority_counter.items(), key=lambda item: PRIORITY_ORDER.get(item[0], 99)
        )
    ]

    return ComplaintAdvancedAnalytics(
        status_totals=status_totals,
        priority_totals=priority_totals,
        department_backlog=department_backlog,
        resolution_metrics=resolution_metrics,
        recent_trend=recent_trend,
    )


@router.get("/my-assigned", response_model=ComplaintListResponse)
async def get_my_assigned_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    """
    Get complaints assigned to the current department officer.
    
    NOTE: This shows individual assignments. For department heads to see 
    all complaints in their department, use GET /my-department
    """
    if current_user.role not in (UserRole.DEPARTMENT_OFFICER, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for department officers and moderators"
        )

    query: SAQuery[Complaint] = db.query(Complaint).filter(Complaint.assigned_to == current_user.id)

    if status_filter:
        try:
            status_enum = ComplaintStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status") from exc
        query = query.filter(Complaint.status == status_enum)
    if category:
        query = query.filter(Complaint.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Complaint.title.ilike(like)
            | Complaint.description.ilike(like)
            | Complaint.location_description.ilike(like)
        )

    total = query.count()
    complaints = _paginate(query, page=page, page_size=page_size)
    complaint_payloads = [ComplaintResponse.model_validate(item) for item in complaints]

    return ComplaintListResponse(
        total=total,
        page=page,
        page_size=page_size,
        complaints=complaint_payloads,
    )


@router.get("/my-department", response_model=ComplaintListResponse)
async def get_my_department_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    """
    Get all complaints assigned to current user's department.
    
    For department heads/officers to see all complaints in their jurisdiction,
    not just individually assigned ones.
    
    JURISDICTION: Only shows complaints from wards in the same GP/TP/Corporation
    Example: Puttur PWD officer only sees complaints from Puttur TP wards
    """
    if current_user.role not in (UserRole.DEPARTMENT_OFFICER, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for department officers and moderators"
        )
    
    if not current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no department assignment"
        )
    
    # Get department to verify jurisdiction
    dept = db.query(Department).filter(Department.id == current_user.department_id).first()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    
    # Query complaints assigned to this department
    query: SAQuery[Complaint] = db.query(Complaint).filter(
        Complaint.assignment_type == "department",
        Complaint.dept_id == current_user.department_id
    )
    
    # Additional filters
    if status_filter:
        try:
            status_enum = ComplaintStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status") from exc
        query = query.filter(Complaint.status == status_enum)
    if category:
        query = query.filter(Complaint.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Complaint.title.ilike(like)
            | Complaint.description.ilike(like)
            | Complaint.location_description.ilike(like)
        )
    
    total = query.count()
    complaints = _paginate(query, page=page, page_size=page_size)
    complaint_payloads = [ComplaintResponse.model_validate(item) for item in complaints]
    
    return ComplaintListResponse(
        total=total,
        page=page,
        page_size=page_size,
        complaints=complaint_payloads,
    )


@router.get("/my-panchayat", response_model=ComplaintListResponse)
async def get_my_panchayat_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    """Get complaints assigned to the current panchayat officer's jurisdiction."""
    
    # Check if user is a panchayat officer
    panchayat_roles = [
        UserRole.PDO, UserRole.VILLAGE_ACCOUNTANT, UserRole.GP_PRESIDENT,
        UserRole.TALUK_PANCHAYAT_OFFICER, UserRole.TP_PRESIDENT,
        UserRole.ZILLA_PANCHAYAT_OFFICER, UserRole.ZP_PRESIDENT
    ]
    if current_user.role not in panchayat_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for panchayat officials"
        )

    query: SAQuery[Complaint] = db.query(Complaint)
    
    # Filter based on panchayat level
    if current_user.role in [UserRole.PDO, UserRole.VILLAGE_ACCOUNTANT, UserRole.GP_PRESIDENT]:
        # GP-level officers: see complaints assigned to their GP
        if not current_user.gram_panchayat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no Gram Panchayat assignment"
            )
        query = query.filter(
            Complaint.assignment_type == "gram_panchayat",
            Complaint.gram_panchayat_id == current_user.gram_panchayat_id
        )
    
    elif current_user.role in [UserRole.TALUK_PANCHAYAT_OFFICER, UserRole.TP_PRESIDENT]:
        # TP-level officers: see complaints assigned to their TP + all child GPs
        if not current_user.taluk_panchayat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no Taluk Panchayat assignment"
            )
        
        # Get all GPs under this TP
        from sqlalchemy import or_
        child_gps = db.query(GramPanchayat).filter(
            GramPanchayat.taluk_panchayat_id == current_user.taluk_panchayat_id
        ).all()
        child_gp_ids = [gp.id for gp in child_gps]
        
        query = query.filter(
            or_(
                # Complaints directly assigned to this TP
                (Complaint.assignment_type == "taluk_panchayat") & 
                (Complaint.taluk_panchayat_id == current_user.taluk_panchayat_id),
                # Complaints assigned to child GPs
                (Complaint.assignment_type == "gram_panchayat") & 
                (Complaint.gram_panchayat_id.in_(child_gp_ids))
            )
        )
    
    elif current_user.role in [UserRole.ZILLA_PANCHAYAT_OFFICER, UserRole.ZP_PRESIDENT]:
        # ZP-level officers: see complaints assigned to their ZP + all child TPs + all child GPs
        if not current_user.zilla_panchayat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no Zilla Panchayat assignment"
            )
        
        # Get all TPs and GPs under this ZP
        from sqlalchemy import or_
        from app.models.panchayat import TalukPanchayat
        
        child_tps = db.query(TalukPanchayat).filter(
            TalukPanchayat.zilla_panchayat_id == current_user.zilla_panchayat_id
        ).all()
        child_tp_ids = [tp.id for tp in child_tps]
        
        child_gps = db.query(GramPanchayat).filter(
            GramPanchayat.taluk_panchayat_id.in_(child_tp_ids)
        ).all()
        child_gp_ids = [gp.id for gp in child_gps]
        
        query = query.filter(
            or_(
                # Complaints directly assigned to this ZP
                (Complaint.assignment_type == "zilla_panchayat") & 
                (Complaint.zilla_panchayat_id == current_user.zilla_panchayat_id),
                # Complaints assigned to child TPs
                (Complaint.assignment_type == "taluk_panchayat") & 
                (Complaint.taluk_panchayat_id.in_(child_tp_ids)),
                # Complaints assigned to child GPs
                (Complaint.assignment_type == "gram_panchayat") & 
                (Complaint.gram_panchayat_id.in_(child_gp_ids))
            )
        )
    
    # Apply additional filters
    if status_filter:
        try:
            status_enum = ComplaintStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status") from exc
        query = query.filter(Complaint.status == status_enum)
    if category:
        query = query.filter(Complaint.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Complaint.title.ilike(like)
            | Complaint.description.ilike(like)
            | Complaint.location_description.ilike(like)
        )

    total = query.count()
    complaints = _paginate(query, page=page, page_size=page_size)
    complaint_payloads = [ComplaintResponse.model_validate(item) for item in complaints]

    return ComplaintListResponse(
        total=total,
        page=page,
        page_size=page_size,
        complaints=complaint_payloads,
    )


# ---------------------------------------------------------------------------
# Duplicate Detection
# ---------------------------------------------------------------------------


@router.get("/{complaint_id}/possible-duplicates", response_model=List[ComplaintResponse])
async def find_possible_duplicates(
    complaint_id: UUID,
    max_distance_meters: int = Query(200, ge=50, le=1000),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> List[ComplaintResponse]:
    """Find possible duplicate complaints within a certain radius."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    if not complaint.lat or not complaint.lng:
        return []
    
    # Find nearby complaints with similar category
    from datetime import timedelta
    
    # Calculate distance using simple bounding box
    lat = float(complaint.lat)
    lng = float(complaint.lng)
    
    # Simple bounding box search (roughly 200m at equator = 0.0018 degrees)
    lat_range = max_distance_meters / 111000  # 1 degree latitude ≈ 111km
    lng_range = max_distance_meters / (111000 * 0.9)  # Approximate for mid-latitudes
    
    possible_duplicates = (
        db.query(Complaint)
        .filter(
            Complaint.id != complaint_id,
            Complaint.constituency_id == complaint.constituency_id,
            Complaint.category == complaint.category,
            Complaint.is_duplicate == False,
            Complaint.status.in_([ComplaintStatus.SUBMITTED, ComplaintStatus.ASSIGNED]),
            Complaint.lat.isnot(None),
            Complaint.lng.isnot(None),
            Complaint.lat.between(lat - lat_range, lat + lat_range),
            Complaint.lng.between(lng - lng_range, lng + lng_range),
            # Created within last 30 days
            Complaint.created_at >= datetime.now(tz=timezone.utc) - timedelta(days=30)
        )
        .order_by(Complaint.created_at.desc())
        .limit(10)
        .all()
    )
    
    return [ComplaintResponse.model_validate(item) for item in possible_duplicates]


@router.post("/{complaint_id}/mark-duplicate", response_model=ComplaintResponse)
async def mark_complaint_as_duplicate(
    complaint_id: UUID,
    parent_complaint_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Mark a complaint as duplicate of another complaint."""
    # Check permissions
    if current_user.role not in (UserRole.MODERATOR, UserRole.ADMIN, UserRole.DEPARTMENT_OFFICER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators, officers, and admins can mark duplicates"
        )
    
    # Get both complaints
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    parent_complaint = db.query(Complaint).filter(Complaint.id == parent_complaint_id).first()
    if not parent_complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    _ensure_constituency_access(parent_complaint, current_user)
    
    # Prevent marking as duplicate of itself
    if complaint_id == parent_complaint_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot mark complaint as duplicate of itself"
        )
    
    # Prevent marking already resolved complaints as duplicates
    if complaint.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot mark resolved/closed complaints as duplicates"
        )
    
    # Prevent duplicate chains (parent is already a duplicate)
    if parent_complaint.is_duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot mark as duplicate of another duplicate. Link to the original complaint."
        )
    
    # Mark as duplicate
    complaint.is_duplicate = True
    complaint.parent_complaint_id = parent_complaint_id
    complaint.status = ComplaintStatus.CLOSED
    complaint.updated_at = _utcnow()
    
    # Increment parent's duplicate count
    parent_complaint.duplicate_count = (parent_complaint.duplicate_count or 0) + 1
    
    # Add status log
    note_text = f"Marked as duplicate of complaint #{parent_complaint_id}"
    if reason:
        note_text += f". Reason: {reason}"
    
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=complaint.status,
        new_status=ComplaintStatus.CLOSED,
        changed_by=current_user.id,
        note=note_text,
    )
    
    db.commit()
    db.refresh(complaint)
    
    # Notify citizen
    await ComplaintNotifications.notify_complaint_closed(complaint, current_user)  # type: ignore[func-returns-value]
    await dispatch_event(
        "complaint.marked_duplicate",
        {
            "complaint": _serialize_complaint(complaint),
            "parent_complaint_id": str(parent_complaint_id),
            "marked_by": str(current_user.id)
        }
    )
    
    return ComplaintResponse.model_validate(complaint)


@router.post("/{complaint_id}/unmark-duplicate", response_model=ComplaintResponse)
async def unmark_duplicate(
    complaint_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Unmark a complaint that was incorrectly marked as duplicate."""
    if current_user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators and admins can unmark duplicates"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    if not complaint.is_duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint is not marked as duplicate"
        )
    
    # Get parent to decrement count
    if complaint.parent_complaint_id:
        parent = db.query(Complaint).filter(Complaint.id == complaint.parent_complaint_id).first()
        if parent:
            parent.duplicate_count = max(0, (parent.duplicate_count or 0) - 1)
    
    # Unmark duplicate
    complaint.is_duplicate = False
    complaint.parent_complaint_id = None
    complaint.status = ComplaintStatus.SUBMITTED
    complaint.updated_at = _utcnow()
    
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=ComplaintStatus.CLOSED,
        new_status=ComplaintStatus.SUBMITTED,
        changed_by=current_user.id,
        note="Unmarked as duplicate - reopened",
    )
    
    db.commit()
    db.refresh(complaint)
    
    return ComplaintResponse.model_validate(complaint)


@router.patch("/{complaint_id}/notes")
async def update_complaint_notes(
    complaint_id: UUID,
    internal_notes: Optional[str] = None,
    notes_are_internal: bool = True,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Update internal notes for a complaint.
    Only moderators, department officers, admins, and MLAs can update notes.
    """
    # Role check - only officials can access internal notes
    official_roles = [UserRole.MODERATOR, UserRole.DEPARTMENT_OFFICER, UserRole.ADMIN, UserRole.MLA]
    if current_user.role not in official_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officials can update internal notes"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Update notes
    complaint.internal_notes = internal_notes
    complaint.notes_are_internal = notes_are_internal
    complaint.notes_updated_at = _utcnow()
    complaint.notes_updated_by = str(current_user.id)
    complaint.updated_at = _utcnow()
    
    db.commit()
    db.refresh(complaint)
    
    # Format notes_updated_at safely
    notes_updated_at_value = complaint.notes_updated_at
    notes_updated_at_str: Optional[str] = notes_updated_at_value.isoformat() if notes_updated_at_value is not None else None
    
    return {
        "id": str(complaint.id),
        "internal_notes": complaint.internal_notes,
        "notes_are_internal": complaint.notes_are_internal,
        "notes_updated_at": notes_updated_at_str,
        "notes_updated_by": complaint.notes_updated_by,
        "message": "Notes updated successfully"
    }


# ---------------------------------------------------------------------------
# Panchayat Escalation Endpoints
# ---------------------------------------------------------------------------

@router.post("/{complaint_id}/escalate-to-taluk", response_model=EscalationResponse)
async def escalate_complaint_to_taluk(
    complaint_id: UUID,
    payload: EscalationRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Escalate a GP-level complaint to Taluk Panchayat."""
    
    # Only GP-level officials can escalate to TP
    gp_roles = [UserRole.PDO, UserRole.VILLAGE_ACCOUNTANT, UserRole.GP_PRESIDENT, UserRole.ADMIN]
    if current_user.role not in gp_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Gram Panchayat officials can escalate to Taluk level"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Store old assignment type
    old_assignment_type = complaint.assignment_type
    
    # Perform escalation
    success = escalate_to_taluk_panchayat(db, complaint)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot escalate: complaint is not at Gram Panchayat level or TP not found"
        )
    
    # Log the escalation
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=complaint.status,
        new_status=complaint.status,
        changed_by=current_user.id,
        note=f"Escalated to Taluk Panchayat. {payload.note or ''}",
    )
    
    complaint.updated_at = _utcnow()
    db.commit()
    db.refresh(complaint)
    
    await ComplaintNotifications.notify_complaint_escalated(complaint, current_user, "Taluk Panchayat")  # type: ignore[func-returns-value]
    
    return EscalationResponse(
        success=True,
        message="Complaint escalated to Taluk Panchayat successfully",
        complaint_id=complaint.id,
        old_assignment_type=old_assignment_type,
        new_assignment_type="taluk_panchayat"
    )


@router.post("/{complaint_id}/escalate-to-zilla", response_model=EscalationResponse)
async def escalate_complaint_to_zilla(
    complaint_id: UUID,
    payload: EscalationRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Escalate a TP-level complaint to Zilla Panchayat."""
    
    # Only TP-level officials can escalate to ZP
    tp_roles = [UserRole.TALUK_PANCHAYAT_OFFICER, UserRole.TP_PRESIDENT, UserRole.ADMIN]
    if current_user.role not in tp_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Taluk Panchayat officials can escalate to Zilla level"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Store old assignment type
    old_assignment_type = complaint.assignment_type
    
    # Perform escalation
    success = escalate_to_zilla_panchayat(db, complaint)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot escalate: complaint is not at Taluk Panchayat level or ZP not found"
        )
    
    # Log the escalation
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=complaint.status,
        new_status=complaint.status,
        changed_by=current_user.id,
        note=f"Escalated to Zilla Panchayat. {payload.note or ''}",
    )
    
    complaint.updated_at = _utcnow()
    db.commit()
    db.refresh(complaint)
    
    await ComplaintNotifications.notify_complaint_escalated(complaint, current_user, "Zilla Panchayat")  # type: ignore[func-returns-value]
    
    return EscalationResponse(
        success=True,
        message="Complaint escalated to Zilla Panchayat successfully",
        complaint_id=complaint.id,
        old_assignment_type=old_assignment_type,
        new_assignment_type="zilla_panchayat"
    )


@router.post("/{complaint_id}/transfer-to-department", response_model=EscalationResponse)
async def transfer_complaint_to_department(
    complaint_id: UUID,
    payload: TransferRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Transfer a panchayat-level complaint to a specialized department."""
    
    # Any panchayat official can transfer to department
    panchayat_roles = [
        UserRole.PDO, UserRole.VILLAGE_ACCOUNTANT, UserRole.GP_PRESIDENT,
        UserRole.TALUK_PANCHAYAT_OFFICER, UserRole.TP_PRESIDENT,
        UserRole.ZILLA_PANCHAYAT_OFFICER, UserRole.ZP_PRESIDENT,
        UserRole.ADMIN, UserRole.MODERATOR
    ]
    if current_user.role not in panchayat_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only panchayat officials can transfer complaints to departments"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Store old assignment type
    old_assignment_type = complaint.assignment_type
    
    # Perform transfer
    success = transfer_to_department(db, complaint, payload.dept_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer: department not found"
        )
    
    # Log the transfer
    dept = db.query(Department).filter(Department.id == payload.dept_id).first()
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=complaint.status,
        new_status=complaint.status,
        changed_by=current_user.id,
        note=f"Transferred to {dept.name if dept else 'Department'}. {payload.note or ''}",
    )
    
    complaint.updated_at = _utcnow()
    db.commit()
    db.refresh(complaint)
    
    await ComplaintNotifications.notify_complaint_transferred(complaint, current_user, dept.name if dept else "Department")  # type: ignore[func-returns-value]
    
    return EscalationResponse(
        success=True,
        message=f"Complaint transferred to {dept.name if dept else 'department'} successfully",
        complaint_id=complaint.id,
        old_assignment_type=old_assignment_type,
        new_assignment_type="department"
    )


@router.post("/{complaint_id}/reassign-to-gp", response_model=EscalationResponse)
async def reassign_complaint_to_gp(
    complaint_id: UUID,
    payload: ReassignRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Reassign a complaint down to a Gram Panchayat (used by TP/ZP officers)."""
    
    # Only TP/ZP officials can reassign down to GP
    higher_roles = [
        UserRole.TALUK_PANCHAYAT_OFFICER, UserRole.TP_PRESIDENT,
        UserRole.ZILLA_PANCHAYAT_OFFICER, UserRole.ZP_PRESIDENT,
        UserRole.ADMIN
    ]
    if current_user.role not in higher_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Taluk/Zilla Panchayat officials can reassign to Gram Panchayat"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Store old assignment type
    old_assignment_type = complaint.assignment_type
    
    # Perform reassignment
    success = reassign_to_gram_panchayat(db, complaint, payload.gram_panchayat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reassign: Gram Panchayat not found"
        )
    
    # Log the reassignment
    gp = db.query(GramPanchayat).filter(GramPanchayat.id == payload.gram_panchayat_id).first()
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=complaint.status,
        new_status=complaint.status,
        changed_by=current_user.id,
        note=f"Reassigned to {gp.village_name if gp else 'Gram Panchayat'}. {payload.note or ''}",
    )
    
    complaint.updated_at = _utcnow()
    db.commit()
    db.refresh(complaint)
    
    await ComplaintNotifications.notify_complaint_reassigned(complaint, current_user, gp.village_name if gp else "Gram Panchayat")  # type: ignore[func-returns-value]
    
    return EscalationResponse(
        success=True,
        message=f"Complaint reassigned to {gp.village_name if gp else 'Gram Panchayat'} successfully",
        complaint_id=complaint.id,
        old_assignment_type=old_assignment_type,
        new_assignment_type="gram_panchayat"
    )


# ---------------------------------------------------------------------------
# Ward-Centric Workflow (NEW SIMPLIFIED FLOW)
# ---------------------------------------------------------------------------

@router.post("/{complaint_id}/ward-assign", response_model=WardAssignmentResponse)
async def ward_assign_to_department(
    complaint_id: UUID,
    payload: WardAssignToDepartmentRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """
    Ward officer assigns complaint to a department.
    This is the key transition: Ward → Department
    """
    
    # Only ward officers can perform this action
    if current_user.role != UserRole.WARD_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ward officers can assign complaints to departments"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Verify complaint is at ward level
    if complaint.assignment_type != "ward":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Complaint is already assigned to {complaint.assignment_type}"
        )
    
    # Verify ward officer is assigned to this complaint's ward
    if current_user.ward_id != complaint.ward_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only assign complaints from your own ward"
        )
    
    # Get department
    dept = db.query(Department).filter(Department.id == payload.dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Perform assignment with jurisdiction validation
    from app.services.complaint_routing import ward_assign_to_department as do_assignment
    success, error_msg = do_assignment(
        db=db,
        complaint=complaint,
        dept_id=payload.dept_id,
        ward_officer_id=current_user.id,
        public_note=payload.public_note
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or "Failed to assign complaint to department"
        )
    
    # Log the assignment
    _add_status_log(
        db,
        complaint_id=complaint.id,
        old_status=complaint.status,
        new_status=ComplaintStatus.ASSIGNED,
        changed_by=current_user.id,
        note=f"Assigned to {dept.name} by ward officer. {payload.public_note}",
    )
    
    # Update status
    complaint.status = ComplaintStatus.ASSIGNED
    complaint.updated_at = _utcnow()
    complaint.last_activity_at = _utcnow()
    
    db.commit()
    db.refresh(complaint)
    
    await ComplaintNotifications.notify_complaint_assigned_to_department(complaint, current_user, dept.name)  # type: ignore[func-returns-value]
    
    return WardAssignmentResponse(
        success=True,
        message=f"Complaint assigned to {dept.name} successfully",
        complaint_id=complaint.id,
        assigned_department=dept.name,
        ward_officer_name=current_user.name
    )


@router.get("/my-ward", response_model=ComplaintListResponse)
async def get_my_ward_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    """Get complaints assigned to the current ward officer's ward."""
    
    # Check if user is a ward officer
    if current_user.role != UserRole.WARD_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for ward officers"
        )
    
    if not current_user.ward_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no ward assignment"
        )
    
    # Query complaints in this ward
    query: SAQuery[Complaint] = db.query(Complaint).filter(
        Complaint.ward_id == current_user.ward_id,
        Complaint.assignment_type == "ward"  # Only show complaints not yet assigned to departments
    )
    
    # Apply filters
    if status_filter:
        try:
            status_enum = ComplaintStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status") from exc
        query = query.filter(Complaint.status == status_enum)
    if category:
        query = query.filter(Complaint.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Complaint.title.ilike(like)
            | Complaint.description.ilike(like)
            | Complaint.location_description.ilike(like)
        )

    total = query.count()
    complaints = _paginate(query, page=page, page_size=page_size)
    complaint_payloads = [ComplaintResponse.model_validate(item) for item in complaints]

    return ComplaintListResponse(
        total=total,
        page=page,
        page_size=page_size,
        complaints=complaint_payloads,
    )


@router.post("/{complaint_id}/public-note")
async def add_public_note_to_complaint(
    complaint_id: UUID,
    payload: AddPublicNoteRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Add a public note to complaint (visible to citizen)."""
    
    # Only officers can add public notes
    official_roles = [
        UserRole.MODERATOR, UserRole.DEPARTMENT_OFFICER, UserRole.WARD_OFFICER,
        UserRole.ADMIN, UserRole.MLA
    ]
    if current_user.role not in official_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officials can add public notes"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Add the public note
    from app.services.complaint_routing import add_public_note
    add_public_note(complaint, payload.note, current_user.name)
    
    complaint.updated_at = _utcnow()
    complaint.last_activity_at = _utcnow()
    
    db.commit()
    db.refresh(complaint)
    
    return {
        "success": True,
        "message": "Public note added successfully",
        "complaint_id": str(complaint.id),
        "public_notes": complaint.public_notes or ""
    }


@router.post("/{complaint_id}/internal-note")
async def add_internal_note_to_complaint(
    complaint_id: UUID,
    payload: AddInternalNoteRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Add an internal note to complaint (only visible to officers)."""
    
    # Only officers can add internal notes
    official_roles = [
        UserRole.MODERATOR, UserRole.DEPARTMENT_OFFICER, UserRole.WARD_OFFICER,
        UserRole.ADMIN, UserRole.MLA
    ]
    if current_user.role not in official_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officials can add internal notes"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    _ensure_constituency_access(complaint, current_user)
    
    # Add the internal note
    from app.services.complaint_routing import add_internal_note
    add_internal_note(complaint, payload.note, current_user.name)
    
    complaint.updated_at = _utcnow()
    
    db.commit()
    db.refresh(complaint)
    
    return {
        "success": True,
        "message": "Internal note added successfully",
        "complaint_id": str(complaint.id),
        "internal_notes": complaint.internal_notes or ""
    }


@router.get("/ward/{ward_id}/available-departments", response_model=List[Dict[str, Any]])
async def get_available_departments_for_ward(
    ward_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get departments available for a specific ward based on jurisdiction.
    
    Example:
    - Ward in Puttur GP → Returns only Puttur GP departments (Puttur PWD, Puttur Electricity, etc.)
    - Ward in Mangalore Corp → Returns only Mangalore departments (Mangalore PWD, etc.)
    
    This ensures ward officers only see relevant departments.
    """
    if current_user.role != UserRole.WARD_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ward officers can view available departments"
        )
    
    # Get the ward
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ward not found")
    
    # Verify ward officer has access to this ward
    if current_user.ward_id != ward_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view departments for your assigned ward"
        )
    
    # Query departments based on ward's jurisdiction
    query = db.query(Department).filter(Department.constituency_id == ward.constituency_id)
    
    if ward.gram_panchayat_id:
        # Ward belongs to Gram Panchayat
        query = query.filter(Department.gram_panchayat_id == ward.gram_panchayat_id)
    elif ward.taluk_panchayat_id:
        # Ward belongs to Taluk Panchayat
        query = query.filter(Department.taluk_panchayat_id == ward.taluk_panchayat_id)
    elif ward.city_corporation_id:
        # Ward belongs to City Corporation
        query = query.filter(Department.city_corporation_id == ward.city_corporation_id)
    else:
        # Ward has no parent - return empty list
        return []
    
    departments = query.order_by(Department.name).all()
    
    return [
        {
            "id": str(dept.id),
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
            "contact_phone": dept.contact_phone,
            "contact_email": dept.contact_email,
        }
        for dept in departments
    ]



