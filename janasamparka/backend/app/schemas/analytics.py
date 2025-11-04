"""
Analytics and reporting schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date
from uuid import UUID


class ComplaintStats(BaseModel):
    """Overall complaint statistics"""
    total: int
    submitted: int
    assigned: int
    in_progress: int
    resolved: int
    closed: int
    rejected: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "submitted": 10,
                "assigned": 20,
                "in_progress": 30,
                "resolved": 25,
                "closed": 10,
                "rejected": 5
            }
        }


class DepartmentPerformance(BaseModel):
    """Department performance metrics"""
    department_id: UUID
    department_name: str
    total_assigned: int
    in_progress: int
    completed: int
    rejected: int
    avg_resolution_time_hours: Optional[float] = None
    avg_response_time_hours: Optional[float] = None
    completion_rate: float  # Percentage
    on_time_rate: float  # Percentage meeting SLA
    
    class Config:
        json_schema_extra = {
            "example": {
                "department_id": "123e4567-e89b-12d3-a456-426614174000",
                "department_name": "Road & Infrastructure",
                "total_assigned": 50,
                "in_progress": 10,
                "completed": 35,
                "rejected": 5,
                "avg_resolution_time_hours": 48.5,
                "avg_response_time_hours": 2.5,
                "completion_rate": 70.0,
                "on_time_rate": 85.0
            }
        }


class CategoryStats(BaseModel):
    """Statistics by complaint category"""
    category: str
    count: int
    percentage: float
    avg_resolution_days: Optional[float] = None


class PriorityStats(BaseModel):
    """Statistics by priority level"""
    priority: str
    count: int
    percentage: float
    avg_resolution_days: Optional[float] = None


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series"""
    date: date
    count: int
    resolved: int = 0
    new: int = 0


class TrendAnalysis(BaseModel):
    """Trend analysis over time"""
    period: str  # daily, weekly, monthly
    data_points: List[TimeSeriesDataPoint]
    total_complaints: int
    total_resolved: int
    trend_direction: str  # increasing, decreasing, stable


class SLAMetrics(BaseModel):
    """SLA compliance metrics"""
    total_complaints: int
    within_sla: int
    breached_sla: int
    sla_compliance_rate: float
    avg_resolution_time_hours: Optional[float] = None
    median_resolution_time_hours: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_complaints": 100,
                "within_sla": 85,
                "breached_sla": 15,
                "sla_compliance_rate": 85.0,
                "avg_resolution_time_hours": 36.5,
                "median_resolution_time_hours": 24.0
            }
        }


class UserActivityStats(BaseModel):
    """User activity statistics"""
    user_id: UUID
    user_name: str
    role: str
    complaints_created: int = 0
    status_changes: int = 0
    approvals: int = 0
    rejections: int = 0
    last_active: Optional[datetime] = None


class ConstituencyStats(BaseModel):
    """Constituency-level statistics"""
    constituency_id: UUID
    constituency_name: str
    total_complaints: int
    active_complaints: int
    resolved_complaints: int
    avg_resolution_days: Optional[float] = None
    top_categories: List[CategoryStats]
    department_performance: List[DepartmentPerformance]


class DashboardSummary(BaseModel):
    """Complete dashboard summary"""
    overall_stats: ComplaintStats
    category_breakdown: List[CategoryStats]
    priority_breakdown: List[PriorityStats]
    department_performance: List[DepartmentPerformance]
    sla_metrics: SLAMetrics
    recent_trend: TrendAnalysis
    top_performers: List[UserActivityStats]
    
    # Additional metrics
    avg_resolution_time_days: Optional[float] = None
    complaints_this_week: int = 0
    complaints_this_month: int = 0
    resolution_rate: float = 0.0


class ReportFilter(BaseModel):
    """Filter parameters for reports"""
    constituency_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_by: Optional[UUID] = None
    assigned_to: Optional[UUID] = None


class ExportRequest(BaseModel):
    """Request for data export"""
    format: str = Field(..., description="Export format: csv, excel, pdf")
    filters: Optional[ReportFilter] = None
    include_media: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "excel",
                "filters": {
                    "start_date": "2025-01-01",
                    "end_date": "2025-01-31",
                    "status": "closed"
                },
                "include_media": False
            }
        }


class ComparativeAnalysis(BaseModel):
    """Comparative analysis between periods"""
    current_period: ComplaintStats
    previous_period: ComplaintStats
    change_percentage: Dict[str, float]
    trend: str  # improved, declined, stable


class HeatmapData(BaseModel):
    """Geospatial heatmap data"""
    location: Dict[str, float]  # {lat, lng}
    complaint_count: int
    avg_resolution_days: Optional[float] = None
    category_distribution: Dict[str, int]


class AlertMetric(BaseModel):
    """Alert/notification for metrics"""
    alert_type: str  # sla_breach, high_volume, low_performance
    severity: str  # low, medium, high, critical
    message: str
    affected_count: int
    created_at: datetime
