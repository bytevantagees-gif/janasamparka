"""
Optimized database utilities for Janasamparka
"""
from typing import List, Optional, Dict, Any, Type, TypeVar, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, func, desc, asc, text
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import database_logger, performance_logger
from app.core.metrics import track_database_query

T = TypeVar('T')


class OptimizedQuery:
    """Optimized database query builder"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
        self.query = db.query(model)
        self._eager_loads = []
        self._filters = []
        self._order_by = []
        self._limit_count = None
        self._offset_count = None
    
    def eager_load(self, *relationships):
        """Add eager loading for relationships"""
        self._eager_loads.extend(relationships)
        return self
    
    def filter(self, *criteria):
        """Add filter criteria"""
        self._filters.extend(criteria)
        return self
    
    def order_by(self, *criterion):
        """Add ordering"""
        self._order_by.extend(criterion)
        return self
    
    def limit(self, count: int):
        """Set limit"""
        self._limit_count = count
        return self
    
    def offset(self, count: int):
        """Set offset"""
        self._offset_count = count
        return self
    
    def execute(self) -> List[T]:
        """Execute the optimized query"""
        start_time = datetime.utcnow()
        
        try:
            # Apply eager loads
            for relationship in self._eager_loads:
                if hasattr(relationship, 'prop'):
                    # Handle SQLAlchemy relationship objects
                    if relationship.prop.lazy == 'selectin':
                        self.query = self.query.options(selectinload(relationship))
                    else:
                        self.query = self.query.options(joinedload(relationship))
            
            # Apply filters
            for criterion in self._filters:
                self.query = self.query.filter(criterion)
            
            # Apply ordering
            for criterion in self._order_by:
                self.query = self.query.order_by(criterion)
            
            # Apply pagination
            if self._limit_count:
                self.query = self.query.limit(self._limit_count)
            if self._offset_count:
                self.query = self.query.offset(self._offset_count)
            
            result = self.query.all()
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            database_logger.log_query(
                query=str(self.query),
                duration=duration,
                affected_rows=len(result)
            )
            
            return result
            
        except SQLAlchemyError as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            database_logger.log_connection_error(e)
            raise
    
    def first(self) -> Optional[T]:
        """Execute query and return first result"""
        return self.limit(1).execute()[0] if self.execute() else None
    
    def count(self) -> int:
        """Execute count query"""
        start_time = datetime.utcnow()
        
        try:
            # Apply filters
            for criterion in self._filters:
                self.query = self.query.filter(criterion)
            
            count = self.query.count()
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            database_logger.log_query(
                query=f"COUNT({str(self.query)})",
                duration=duration,
                affected_rows=count
            )
            
            return count
            
        except SQLAlchemyError as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            database_logger.log_connection_error(e)
            raise


class ComplaintQueryBuilder:
    """Specialized query builder for complaints"""
    
    @staticmethod
    def get_complaints_list(
        db: Session,
        constituency_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        department_id: Optional[str] = None,
        user_id: Optional[str] = None,
        is_emergency: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Get optimized complaints list with filters"""
        
        from app.models.complaint import Complaint
        
        start_time = datetime.utcnow()
        
        try:
            # Build base query with optimized joins
            query = db.query(Complaint).options(
                joinedload(Complaint.user),
                joinedload(Complaint.department),
                joinedload(Complaint.constituency),
                selectinload(Complaint.media),
                selectinload(Complaint.status_logs)
            )
            
            # Apply filters efficiently
            filters = []
            
            if constituency_id:
                filters.append(Complaint.constituency_id == constituency_id)
            
            if status:
                if isinstance(status, list):
                    filters.append(Complaint.status.in_(status))
                else:
                    filters.append(Complaint.status == status)
            
            if priority:
                if isinstance(priority, list):
                    filters.append(Complaint.priority.in_(priority))
                else:
                    filters.append(Complaint.priority == priority)
            
            if category:
                if isinstance(category, list):
                    filters.append(Complaint.category.in_(category))
                else:
                    filters.append(Complaint.category == category)
            
            if department_id:
                filters.append(Complaint.dept_id == department_id)
            
            if user_id:
                filters.append(Complaint.user_id == user_id)
            
            if is_emergency is not None:
                filters.append(Complaint.is_emergency == is_emergency)
            
            if date_from:
                filters.append(Complaint.created_at >= date_from)
            
            if date_to:
                filters.append(Complaint.created_at <= date_to)
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Apply sorting
            sort_column = getattr(Complaint, sort_by, Complaint.created_at)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)
            
            # Execute query
            complaints = query.all()
            
            # Calculate pagination info
            pages = (total + size - 1) // size
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            performance_logger.log_api_response_time(
                endpoint="complaints_list",
                method="GET",
                duration=duration
            )
            
            return {
                "items": [complaint.to_dict() for complaint in complaints],
                "total": total,
                "page": page,
                "size": size,
                "pages": pages
            }
            
        except SQLAlchemyError as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            database_logger.log_connection_error(e)
            raise
    
    @staticmethod
    def get_complaint_stats(
        db: Session,
        constituency_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get optimized complaint statistics"""
        
        from app.models.complaint import Complaint, ComplaintStatus, ComplaintPriority
        
        start_time = datetime.utcnow()
        
        try:
            # Build base query
            query = db.query(Complaint)
            
            # Apply filters
            filters = []
            if constituency_id:
                filters.append(Complaint.constituency_id == constituency_id)
            if date_from:
                filters.append(Complaint.created_at >= date_from)
            if date_to:
                filters.append(Complaint.created_at <= date_to)
            
            if filters:
                query = query.filter(and_(*filters))
            
            # Get statistics using efficient aggregate queries
            total_complaints = query.count()
            
            # Status breakdown
            status_stats = db.query(
                Complaint.status,
                func.count(Complaint.id).label('count')
            ).filter(and_(*filters) if filters else True).group_by(Complaint.status).all()
            
            # Priority breakdown
            priority_stats = db.query(
                Complaint.priority,
                func.count(Complaint.id).label('count')
            ).filter(and_(*filters) if filters else True).group_by(Complaint.priority).all()
            
            # Category breakdown
            category_stats = db.query(
                Complaint.category,
                func.count(Complaint.id).label('count')
            ).filter(and_(*filters) if filters else True).group_by(Complaint.category).all()
            
            # Resolution metrics
            resolved_complaints = query.filter(Complaint.status == ComplaintStatus.RESOLVED).count()
            avg_resolution_time = db.query(
                func.avg(
                    func.extract('epoch', Complaint.resolved_at - Complaint.created_at)
                ).label('avg_seconds')
            ).filter(
                and_(*filters, Complaint.status == ComplaintStatus.RESOLVED) if filters else
                Complaint.status == ComplaintStatus.RESOLVED
            ).scalar()
            
            # Compile results
            stats = {
                "total_complaints": total_complaints,
                "by_status": {status: count for status, count in status_stats},
                "by_priority": {priority: count for priority, count in priority_stats},
                "by_category": {category: count for category, count in category_stats},
                "resolved": resolved_complaints,
                "resolution_rate": round(resolved_complaints / total_complaints * 100, 2) if total_complaints > 0 else 0,
                "avg_resolution_hours": round(avg_resolution_time / 3600, 2) if avg_resolution_time else 0
            }
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds()
            performance_logger.log_api_response_time(
                endpoint="complaint_stats",
                method="GET",
                duration=duration
            )
            
            return stats
            
        except SQLAlchemyError as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            database_logger.log_connection_error(e)
            raise


class DatabaseOptimizer:
    """Database optimization utilities"""
    
    @staticmethod
    def analyze_table_performance(db: Session, table_name: str) -> Dict[str, Any]:
        """Analyze table performance metrics"""
        try:
            # Get table statistics
            stats_query = text(f"""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables 
                WHERE tablename = :table_name
            """)
            
            result = db.execute(stats_query, {"table_name": table_name}).fetchone()
            
            if result:
                return dict(result._mapping)
            
            return {}
            
        except Exception as e:
            database_logger.logger.error("Failed to analyze table performance", 
                                       table_name=table_name, error=str(e))
            return {}
    
    @staticmethod
    def get_slow_queries(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slow queries from PostgreSQL statistics"""
        try:
            # This requires pg_stat_statements extension
            slow_queries_query = text(f"""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY mean_time DESC 
                LIMIT :limit
            """)
            
            results = db.execute(slow_queries_query, {"limit": limit}).fetchall()
            
            return [dict(row._mapping) for row in results] if results else []
            
        except Exception as e:
            database_logger.logger.error("Failed to get slow queries", error=str(e))
            return []
    
    @staticmethod
    def vacuum_table(db: Session, table_name: str) -> bool:
        """Run VACUUM on a table to reclaim space"""
        try:
            db.execute(text(f"VACUUM ANALYZE {table_name}"))
            db.commit()
            database_logger.logger.info("Table vacuumed successfully", table_name=table_name)
            return True
            
        except Exception as e:
            db.rollback()
            database_logger.logger.error("Failed to vacuum table", 
                                       table_name=table_name, error=str(e))
            return False
    
    @staticmethod
    def reindex_table(db: Session, table_name: str) -> bool:
        """Reindex all indexes on a table"""
        try:
            db.execute(text(f"REINDEX TABLE {table_name}"))
            db.commit()
            database_logger.logger.info("Table reindexed successfully", table_name=table_name)
            return True
            
        except Exception as e:
            db.rollback()
            database_logger.logger.error("Failed to reindex table", 
                                       table_name=table_name, error=str(e))
            return False


def get_optimized_query(db: Session, model: Type[T]) -> OptimizedQuery:
    """Get an optimized query builder"""
    return OptimizedQuery(db, model)
