"""
Metrics collection for Janasamparka
"""
import time
import psutil
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from fastapi import Response

from app.core.logging import performance_logger, database_logger


# Application info
app_info = Info('janasamparka_app_info', 'Application information')
app_info.info({
    'version': '1.0.0',
    'environment': 'production'  # This will be updated from config
})

# HTTP metrics
http_requests_total = Counter(
    'janasamparka_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'user_role']
)

http_request_duration = Histogram(
    'janasamparka_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'user_role'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0]
)

http_request_size = Histogram(
    'janasamparka_http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
)

http_response_size = Histogram(
    'janasamparka_http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status_code'],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000]
)

# Authentication metrics
auth_attempts_total = Counter(
    'janasamparka_auth_attempts_total',
    'Total authentication attempts',
    ['phone', 'success']
)

auth_failures_total = Counter(
    'janasamparka_auth_failures_total',
    'Total authentication failures',
    ['reason']
)

# Database metrics
db_connections_active = Gauge(
    'janasamparka_db_connections_active',
    'Active database connections'
)

db_query_duration = Histogram(
    'janasamparka_db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

db_queries_total = Counter(
    'janasamparka_db_queries_total',
    'Total database queries',
    ['query_type', 'success']
)

# Business metrics
complaints_total = Counter(
    'janasamparka_complaints_total',
    'Total complaints created',
    ['constituency_id', 'category', 'priority']
)

complaint_status_changes = Counter(
    'janasamparka_complaint_status_changes_total',
    'Total complaint status changes',
    ['old_status', 'new_status', 'changed_by_role']
)

users_total = Gauge(
    'janasamparka_users_total',
    'Total number of users',
    ['role', 'constituency_id', 'active']
)

departments_total = Gauge(
    'janasamparka_departments_total',
    'Total number of departments',
    ['constituency_id', 'active']
)

# System metrics
system_cpu_usage = Gauge(
    'janasamparka_system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage = Gauge(
    'janasamparka_system_memory_usage_bytes',
    'System memory usage in bytes'
)

system_disk_usage = Gauge(
    'janasamparka_system_disk_usage_bytes',
    'System disk usage in bytes',
    ['mount_point']
)

# File upload metrics
file_uploads_total = Counter(
    'janasamparka_file_uploads_total',
    'Total file uploads',
    ['file_type', 'success']
)

file_upload_size = Histogram(
    'janasamparka_file_upload_size_bytes',
    'File upload size in bytes',
    ['file_type'],
    buckets=[1000, 10000, 100000, 1000000, 10000000, 50000000]
)

# Cache metrics
cache_hits_total = Counter(
    'janasamparka_cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'janasamparka_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

cache_size = Gauge(
    'janasamparka_cache_size_bytes',
    'Cache size in bytes',
    ['cache_type']
)


def track_http_request(func):
    """Decorator to track HTTP request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Extract request info from args (this is simplified)
        method = "GET"  # Would extract from actual request
        endpoint = "/"  # Would extract from actual request
        user_role = "anonymous"  # Would extract from actual request
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200  # Would extract from actual response
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
                user_role=user_role
            ).inc()
            
            duration = time.time() - start_time
            http_request_duration.labels(
                method=method,
                endpoint=endpoint,
                user_role=user_role
            ).observe(duration)
            
            return result
            
        except Exception as e:
            status_code = 500  # Would extract from actual response
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
                user_role=user_role
            ).inc()
            
            duration = time.time() - start_time
            http_request_duration.labels(
                method=method,
                endpoint=endpoint,
                user_role=user_role
            ).observe(duration)
            
            raise
    
    return wrapper


def track_database_query(query_type: str):
    """Decorator to track database query metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record successful query
                db_queries_total.labels(
                    query_type=query_type,
                    success='true'
                ).inc()
                
                duration = time.time() - start_time
                db_query_duration.labels(query_type=query_type).observe(duration)
                
                # Log slow queries
                if duration > 1.0:
                    performance_logger.log_slow_query(
                        query=f"{query_type} query",
                        duration=duration
                    )
                
                return result
                
            except Exception as e:
                # Record failed query
                db_queries_total.labels(
                    query_type=query_type,
                    success='false'
                ).inc()
                
                duration = time.time() - start_time
                db_query_duration.labels(query_type=query_type).observe(duration)
                
                database_logger.logger.error(
                    "Database query failed",
                    query_type=query_type,
                    duration_ms=round(duration * 1000, 2),
                    error=str(e)
                )
                
                raise
        
        return wrapper
    return decorator


@contextmanager
def track_operation(operation_name: str, labels: Optional[Dict[str, str]] = None):
    """Context manager to track operation metrics"""
    start_time = time.time()
    labels = labels or {}
    
    try:
        yield
        duration = time.time() - start_time
        
        # Log successful operation
        performance_logger.logger.info(
            "Operation completed successfully",
            operation=operation_name,
            duration_ms=round(duration * 1000, 2),
            **labels
        )
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Log failed operation
        performance_logger.logger.error(
            "Operation failed",
            operation=operation_name,
            duration_ms=round(duration * 1000, 2),
            error=str(e),
            **labels
        )
        
        raise


class MetricsCollector:
    """Collect and update system metrics"""
    
    def __init__(self):
        self.last_update = 0
        self.update_interval = 30  # seconds
    
    def update_system_metrics(self):
        """Update system-level metrics"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.used)
            
            # Disk usage
            disk_partitions = psutil.disk_partitions()
            for partition in disk_partitions:
                usage = psutil.disk_usage(partition.mountpoint)
                system_disk_usage.labels(mount_point=partition.mountpoint).set(usage.used)
            
            self.last_update = current_time
            
        except Exception as e:
            performance_logger.logger.error(
                "Failed to update system metrics",
                error=str(e)
            )
    
    def record_complaint_created(self, constituency_id: str, category: str, priority: str):
        """Record complaint creation metric"""
        complaints_total.labels(
            constituency_id=constituency_id,
            category=category,
            priority=priority
        ).inc()
    
    def record_complaint_status_change(self, old_status: str, new_status: str, changed_by_role: str):
        """Record complaint status change metric"""
        complaint_status_changes.labels(
            old_status=old_status,
            new_status=new_status,
            changed_by_role=changed_by_role
        ).inc()
    
    def record_auth_attempt(self, phone: str, success: bool):
        """Record authentication attempt"""
        auth_attempts_total.labels(
            phone=phone,
            success=str(success).lower()
        ).inc()
        
        if not success:
            auth_failures_total.labels(reason="invalid_credentials").inc()
    
    def record_file_upload(self, file_type: str, success: bool, size_bytes: int):
        """Record file upload metric"""
        file_uploads_total.labels(
            file_type=file_type,
            success=str(success).lower()
        ).inc()
        
        if success:
            file_upload_size.labels(file_type=file_type).observe(size_bytes)
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        cache_hits_total.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        cache_misses_total.labels(cache_type=cache_type).inc()


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_response() -> Response:
    """Return Prometheus metrics"""
    # Update system metrics before returning
    metrics_collector.update_system_metrics()
    
    metrics_data = generate_latest()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )


def setup_metrics(app):
    """Setup metrics collection for FastAPI app"""
    from app.core.config import settings
    
    # Update app info
    app_info.info({
        'version': settings.APP_VERSION,
        'environment': settings.ENVIRONMENT
    })
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics():
        return get_metrics_response()
    
    return app
