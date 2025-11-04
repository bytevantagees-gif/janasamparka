"""
Structured logging configuration for Janasamparka
"""
import logging
import logging.config
import sys
import json
import time
from typing import Any, Dict
from datetime import datetime
from pathlib import Path

import structlog
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp if not present
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Add application info
        log_record['application'] = settings.APP_NAME
        log_record['environment'] = settings.ENVIRONMENT
        log_record['version'] = settings.APP_VERSION
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        if hasattr(record, 'constituency_id'):
            log_record['constituency_id'] = record.constituency_id


class ContextFilter(logging.Filter):
    """Filter to add context information to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record"""
        record.app_name = settings.APP_NAME
        record.environment = settings.ENVIRONMENT
        return True


def setup_logging():
    """Setup structured logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            },
            "console": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "filters": {
            "context": {
                "()": ContextFilter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "console",
                "filters": ["context"],
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "json",
                "filters": ["context"],
                "filename": f"logs/{settings.ENVIRONMENT}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filters": ["context"],
                "filename": f"logs/{settings.ENVIRONMENT}-error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"]
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Setup Sentry if configured
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                sentry_logging,
                SqlalchemyIntegration(),
                FastApiIntegration(auto_enabling_integrations=False)
            ],
            environment=settings.ENVIRONMENT,
            release=settings.APP_VERSION,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1
        )


class RequestLogger:
    """Logger for HTTP requests with context"""
    
    def __init__(self):
        self.logger = structlog.get_logger("request")
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration: float, user_id: str = None, 
                   request_id: str = None, **kwargs):
        """Log HTTP request"""
        self.logger.info(
            "HTTP request completed",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2),
            user_id=user_id,
            request_id=request_id,
            **kwargs
        )
    
    def log_error(self, method: str, path: str, error: Exception,
                  user_id: str = None, request_id: str = None, **kwargs):
        """Log HTTP request error"""
        self.logger.error(
            "HTTP request failed",
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            user_id=user_id,
            request_id=request_id,
            **kwargs
        )


class DatabaseLogger:
    """Logger for database operations"""
    
    def __init__(self):
        self.logger = structlog.get_logger("database")
    
    def log_query(self, query: str, duration: float, 
                 affected_rows: int = None, **kwargs):
        """Log database query"""
        self.logger.debug(
            "Database query executed",
            query=query[:200] + "..." if len(query) > 200 else query,
            duration_ms=round(duration * 1000, 2),
            affected_rows=affected_rows,
            **kwargs
        )
    
    def log_connection_error(self, error: Exception, **kwargs):
        """Log database connection error"""
        self.logger.error(
            "Database connection failed",
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )


class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_authentication_attempt(self, phone: str, success: bool, 
                                   ip_address: str = None, **kwargs):
        """Log authentication attempt"""
        level = "info" if success else "warning"
        getattr(self.logger, level)(
            "Authentication attempt",
            phone=phone,
            success=success,
            ip_address=ip_address,
            **kwargs
        )
    
    def log_authorization_failure(self, user_id: str, resource: str, 
                                 action: str, **kwargs):
        """Log authorization failure"""
        self.logger.warning(
            "Authorization failed",
            user_id=user_id,
            resource=resource,
            action=action,
            **kwargs
        )
    
    def log_suspicious_activity(self, activity: str, user_id: str = None,
                               ip_address: str = None, **kwargs):
        """Log suspicious activity"""
        self.logger.error(
            "Suspicious activity detected",
            activity=activity,
            user_id=user_id,
            ip_address=ip_address,
            **kwargs
        )


class BusinessLogger:
    """Logger for business events"""
    
    def __init__(self):
        self.logger = structlog.get_logger("business")
    
    def log_complaint_created(self, complaint_id: str, user_id: str,
                             constituency_id: str, category: str, **kwargs):
        """Log complaint creation"""
        self.logger.info(
            "Complaint created",
            complaint_id=complaint_id,
            user_id=user_id,
            constituency_id=constituency_id,
            category=category,
            **kwargs
        )
    
    def log_complaint_status_change(self, complaint_id: str, old_status: str,
                                   new_status: str, changed_by: str, **kwargs):
        """Log complaint status change"""
        self.logger.info(
            "Complaint status changed",
            complaint_id=complaint_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            **kwargs
        )
    
    def log_department_assignment(self, complaint_id: str, department_id: str,
                                  assigned_by: str, **kwargs):
        """Log department assignment"""
        self.logger.info(
            "Complaint assigned to department",
            complaint_id=complaint_id,
            department_id=department_id,
            assigned_by=assigned_by,
            **kwargs
        )


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_slow_query(self, query: str, duration: float, threshold: float = 1.0, **kwargs):
        """Log slow database query"""
        self.logger.warning(
            "Slow query detected",
            query=query[:200] + "..." if len(query) > 200 else query,
            duration_ms=round(duration * 1000, 2),
            threshold_ms=round(threshold * 1000, 2),
            **kwargs
        )
    
    def log_memory_usage(self, memory_mb: float, threshold_mb: float = 500, **kwargs):
        """Log memory usage"""
        level = "warning" if memory_mb > threshold_mb else "info"
        getattr(self.logger, level)(
            "Memory usage recorded",
            memory_mb=round(memory_mb, 2),
            threshold_mb=threshold_mb,
            **kwargs
        )
    
    def log_api_response_time(self, endpoint: str, method: str, duration: float,
                             threshold: float = 1.0, **kwargs):
        """Log API response time"""
        level = "warning" if duration > threshold else "info"
        getattr(self.logger, level)(
            "API response time recorded",
            endpoint=endpoint,
            method=method,
            duration_ms=round(duration * 1000, 2),
            threshold_ms=round(threshold * 1000, 2),
            **kwargs
        )


# Initialize loggers
request_logger = RequestLogger()
database_logger = DatabaseLogger()
security_logger = SecurityLogger()
business_logger = BusinessLogger()
performance_logger = PerformanceLogger()

# Get structured logger
logger = structlog.get_logger(__name__)
