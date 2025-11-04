"""
Data export utilities for generating CSV, Excel, and PDF reports
"""
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.schemas.analytics import ReportFilter


class ExportService:
    """Service for exporting data in various formats"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def filter_complaints(self, filters: Optional[ReportFilter] = None) -> List[Complaint]:
        """
        Apply filters and return complaint queryset
        """
        query = self.db.query(Complaint)
        
        if not filters:
            return query.all()
        
        # Apply filters
        if filters.constituency_id:
            query = query.filter(Complaint.constituency_id == filters.constituency_id)
        
        if filters.department_id:
            query = query.filter(Complaint.dept_id == filters.department_id)
        
        if filters.category:
            query = query.filter(Complaint.category == filters.category)
        
        if filters.priority:
            query = query.filter(Complaint.priority == filters.priority)
        
        if filters.status:
            query = query.filter(Complaint.status == filters.status)
        
        if filters.start_date:
            query = query.filter(Complaint.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Complaint.created_at <= filters.end_date)
        
        if filters.created_by:
            query = query.filter(Complaint.created_by == filters.created_by)
        
        if filters.assigned_to:
            query = query.filter(Complaint.assigned_to == filters.assigned_to)
        
        return query.all()
    
    def export_to_csv(self, filters: Optional[ReportFilter] = None) -> str:
        """
        Export complaints to CSV format
        Returns CSV content as string
        """
        complaints = self.filter_complaints(filters)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID',
            'Title',
            'Category',
            'Priority',
            'Status',
            'Created Date',
            'Resolved Date',
            'Closed Date',
            'Constituency',
            'Department',
            'Location',
            'Description'
        ])
        
        # Write data
        for complaint in complaints:
            # Get constituency name if available
            constituency_name = ''
            if complaint.constituency_id:
                from app.models.constituency import Constituency
                constituency = self.db.query(Constituency).filter(
                    Constituency.id == complaint.constituency_id
                ).first()
                if constituency:
                    constituency_name = constituency.name
            
            # Get department name if available
            department_name = ''
            if complaint.dept_id:
                from app.models.department import Department
                dept = self.db.query(Department).filter(
                    Department.id == complaint.dept_id
                ).first()
                if dept:
                    department_name = dept.name
            
            writer.writerow([
                str(complaint.id),
                complaint.title,
                complaint.category,
                complaint.priority,
                complaint.status,
                complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                complaint.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if complaint.resolved_at else '',
                complaint.closed_at.strftime('%Y-%m-%d %H:%M:%S') if complaint.closed_at else '',
                constituency_name,
                department_name,
                complaint.location_description or '',
                complaint.description[:200] + '...' if len(complaint.description) > 200 else complaint.description
            ])
        
        return output.getvalue()
    
    def export_to_dict(self, filters: Optional[ReportFilter] = None) -> List[Dict[str, Any]]:
        """
        Export complaints to dictionary format (for JSON or Excel)
        """
        complaints = self.filter_complaints(filters)
        
        data = []
        for complaint in complaints:
            # Calculate resolution time if resolved
            resolution_time_hours = None
            if complaint.resolved_at:
                delta = complaint.resolved_at - complaint.created_at
                resolution_time_hours = round(delta.total_seconds() / 3600, 2)
            
            # Get constituency name
            constituency_name = None
            if complaint.constituency_id:
                from app.models.constituency import Constituency
                constituency = self.db.query(Constituency).filter(
                    Constituency.id == complaint.constituency_id
                ).first()
                if constituency:
                    constituency_name = constituency.name
            
            # Get department name
            department_name = None
            if complaint.dept_id:
                from app.models.department import Department
                dept = self.db.query(Department).filter(
                    Department.id == complaint.dept_id
                ).first()
                if dept:
                    department_name = dept.name
            
            data.append({
                'id': str(complaint.id),
                'title': complaint.title,
                'category': complaint.category,
                'priority': complaint.priority,
                'status': complaint.status,
                'created_at': complaint.created_at.isoformat(),
                'resolved_at': complaint.resolved_at.isoformat() if complaint.resolved_at else None,
                'closed_at': complaint.closed_at.isoformat() if complaint.closed_at else None,
                'resolution_time_hours': resolution_time_hours,
                'constituency_id': str(complaint.constituency_id) if complaint.constituency_id else None,
                'constituency_name': constituency_name,
                'department_id': str(complaint.dept_id) if complaint.dept_id else None,
                'department_name': department_name,
                'location_description': complaint.location_description,
                'latitude': float(complaint.lat) if complaint.lat else None,
                'longitude': float(complaint.lng) if complaint.lng else None,
                'description': complaint.description,
                'work_approved': complaint.work_approved,
                'approval_comments': complaint.approval_comments,
            })
        
        return data
    
    def generate_summary_report(self, filters: Optional[ReportFilter] = None) -> Dict[str, Any]:
        """
        Generate a summary report with statistics
        """
        complaints = self.filter_complaints(filters)
        total = len(complaints)
        
        if total == 0:
            return {
                'total_complaints': 0,
                'status_distribution': {},
                'category_distribution': {},
                'priority_distribution': {},
                'avg_resolution_time_hours': None
            }
        
        # Status distribution
        status_dist = {}
        for complaint in complaints:
            status_dist[complaint.status] = status_dist.get(complaint.status, 0) + 1
        
        # Category distribution
        category_dist = {}
        for complaint in complaints:
            category_dist[complaint.category] = category_dist.get(complaint.category, 0) + 1
        
        # Priority distribution
        priority_dist = {}
        for complaint in complaints:
            priority_dist[complaint.priority] = priority_dist.get(complaint.priority, 0) + 1
        
        # Average resolution time
        resolved_complaints = [c for c in complaints if c.resolved_at]
        if resolved_complaints:
            total_hours = sum(
                (c.resolved_at - c.created_at).total_seconds() / 3600
                for c in resolved_complaints
            )
            avg_resolution_hours = round(total_hours / len(resolved_complaints), 2)
        else:
            avg_resolution_hours = None
        
        return {
            'total_complaints': total,
            'status_distribution': status_dist,
            'category_distribution': category_dist,
            'priority_distribution': priority_dist,
            'avg_resolution_time_hours': avg_resolution_hours,
            'resolved_count': len(resolved_complaints),
            'resolution_rate': round((len(resolved_complaints) / total) * 100, 2) if total > 0 else 0,
            'date_range': {
                'start': min(c.created_at for c in complaints).isoformat() if complaints else None,
                'end': max(c.created_at for c in complaints).isoformat() if complaints else None
            }
        }


def create_excel_report(data: List[Dict], summary: Dict) -> bytes:
    """
    Create Excel report with data and summary
    Requires openpyxl or xlsxwriter library
    
    TODO: Implement Excel generation
    Returns placeholder for now
    """
    # This would use openpyxl or xlsxwriter to create Excel file
    # For now, return CSV-like format
    raise NotImplementedError("Excel export requires openpyxl library. Use CSV for now.")


def create_pdf_report(data: List[Dict], summary: Dict) -> bytes:
    """
    Create PDF report with data and summary
    Requires reportlab library
    
    TODO: Implement PDF generation
    Returns placeholder for now
    """
    # This would use reportlab to create PDF
    raise NotImplementedError("PDF export requires reportlab library. Use CSV for now.")
