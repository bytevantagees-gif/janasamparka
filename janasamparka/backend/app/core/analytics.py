"""
Analytics service for computing metrics and statistics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List, Dict
from datetime import datetime, timedelta, date, timezone
from uuid import UUID
from app.models.complaint import Complaint, StatusLog
from app.models.department import Department
from app.schemas.analytics import (
    ComplaintStats, DepartmentPerformance, CategoryStats, 
    PriorityStats, SLAMetrics, TimeSeriesDataPoint, TrendAnalysis
)


class AnalyticsService:
    """Service for computing analytics and metrics"""
    
    # SLA targets in hours
    SLA_TARGETS = {
        "critical": 24,  # 1 day
        "high": 72,      # 3 days
        "medium": 168,   # 7 days
        "low": 336       # 14 days
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_overall_stats(
        self, 
        constituency_id: Optional[UUID] = None
    ) -> ComplaintStats:
        """Get overall complaint statistics"""
        query = self.db.query(Complaint)
        
        if constituency_id:
            query = query.filter(Complaint.constituency_id == constituency_id)
        
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
    
    def get_category_breakdown(
        self,
        constituency_id: Optional[UUID] = None
    ) -> List[CategoryStats]:
        """Get breakdown by category"""
        query = self.db.query(
            Complaint.category,
            func.count(Complaint.id).label('count')
        )
        
        if constituency_id:
            query = query.filter(Complaint.constituency_id == constituency_id)
        
        results = query.group_by(Complaint.category).all()
        total = sum(int(r.count) for r in results)  # type: ignore[arg-type]
        
        category_stats: List[CategoryStats] = []
        for result in results:
            # Calculate average resolution time for this category
            avg_days = self._get_avg_resolution_time(
                category=result.category,
                constituency_id=constituency_id
            )
            
            count_val = int(result.count)  # type: ignore[arg-type]
            category_stats.append(CategoryStats(
                category=result.category,
                count=count_val,
                percentage=round((count_val / total * 100), 2) if total > 0 else 0,
                avg_resolution_days=avg_days
            ))
        
        return sorted(category_stats, key=lambda x: x.count, reverse=True)
    
    def get_priority_breakdown(
        self,
        constituency_id: Optional[UUID] = None
    ) -> List[PriorityStats]:
        """Get breakdown by priority"""
        query = self.db.query(
            Complaint.priority,
            func.count(Complaint.id).label('count')
        )
        
        if constituency_id:
            query = query.filter(Complaint.constituency_id == constituency_id)
        
        results = query.group_by(Complaint.priority).all()
        total = sum(int(r.count) for r in results)  # type: ignore[arg-type]
        
        priority_stats: List[PriorityStats] = []
        for result in results:
            avg_days = self._get_avg_resolution_time(
                priority=result.priority,
                constituency_id=constituency_id
            )
            
            count_val = int(result.count)  # type: ignore[arg-type]
            priority_stats.append(PriorityStats(
                priority=result.priority,
                count=count_val,
                percentage=round((count_val / total * 100), 2) if total > 0 else 0,
                avg_resolution_days=avg_days
            ))
        
        return priority_stats
    
    def get_department_performance(
        self,
        constituency_id: Optional[UUID] = None
    ) -> List[DepartmentPerformance]:
        """Get performance metrics by department"""
        query = self.db.query(Department)
        
        performance_list: List[DepartmentPerformance] = []
        
        for dept in query.all():
            complaints_query = self.db.query(Complaint).filter(
                Complaint.dept_id == dept.id
            )
            
            if constituency_id:
                complaints_query = complaints_query.filter(
                    Complaint.constituency_id == constituency_id
                )
            
            total_assigned = complaints_query.count()
            
            if total_assigned == 0:
                continue
            
            in_progress = complaints_query.filter(
                Complaint.status == "in_progress"
            ).count()
            
            completed = complaints_query.filter(
                or_(
                    Complaint.status == "resolved",
                    Complaint.status == "closed"
                )
            ).count()
            
            rejected = complaints_query.filter(
                Complaint.status == "rejected"
            ).count()
            
            # Calculate average resolution time
            resolved_complaints = complaints_query.filter(
                Complaint.resolved_at.isnot(None)
            ).all()
            
            avg_resolution_hours: Optional[float] = None
            if resolved_complaints:
                total_hours = sum(
                    (c.resolved_at - c.created_at).total_seconds() / 3600  # type: ignore[operator, union-attr]
                    for c in resolved_complaints
                    if c.resolved_at and c.created_at
                )
                avg_resolution_hours = total_hours / len(resolved_complaints)
            
            # Calculate response time (time to assignment)
            assigned_complaints = complaints_query.filter(
                Complaint.status.in_(["assigned", "in_progress", "resolved", "closed"])
            ).all()
            
            avg_response_hours: Optional[float] = None
            if assigned_complaints:
                response_times: List[float] = []
                for c in assigned_complaints:
                    # Find first assignment from status log
                    first_assignment = self.db.query(StatusLog).filter(
                        StatusLog.complaint_id == c.id,
                        StatusLog.new_status == "assigned"
                    ).order_by(StatusLog.timestamp).first()
                    
                    if first_assignment:
                        response_hours = (
                            first_assignment.timestamp - c.created_at
                        ).total_seconds() / 3600
                        response_times.append(response_hours)
                
                avg_response_hours = (
                    sum(response_times) / len(response_times)
                    if response_times else None
                )
            
            # Calculate rates
            completion_rate = (completed / total_assigned * 100) if total_assigned > 0 else 0
            
            # Calculate SLA compliance
            on_time_count = 0
            for c in resolved_complaints:
                if not c.resolved_at or not c.created_at:
                    continue
                sla_hours = self.SLA_TARGETS.get(c.priority, 168)
                resolution_hours = (c.resolved_at - c.created_at).total_seconds() / 3600  # type: ignore[operator]
                if resolution_hours <= sla_hours:
                    on_time_count += 1
            
            on_time_rate = (
                (on_time_count / len(resolved_complaints) * 100)
                if resolved_complaints else 0
            )
            
            performance_list.append(DepartmentPerformance(
                department_id=dept.id,
                department_name=dept.name,
                total_assigned=total_assigned,
                in_progress=in_progress,
                completed=completed,
                rejected=rejected,
                avg_resolution_time_hours=round(avg_resolution_hours, 2) if avg_resolution_hours else None,
                avg_response_time_hours=round(avg_response_hours, 2) if avg_response_hours else None,
                completion_rate=round(completion_rate, 2),
                on_time_rate=round(on_time_rate, 2)
            ))
        
        return sorted(performance_list, key=lambda x: x.total_assigned, reverse=True)
    
    def get_sla_metrics(
        self,
        constituency_id: Optional[UUID] = None
    ) -> SLAMetrics:
        """Calculate SLA compliance metrics"""
        query = self.db.query(Complaint).filter(
            Complaint.resolved_at.isnot(None)
        )
        
        if constituency_id:
            query = query.filter(Complaint.constituency_id == constituency_id)
        
        complaints = query.all()
        total = len(complaints)
        
        if total == 0:
            return SLAMetrics(
                total_complaints=0,
                within_sla=0,
                breached_sla=0,
                sla_compliance_rate=0,
                avg_resolution_time_hours=None,
                median_resolution_time_hours=None
            )
        
        within_sla = 0
        resolution_times: List[float] = []
        
        for complaint in complaints:
            if not complaint.resolved_at or not complaint.created_at:
                continue
            resolution_hours = (
                complaint.resolved_at - complaint.created_at  # type: ignore[operator]
            ).total_seconds() / 3600
            
            resolution_times.append(resolution_hours)
            
            sla_hours = self.SLA_TARGETS.get(complaint.priority, 168)
            if resolution_hours <= sla_hours:
                within_sla += 1
        
        breached_sla = total - within_sla
        compliance_rate = (within_sla / total * 100) if total > 0 else 0
        
        resolution_times.sort()
        median = resolution_times[len(resolution_times) // 2] if resolution_times else None
        avg = sum(resolution_times) / len(resolution_times) if resolution_times else None
        
        return SLAMetrics(
            total_complaints=total,
            within_sla=within_sla,
            breached_sla=breached_sla,
            sla_compliance_rate=round(compliance_rate, 2),
            avg_resolution_time_hours=round(avg, 2) if avg else None,
            median_resolution_time_hours=round(median, 2) if median else None
        )
    
    def get_trend_analysis(
        self,
        period: str = "daily",
        days: int = 30,
        constituency_id: Optional[UUID] = None
    ) -> TrendAnalysis:
        """Get trend analysis over time"""
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=days)
        
        query = self.db.query(Complaint).filter(
            Complaint.created_at >= datetime.combine(start_date, datetime.min.time())
        )
        
        if constituency_id:
            query = query.filter(Complaint.constituency_id == constituency_id)
        
        complaints = query.all()
        
        # Group by date
        date_groups: Dict[date, Dict[str, int]] = {}
        
        current_date = start_date
        while current_date <= end_date:
            date_groups[current_date] = {"new": 0, "resolved": 0, "total": 0}
            current_date += timedelta(days=1)
        
        for complaint in complaints:
            created_date = complaint.created_at.date()
            if created_date in date_groups:
                date_groups[created_date]["new"] += 1
                date_groups[created_date]["total"] += 1
            
            if complaint.resolved_at:
                resolved_date = complaint.resolved_at.date()
                if resolved_date in date_groups:
                    date_groups[resolved_date]["resolved"] += 1
        
        # Create data points
        data_points = [
            TimeSeriesDataPoint(
                date=d,
                count=stats["total"],
                resolved=stats["resolved"],
                new=stats["new"]
            )
            for d, stats in sorted(date_groups.items())
        ]
        
        # Determine trend
        if len(data_points) >= 7:
            recent_avg = sum(p.new for p in data_points[-7:]) / 7
            older_avg = sum(p.new for p in data_points[:7]) / 7
            
            if recent_avg > older_avg * 1.1:
                trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return TrendAnalysis(
            period=period,
            data_points=data_points,
            total_complaints=sum(p.new for p in data_points),
            total_resolved=sum(p.resolved for p in data_points),
            trend_direction=trend
        )
    
    def _get_avg_resolution_time(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        constituency_id: Optional[UUID] = None
    ) -> Optional[float]:
        """Helper to calculate average resolution time"""
        query = self.db.query(Complaint).filter(
            Complaint.resolved_at.isnot(None)
        )
        
        if category:
            query = query.filter(Complaint.category == category)
        if priority:
            query = query.filter(Complaint.priority == priority)
        if constituency_id:
            query = query.filter(Complaint.constituency_id == constituency_id)
        
        complaints = query.all()
        
        if not complaints:
            return None
        
        total_days = sum(
            (c.resolved_at - c.created_at).total_seconds() / 86400  # type: ignore[operator, union-attr]
            for c in complaints
            if c.resolved_at and c.created_at
        )
        
        valid_complaints = [c for c in complaints if c.resolved_at and c.created_at]
        if not valid_complaints:
            return None
            
        return round(total_days / len(valid_complaints), 2)
