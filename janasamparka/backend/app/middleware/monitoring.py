"""
Monitoring middleware for FastAPI application
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import request_logger, performance_logger
from app.core.auth import get_current_user


class RequestMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor HTTP requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get start time
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Try to get user info (if authenticated)
        user_id = None
        constituency_id = None
        try:
            # This will work if the request has valid auth
            current_user = await get_current_user(
                request.headers.get("authorization"),
                None  # We don't have db session here, but that's ok for monitoring
            )
            if current_user:
                user_id = str(current_user.id)
                constituency_id = str(current_user.constituency_id) if current_user.constituency_id else None
        except:
            pass  # User not authenticated, that's fine
        
        # Log request start
        request_logger.logger.info(
            "HTTP request started",
            method=request.method,
            path=request.url.path,
            query_string=str(request.url.query) if request.url.query else None,
            client_ip=client_ip,
            user_agent=user_agent,
            user_id=user_id,
            request_id=request_id
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful request
            request_logger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
                user_id=user_id,
                request_id=request_id,
                client_ip=client_ip,
                constituency_id=constituency_id
            )
            
            # Log performance metrics
            performance_logger.log_api_response_time(
                endpoint=request.url.path,
                method=request.method,
                duration=duration
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            request_logger.log_error(
                method=request.method,
                path=request.url.path,
                error=e,
                user_id=user_id,
                request_id=request_id,
                client_ip=client_ip,
                duration=duration
            )
            
            # Re-raise the exception
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add HSTS header in production
        from app.core.config import settings
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.SECURITY_HSTS_SECONDS}; "
                f"includeSubDomains={str(settings.SECURITY_HSTS_INCLUDE_SUBDOMAINS).lower()}; "
                f"preload={str(settings.SECURITY_HSTS_PRELOAD).lower()}"
            )
        
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        cutoff_time = current_time - 60
        self.request_counts = {
            ip: times for ip, times in self.request_counts.items()
            if any(t > cutoff_time for t in times)
        }
        
        # Check rate limit
        if client_ip in self.request_counts:
            recent_requests = [t for t in self.request_counts[client_ip] if t > cutoff_time]
            if len(recent_requests) >= self.requests_per_minute:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": "60"}
                )
            self.request_counts[client_ip] = recent_requests + [current_time]
        else:
            self.request_counts[client_ip] = [current_time]
        
        return await call_next(request)


class DatabaseMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor database performance"""
    
    def __init__(self, app, slow_query_threshold: float = 1.0):
        super().__init__(app)
        self.slow_query_threshold = slow_query_threshold
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # This is a simplified version - in production you'd want to use
        # SQLAlchemy event listeners for more accurate monitoring
        return await call_next(request)


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware to handle health checks without logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in ["/health", "/health/detailed"]:
            # Skip monitoring for health checks
            return await call_next(request)
        
        return await call_next(request)
