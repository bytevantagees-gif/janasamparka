"""
Analytics router - Metrics, statistics, and reporting endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.core.analytics import AnalyticsService
from app.core.export import ExportService
from app.models.user import User, UserRole
from app.models.complaint import Complaint, ComplaintStatus
from app.models.ward import Ward
from app.models.department import Department
from app.models.panchayat import GramPanchayat, TalukPanchayat
from app.schemas.analytics import (
    ComplaintStats,
    DepartmentPerformance,
    CategoryStats,
    PriorityStats,
    SLAMetrics,
    TrendAnalysis,
    DashboardSummary,
    ComparativeAnalysis,
    UserActivityStats,
    ReportFilter,
    ExportRequest
)
from app.schemas.rating import RatingSummary

router = APIRouter()


@router.get("/overview", response_model=ComplaintStats)
async def get_complaint_overview(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get overall complaint statistics
    Automatically filtered by constituency for non-admin users
    """
    service = AnalyticsService(db)
    return service.get_overall_stats(constituency_id=constituency_filter)


@router.get("/categories", response_model=List[CategoryStats])
async def get_category_breakdown(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get complaint breakdown by category
    """
    service = AnalyticsService(db)
    return service.get_category_breakdown(constituency_id=constituency_filter)


@router.get("/priorities", response_model=List[PriorityStats])
async def get_priority_breakdown(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get complaint breakdown by priority level
    """
    service = AnalyticsService(db)
    return service.get_priority_breakdown(constituency_id=constituency_filter)


@router.get("/departments", response_model=List[DepartmentPerformance])
async def get_department_performance(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get department performance metrics
    Shows resolution times, completion rates, and SLA compliance
    """
    service = AnalyticsService(db)
    return service.get_department_performance(constituency_id=constituency_filter)


@router.get("/sla", response_model=SLAMetrics)
async def get_sla_metrics(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get SLA compliance metrics
    Shows percentage of complaints meeting SLA targets
    
    SLA Targets:
    - Critical: 24 hours
    - High: 72 hours (3 days)
    - Medium: 168 hours (7 days)
    - Low: 336 hours (14 days)
    """
    service = AnalyticsService(db)
    return service.get_sla_metrics(constituency_id=constituency_filter)


@router.get("/trends", response_model=TrendAnalysis)
async def get_trend_analysis(
    period: str = Query("daily", description="Period: daily, weekly, monthly"),
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get trend analysis over time
    Shows complaint volume trends and resolution patterns
    """
    service = AnalyticsService(db)
    return service.get_trend_analysis(
        period=period,
        days=days,
        constituency_id=constituency_filter
    )


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard summary with all key metrics
    Optimized single endpoint for dashboard display
    """
    service = AnalyticsService(db)
    
    # Get all metrics
    overall_stats = service.get_overall_stats(constituency_id=constituency_filter)
    category_breakdown = service.get_category_breakdown(constituency_id=constituency_filter)
    priority_breakdown = service.get_priority_breakdown(constituency_id=constituency_filter)
    department_performance = service.get_department_performance(constituency_id=constituency_filter)
    sla_metrics = service.get_sla_metrics(constituency_id=constituency_filter)
    recent_trend = service.get_trend_analysis(
        period="daily",
        days=30,
        constituency_id=constituency_filter
    )
    
    # Calculate additional metrics
    from app.models.complaint import Complaint
    
    query = db.query(Complaint)
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    # This week
    week_start = datetime.utcnow() - timedelta(days=7)
    complaints_this_week = query.filter(
        Complaint.created_at >= week_start
    ).count()
    
    # This month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    complaints_this_month = query.filter(
        Complaint.created_at >= month_start
    ).count()
    
    # Resolution rate
    total_resolved = overall_stats.closed + overall_stats.resolved
    resolution_rate = (
        (total_resolved / overall_stats.total * 100)
        if overall_stats.total > 0 else 0
    )
    
    # Average resolution time in days
    avg_resolution_days = None
    if sla_metrics.avg_resolution_time_hours:
        avg_resolution_days = round(sla_metrics.avg_resolution_time_hours / 24, 2)
    
    return DashboardSummary(
        overall_stats=overall_stats,
        category_breakdown=category_breakdown,
        priority_breakdown=priority_breakdown,
        department_performance=department_performance,
        sla_metrics=sla_metrics,
        recent_trend=recent_trend,
        top_performers=[],  # TODO: Implement user activity tracking
        avg_resolution_time_days=avg_resolution_days,
        complaints_this_week=complaints_this_week,
        complaints_this_month=complaints_this_month,
        resolution_rate=round(resolution_rate, 2)
    )


@router.get("/comparison")
async def get_comparative_analysis(
    current_period_days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Compare current period with previous period
    Shows trends and changes over time
    """
    from app.models.complaint import Complaint
    
    service = AnalyticsService(db)
    
    # Current period
    current_end = datetime.utcnow()
    current_start = current_end - timedelta(days=current_period_days)
    
    # Previous period (same duration)
    previous_end = current_start
    previous_start = previous_end - timedelta(days=current_period_days)
    
    # Query for current period
    current_query = db.query(Complaint).filter(
        Complaint.created_at >= current_start,
        Complaint.created_at <= current_end
    )
    
    # Query for previous period
    previous_query = db.query(Complaint).filter(
        Complaint.created_at >= previous_start,
        Complaint.created_at < previous_end
    )
    
    if constituency_filter:
        current_query = current_query.filter(Complaint.constituency_id == constituency_filter)
        previous_query = previous_query.filter(Complaint.constituency_id == constituency_filter)
    
    # Get stats for both periods
    def get_period_stats(query):
        total = query.count()
        submitted = query.filter(Complaint.status == "submitted").count()
        assigned = query.filter(Complaint.status == "assigned").count()
        in_progress = query.filter(Complaint.status == "in_progress").count()
        resolved = query.filter(Complaint.status == "resolved").count()
        closed = query.filter(Complaint.status == "closed").count()
        rejected = query.filter(Complaint.status == "rejected").count()
        
        return ComplaintStats(
            total=total,
            submitted=submitted,
            assigned=assigned,
            in_progress=in_progress,
            resolved=resolved,
            closed=closed,
            rejected=rejected
        )
    
    current_stats = get_period_stats(current_query)
    previous_stats = get_period_stats(previous_query)
    
    # Calculate percentage changes
    def calc_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
    
    change_percentage = {
        "total": calc_change(current_stats.total, previous_stats.total),
        "submitted": calc_change(current_stats.submitted, previous_stats.submitted),
        "resolved": calc_change(current_stats.resolved, previous_stats.resolved),
        "closed": calc_change(current_stats.closed, previous_stats.closed),
    }
    
    # Determine overall trend
    if change_percentage["total"] > 10:
        trend = "increased"
    elif change_percentage["total"] < -10:
        trend = "decreased"
    else:
        trend = "stable"
    
    return ComparativeAnalysis(
        current_period=current_stats,
        previous_period=previous_stats,
        change_percentage=change_percentage,
        trend=trend
    )


@router.get("/alerts")
async def get_performance_alerts(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get performance alerts and warnings
    Identifies SLA breaches, high volumes, and low performance
    """
    from app.models.complaint import Complaint
    from app.schemas.analytics import AlertMetric
    
    service = AnalyticsService(db)
    alerts = []
    
    # Check SLA breaches
    sla_metrics = service.get_sla_metrics(constituency_id=constituency_filter)
    if sla_metrics.sla_compliance_rate < 80:
        alerts.append(AlertMetric(
            alert_type="sla_breach",
            severity="high" if sla_metrics.sla_compliance_rate < 70 else "medium",
            message=f"SLA compliance is at {sla_metrics.sla_compliance_rate}%. Target is 85%+",
            affected_count=sla_metrics.breached_sla,
            created_at=datetime.utcnow()
        ))
    
    # Check for old unresolved complaints
    query = db.query(Complaint).filter(
        Complaint.status.in_(["submitted", "assigned", "in_progress"])
    )
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    old_threshold = datetime.utcnow() - timedelta(days=14)
    old_complaints = query.filter(Complaint.created_at < old_threshold).count()
    
    if old_complaints > 5:
        alerts.append(AlertMetric(
            alert_type="aging_complaints",
            severity="medium",
            message=f"{old_complaints} complaints are older than 14 days and still unresolved",
            affected_count=old_complaints,
            created_at=datetime.utcnow()
        ))
    
    # Check for high volume (spike detection)
    trend = service.get_trend_analysis(period="daily", days=7, constituency_id=constituency_filter)
    if trend.trend_direction == "increasing":
        recent_avg = sum(p.new for p in trend.data_points[-3:]) / 3
        if recent_avg > 10:  # Threshold for high volume
            alerts.append(AlertMetric(
                alert_type="high_volume",
                severity="low",
                message=f"Complaint volume is increasing. Recent average: {recent_avg:.1f} per day",
                affected_count=int(recent_avg * 7),
                created_at=datetime.utcnow()
            ))
    
    return {"alerts": alerts}


@router.get("/export/csv")
async def export_data_csv(
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Export complaints data to CSV format
    Applies constituency filter for non-admin users
    """
    # Build filters
    filters = ReportFilter(
        constituency_id=constituency_filter,
        status=status,
        category=category
    )
    
    service = ExportService(db)
    csv_content = service.export_to_csv(filters)
    
    # Generate filename with timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"complaints_export_{timestamp}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export/json")
async def export_data_json(
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Export complaints data to JSON format
    Includes detailed information about each complaint
    """
    # Build filters
    filters = ReportFilter(
        constituency_id=constituency_filter,
        status=status,
        category=category
    )
    
    service = ExportService(db)
    data = service.export_to_dict(filters)
    summary = service.generate_summary_report(filters)
    
    return {
        "export_date": datetime.utcnow().isoformat(),
        "exported_by": current_user.name,
        "summary": summary,
        "data": data
    }


@router.get("/reports/summary")
async def get_summary_report(
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Generate a statistical summary report
    """
    # Build filters
    filters = ReportFilter(
        constituency_id=constituency_filter,
        status=status,
        category=category
    )
    
    service = ExportService(db)
    summary = service.generate_summary_report(filters)
    
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.name,
        "filters_applied": filters.dict() if filters else {},
        **summary
    }


@router.get("/satisfaction", response_model=RatingSummary)
async def get_citizen_satisfaction(
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get citizen satisfaction metrics based on ratings
    Shows average rating, distribution, and satisfaction rate
    """
    from app.models.complaint import Complaint
    
    query = db.query(Complaint).filter(
        Complaint.citizen_rating.isnot(None)
    )
    
    # Apply constituency filter
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    rated_complaints = query.all()
    
    if not rated_complaints:
        return RatingSummary(
            total_ratings=0,
            average_rating=0.0,
            rating_distribution={},
            satisfaction_rate=0.0
        )
    
    # Calculate metrics
    total_ratings = len(rated_complaints)
    ratings = [c.citizen_rating for c in rated_complaints]
    average_rating = sum(ratings) / total_ratings
    
    # Rating distribution
    rating_distribution = {str(i): 0 for i in range(1, 6)}
    for rating in ratings:
        rating_distribution[str(rating)] = rating_distribution.get(str(rating), 0) + 1
    
    # Satisfaction rate (4-5 stars)
    satisfied = sum(1 for r in ratings if r >= 4)
    satisfaction_rate = (satisfied / total_ratings) * 100
    
    return RatingSummary(
        total_ratings=total_ratings,
        average_rating=round(average_rating, 2),
        rating_distribution=rating_distribution,
        satisfaction_rate=round(satisfaction_rate, 2)
    )


@router.get("/mla/performance-comparison")
async def get_mla_performance_comparison(
    unit_type: str = Query(..., description="ward, gram_panchayat, taluk_panchayat, department"),
    unit_ids: Optional[List[str]] = Query(None, description="Specific units to compare"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Compare performance across multiple units (wards, GPs, taluks, departments)
    Returns side-by-side metrics for MLA decision-making
    Non-admin users can only compare units from their own constituency
    """
    # Verify MLA/Admin role
    if current_user.role not in [UserRole.MLA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, 
            detail="Only MLAs and Admins can access performance comparison"
        )
    
    # Use constituency filter (None for admin, user's constituency for MLA)
    constituency_id = constituency_filter
    
    comparison_data = []
    
    # Convert string IDs to UUIDs if provided
    unit_uuid_ids = None
    if unit_ids:
        try:
            unit_uuid_ids = [UUID(uid) for uid in unit_ids]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid unit IDs format")
    
    # Fetch and calculate metrics based on unit type
    if unit_type == "ward":
        units_query = db.query(Ward).filter(Ward.constituency_id == constituency_id)
        if unit_uuid_ids:
            units_query = units_query.filter(Ward.id.in_(unit_uuid_ids))
        units = units_query.all()
        
        for ward in units:
            metrics = _calculate_unit_metrics(
                db, "ward", ward.id, date_from, date_to
            )
            comparison_data.append({
                "id": str(ward.id),
                "name": ward.name,
                "type": "ward",
                "metrics": metrics,
                "insights": _generate_insights(metrics)
            })
    
    elif unit_type == "gram_panchayat":
        units_query = db.query(GramPanchayat).filter(
            GramPanchayat.constituency_id == constituency_id
        )
        if unit_uuid_ids:
            units_query = units_query.filter(GramPanchayat.id.in_(unit_uuid_ids))
        units = units_query.all()
        
        for gp in units:
            metrics = _calculate_unit_metrics(
                db, "gram_panchayat", gp.id, date_from, date_to
            )
            comparison_data.append({
                "id": str(gp.id),
                "name": gp.village,
                "type": "gram_panchayat",
                "metrics": metrics,
                "insights": _generate_insights(metrics)
            })
    
    elif unit_type == "taluk_panchayat":
        units_query = db.query(TalukPanchayat).join(
            GramPanchayat, GramPanchayat.taluk_panchayat_id == TalukPanchayat.id
        ).filter(GramPanchayat.constituency_id == constituency_id).distinct()
        
        if unit_uuid_ids:
            units_query = units_query.filter(TalukPanchayat.id.in_(unit_uuid_ids))
        units = units_query.all()
        
        for tp in units:
            metrics = _calculate_unit_metrics(
                db, "taluk_panchayat", tp.id, date_from, date_to
            )
            comparison_data.append({
                "id": str(tp.id),
                "name": tp.name,
                "type": "taluk_panchayat",
                "metrics": metrics,
                "insights": _generate_insights(metrics)
            })
    
    elif unit_type == "department":
        # Get departments that have complaints in this constituency
        dept_ids = db.query(Department.id).join(
            Complaint, Complaint.dept_id == Department.id
        ).filter(Complaint.constituency_id == constituency_id).distinct().all()
        
        dept_ids = [d[0] for d in dept_ids]
        
        units_query = db.query(Department).filter(Department.id.in_(dept_ids))
        if unit_uuid_ids:
            units_query = units_query.filter(Department.id.in_(unit_uuid_ids))
        units = units_query.all()
        
        for dept in units:
            metrics = _calculate_unit_metrics(
                db, "department", dept.id, date_from, date_to, constituency_id
            )
            comparison_data.append({
                "id": str(dept.id),
                "name": dept.name,
                "type": "department",
                "metrics": metrics,
                "insights": _generate_insights(metrics)
            })
    else:
        raise HTTPException(
            status_code=400, 
            detail="Invalid unit_type. Must be: ward, gram_panchayat, taluk_panchayat, or department"
        )
    
    # Calculate constituency average
    if comparison_data:
        total_complaints = sum(u["metrics"]["total_complaints"] for u in comparison_data)
        total_resolved = sum(u["metrics"]["resolved"] for u in comparison_data)
        avg_resolution_rates = [u["metrics"]["resolution_rate"] for u in comparison_data if u["metrics"]["resolution_rate"] is not None]
        avg_satisfaction_scores = [u["metrics"]["citizen_satisfaction"] for u in comparison_data if u["metrics"]["citizen_satisfaction"] is not None]
        
        constituency_avg = {
            "total_complaints": total_complaints,
            "resolution_rate": round(sum(avg_resolution_rates) / len(avg_resolution_rates), 1) if avg_resolution_rates else 0,
            "citizen_satisfaction": round(sum(avg_satisfaction_scores) / len(avg_satisfaction_scores), 2) if avg_satisfaction_scores else 0
        }
    else:
        constituency_avg = {
            "total_complaints": 0,
            "resolution_rate": 0,
            "citizen_satisfaction": 0
        }
    
    # Find best performer
    best_performer = None
    if comparison_data:
        best_performer = max(
            comparison_data, 
            key=lambda x: x["metrics"]["resolution_rate"] if x["metrics"]["resolution_rate"] is not None else 0
        )
    
    # Find units needing attention
    needs_attention = [
        unit for unit in comparison_data 
        if unit["metrics"]["resolution_rate"] is not None and unit["metrics"]["resolution_rate"] < 70
    ]
    
    return {
        "unit_type": unit_type,
        "comparison": sorted(comparison_data, key=lambda x: x["metrics"]["resolution_rate"] or 0, reverse=True),
        "constituency_average": constituency_avg,
        "best_performer": best_performer,
        "needs_attention": needs_attention,
        "date_range": {
            "from": date_from.isoformat() if date_from else None,
            "to": date_to.isoformat() if date_to else None
        }
    }


def _calculate_unit_metrics(
    db: Session, 
    unit_type: str, 
    unit_id: UUID, 
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    constituency_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """Calculate comprehensive metrics for a unit (ward, GP, taluk, department)"""
    
    # Build base query
    query = db.query(Complaint)
    
    if unit_type == "ward":
        query = query.filter(Complaint.ward_id == unit_id)
    elif unit_type == "gram_panchayat":
        query = query.filter(Complaint.gram_panchayat_id == unit_id)
    elif unit_type == "taluk_panchayat":
        # Get all GPs under this taluk
        gp_ids = db.query(GramPanchayat.id).filter(
            GramPanchayat.taluk_panchayat_id == unit_id
        ).all()
        gp_ids = [gp[0] for gp in gp_ids]
        query = query.filter(Complaint.gram_panchayat_id.in_(gp_ids))
    elif unit_type == "department":
        query = query.filter(Complaint.dept_id == unit_id)
        if constituency_id:
            query = query.filter(Complaint.constituency_id == constituency_id)
    
    # Apply date filters
    if date_from:
        query = query.filter(Complaint.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Complaint.created_at <= datetime.combine(date_to, datetime.max.time()))
    
    # Calculate counts
    total = query.count()
    resolved_query = query.filter(
        Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
    )
    resolved = resolved_query.count()
    pending = total - resolved
    
    # Calculate average citizen rating
    avg_rating_result = db.query(func.avg(Complaint.citizen_rating)).filter(
        Complaint.id.in_([c.id for c in query.all()]),
        Complaint.citizen_rating.isnot(None)
    ).scalar()
    avg_rating = float(avg_rating_result) if avg_rating_result else 0
    
    # Calculate average resolution time
    resolved_complaints = resolved_query.filter(
        Complaint.resolved_at.isnot(None)
    ).all()
    
    avg_resolution_days = None
    if resolved_complaints:
        total_days = sum(
            (c.resolved_at - c.created_at).days 
            for c in resolved_complaints
        )
        avg_resolution_days = round(total_days / len(resolved_complaints), 1)
    
    # Count overdue cases (>7 days old and not resolved)
    seven_days_ago = datetime.now() - timedelta(days=7)
    overdue_cases = query.filter(
        Complaint.status.not_in([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]),
        Complaint.created_at < seven_days_ago
    ).count()
    
    return {
        "total_complaints": total,
        "resolved": resolved,
        "pending": pending,
        "resolution_rate": round((resolved / total * 100), 1) if total > 0 else 0,
        "avg_resolution_days": avg_resolution_days,
        "citizen_satisfaction": round(avg_rating, 2),
        "active_cases": pending,
        "overdue_cases": overdue_cases
    }


def _generate_insights(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI-like insights from metrics"""
    insights = {
        "performance_level": "good",
        "recommendations": [],
        "red_flags": [],
        "green_stars": []
    }
    
    # Resolution rate analysis
    resolution_rate = metrics.get("resolution_rate", 0)
    if resolution_rate < 60:
        insights["performance_level"] = "poor"
        insights["red_flags"].append("Low resolution rate - needs immediate attention")
        insights["recommendations"].append("Increase officer assignment or investigate bottlenecks")
    elif resolution_rate > 85:
        insights["performance_level"] = "excellent"
        insights["green_stars"].append("Excellent resolution rate!")
    
    # Citizen satisfaction analysis
    satisfaction = metrics.get("citizen_satisfaction", 0)
    if satisfaction < 3.0 and satisfaction > 0:
        insights["red_flags"].append("Low citizen satisfaction - quality of work may be poor")
        insights["recommendations"].append("Review completed work quality and officer training")
    elif satisfaction >= 4.0:
        insights["green_stars"].append("High citizen satisfaction!")
    
    # Resolution time analysis
    avg_days = metrics.get("avg_resolution_days")
    if avg_days and avg_days > 7:
        insights["red_flags"].append(f"Slow resolution time ({avg_days} days) exceeding 7-day SLA")
        insights["recommendations"].append("Review officer workload and resource allocation")
    
    # Overdue cases analysis
    overdue = metrics.get("overdue_cases", 0)
    if overdue > 5:
        insights["red_flags"].append(f"{overdue} cases are overdue")
        insights["recommendations"].append("Escalate overdue cases to department heads")
    
    # Adjust performance level based on flags
    if len(insights["red_flags"]) >= 3:
        insights["performance_level"] = "critical"
    elif len(insights["red_flags"]) >= 2:
        insights["performance_level"] = "poor"
    elif len(insights["red_flags"]) == 1:
        insights["performance_level"] = "fair"
    
    return insights


@router.get("/satisfaction/aggregated")
async def get_satisfaction_aggregated(
    unit_type: str = Query(..., description="Type of unit: ward, gram_panchayat, taluk_panchayat"),
    unit_ids: Optional[List[str]] = Query(None, description="Optional list of specific unit IDs"),
    unhappy_threshold: int = Query(2, description="Rating threshold for unhappy citizens"),
    date_from: Optional[date] = Query(None, description="Start date for filtering"),
    date_to: Optional[date] = Query(None, description="End date for filtering"),
    current_user: User = Depends(require_auth),
    constituency_id: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get aggregated citizen satisfaction metrics per unit (ward/GP/TP).
    Identifies unhappy citizens needing moderator intervention.
    Returns satisfaction index and list of unhappy citizens with contact info.
    """
    # Role check: moderator, admin, mla can access
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.MLA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators, admins, and MLAs can access satisfaction data"
        )
    
    # Validate unit_type
    if unit_type not in ["ward", "gram_panchayat", "taluk_panchayat"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid unit_type. Must be one of: ward, gram_panchayat, taluk_panchayat"
        )
    
    # Build base query
    query = db.query(Complaint).filter(Complaint.constituency_id == constituency_id)
    
    # Add date filters
    if date_from:
        query = query.filter(Complaint.created_at >= date_from)
    if date_to:
        query = query.filter(Complaint.created_at <= date_to)
    
    # Filter by unit type
    if unit_type == "ward":
        if unit_ids:
            query = query.filter(Complaint.ward_id.in_(unit_ids))
    elif unit_type == "gram_panchayat":
        if unit_ids:
            query = query.filter(Complaint.gram_panchayat_id.in_(unit_ids))
    elif unit_type == "taluk_panchayat":
        # For TP, we need to join through GPs
        gps = db.query(GramPanchayat.id).filter(GramPanchayat.taluk_panchayat_id.in_(unit_ids)).all()
        gp_ids = [gp[0] for gp in gps]
        if gp_ids:
            query = query.filter(Complaint.gram_panchayat_id.in_(gp_ids))
    
    # Get all complaints with ratings
    complaints_with_ratings = query.filter(Complaint.citizen_rating.isnot(None)).all()
    
    # Calculate satisfaction index per unit
    unit_satisfaction = {}
    
    for complaint in complaints_with_ratings:
        # Determine unit_id based on type
        if unit_type == "ward":
            unit_id = str(complaint.ward_id) if complaint.ward_id else None
        elif unit_type == "gram_panchayat":
            unit_id = str(complaint.gram_panchayat_id) if complaint.gram_panchayat_id else None
        elif unit_type == "taluk_panchayat":
            # Get TP ID through GP
            if complaint.gram_panchayat_id:
                gp = db.query(GramPanchayat).filter(GramPanchayat.id == complaint.gram_panchayat_id).first()
                unit_id = str(gp.taluk_panchayat_id) if gp and gp.taluk_panchayat_id else None
            else:
                unit_id = None
        
        if not unit_id:
            continue
        
        if unit_id not in unit_satisfaction:
            unit_satisfaction[unit_id] = {
                "total_ratings": 0,
                "total_score": 0,
                "satisfaction_index": 0.0,
                "unhappy_count": 0
            }
        
        unit_satisfaction[unit_id]["total_ratings"] += 1
        unit_satisfaction[unit_id]["total_score"] += complaint.citizen_rating
        if complaint.citizen_rating <= unhappy_threshold:
            unit_satisfaction[unit_id]["unhappy_count"] += 1
    
    # Calculate satisfaction index (0-100 scale)
    for unit_id, data in unit_satisfaction.items():
        if data["total_ratings"] > 0:
            avg_rating = data["total_score"] / data["total_ratings"]
            # Convert 0-5 scale to 0-100
            data["satisfaction_index"] = round((avg_rating / 5.0) * 100, 1)
    
    # Get unhappy citizens needing intervention
    unhappy_citizens = []
    
    for complaint in complaints_with_ratings:
        if complaint.citizen_rating and complaint.citizen_rating <= unhappy_threshold:
            # Get citizen info
            citizen = db.query(User).filter(User.id == complaint.citizen_id).first()
            if not citizen:
                continue
            
            # Determine unit name
            unit_name = None
            if unit_type == "ward" and complaint.ward_id:
                ward = db.query(Ward).filter(Ward.id == complaint.ward_id).first()
                unit_name = ward.name if ward else None
            elif unit_type == "gram_panchayat" and complaint.gram_panchayat_id:
                gp = db.query(GramPanchayat).filter(GramPanchayat.id == complaint.gram_panchayat_id).first()
                unit_name = gp.name if gp else None
            elif unit_type == "taluk_panchayat" and complaint.gram_panchayat_id:
                gp = db.query(GramPanchayat).filter(GramPanchayat.id == complaint.gram_panchayat_id).first()
                if gp and gp.taluk_panchayat_id:
                    tp = db.query(TalukPanchayat).filter(TalukPanchayat.id == gp.taluk_panchayat_id).first()
                    unit_name = tp.name if tp else None
            
            unhappy_citizens.append({
                "complaint_id": str(complaint.id),
                "complaint_title": complaint.title,
                "citizen_id": str(citizen.id),
                "citizen_name": citizen.name,
                "citizen_phone": citizen.phone,
                "rating": complaint.citizen_rating,
                "rating_feedback": complaint.rating_feedback,
                "rating_submitted_at": complaint.rating_submitted_at.isoformat() if complaint.rating_submitted_at else None,
                "unit_name": unit_name,
                "complaint_status": complaint.status.value,
                "resolved_at": complaint.resolved_at.isoformat() if complaint.resolved_at else None
            })
    
    # Get unit names for satisfaction index
    satisfaction_summary = []
    for unit_id, data in unit_satisfaction.items():
        unit_name = None
        if unit_type == "ward":
            ward = db.query(Ward).filter(Ward.id == UUID(unit_id)).first()
            unit_name = ward.name if ward else f"Ward {unit_id}"
        elif unit_type == "gram_panchayat":
            gp = db.query(GramPanchayat).filter(GramPanchayat.id == UUID(unit_id)).first()
            unit_name = gp.name if gp else f"GP {unit_id}"
        elif unit_type == "taluk_panchayat":
            tp = db.query(TalukPanchayat).filter(TalukPanchayat.id == UUID(unit_id)).first()
            unit_name = tp.name if tp else f"TP {unit_id}"
        
        satisfaction_summary.append({
            "unit_id": unit_id,
            "unit_name": unit_name,
            "unit_type": unit_type,
            "satisfaction_index": data["satisfaction_index"],
            "total_ratings": data["total_ratings"],
            "unhappy_count": data["unhappy_count"],
            "unhappy_percentage": round((data["unhappy_count"] / data["total_ratings"]) * 100, 1) if data["total_ratings"] > 0 else 0
        })
    
    # Sort by satisfaction_index ascending (worst first)
    satisfaction_summary.sort(key=lambda x: x["satisfaction_index"])
    
    # Sort unhappy citizens by rating (most unhappy first), then by date
    unhappy_citizens.sort(key=lambda x: (x["rating"], x["rating_submitted_at"]))
    
    return {
        "unit_type": unit_type,
        "date_range": {
            "from": date_from.isoformat() if date_from else None,
            "to": date_to.isoformat() if date_to else None
        },
        "satisfaction_summary": satisfaction_summary,
        "unhappy_citizens": unhappy_citizens,
        "total_unhappy_citizens": len(unhappy_citizens),
        "unhappy_threshold": unhappy_threshold,
        "summary_stats": {
            "total_units": len(satisfaction_summary),
            "avg_satisfaction_index": round(sum([s["satisfaction_index"] for s in satisfaction_summary]) / len(satisfaction_summary), 1) if satisfaction_summary else 0,
            "units_below_50": sum(1 for s in satisfaction_summary if s["satisfaction_index"] < 50),
            "total_ratings_received": sum([s["total_ratings"] for s in satisfaction_summary])
        }
    }


