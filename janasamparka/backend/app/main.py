"""
Main FastAPI application with monitoring and logging
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import setup_logging, logger
from app.core.metrics import setup_metrics
from app.middleware.monitoring import (
    RequestMonitoringMiddleware,
    SecurityHeadersMiddleware,
    HealthCheckMiddleware
)
from app.routers import (
    auth, complaints, users, constituencies, departments, wards, polls, 
    media, geocode, map as map_router, ai, bhoomi, analytics, ratings, 
    case_management, budgets, faqs, database, panchayats, interventions, 
    department_types, news, citizen_engagement, votebank_engagement, conference_chat, forum, social_feed
)
from pathlib import Path


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ಜನಮನಾ ಸಂಪರ್ಕ | JanaMana Samparka API", version=settings.APP_VERSION)
    
    # Setup logging
    setup_logging()
    
    # Create database tables
    # Note: Tables are created by Alembic migrations, not by create_all()
    # try:
    #     Base.metadata.create_all(bind=engine)
    #     logger.info("Database tables created successfully")
    # except Exception as e:
    #     logger.error("Failed to create database tables", error=str(e))
    #     raise
    
    # Setup metrics
    setup_metrics(app)
    logger.info("Metrics collection initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ಜನಮನಾ ಸಂಪರ್ಕ | JanaMana Samparka API")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add monitoring middleware
app.add_middleware(HealthCheckMiddleware)
app.add_middleware(RequestMonitoringMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(constituencies.router, prefix="/api/constituencies", tags=["Constituencies"])
app.include_router(departments.router, prefix="/api/departments", tags=["Departments"])
app.include_router(department_types.router, prefix="/api/department-types", tags=["Department Types"])
app.include_router(wards.router, prefix="/api/wards", tags=["Wards"])
app.include_router(polls.router, prefix="/api/polls", tags=["Polls"])
app.include_router(media.router, prefix="/api/media", tags=["Media"])
app.include_router(geocode.router, prefix="/api/geocode", tags=["Geocoding"])
app.include_router(map_router.router, prefix="/api/map", tags=["Map"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI & ML"])
app.include_router(bhoomi.router, prefix="/api/bhoomi", tags=["Bhoomi Land Records"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics & Reporting"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Citizen Ratings & Feedback"])
app.include_router(interventions.router, prefix="/api/interventions", tags=["Satisfaction Interventions"])
app.include_router(case_management.router, tags=["Case Management"])
app.include_router(budgets.router, tags=["Budget Tracking"])
app.include_router(faqs.router, tags=["FAQ & Knowledge Base"])
app.include_router(database.router, prefix="/api/database", tags=["Database Management"])
app.include_router(panchayats.router, tags=["Panchayats"])
app.include_router(news.router, prefix="/api/news", tags=["News, Schedule & Ticker"])
app.include_router(citizen_engagement.router, prefix="/api/engagement", tags=["Citizen Engagement"])
app.include_router(conference_chat.router, prefix="/api/chat", tags=["Conference Chat"])
app.include_router(votebank_engagement.router, prefix="/api/votebank", tags=["Votebank Engagement"])
app.include_router(forum.router, prefix="/api/forum", tags=["Knowledge Forum"])
app.include_router(social_feed.router, prefix="/api/social", tags=["MLA Social Feed"])

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
(uploads_dir / "media").mkdir(exist_ok=True)
(uploads_dir / "profile_photos").mkdir(exist_ok=True)

# Mount static files for serving uploaded media
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }
    
    # Check database connectivity
    try:
        from app.core.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        health_status["database"] = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Check Redis connectivity if configured
    try:
        if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["redis"] = "healthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        health_status["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    return health_status


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    logger.info("Detailed health check endpoint accessed")
    
    # Get basic health
    basic_health = await health_check()
    
    # Add system metrics
    try:
        import psutil
        
        detailed_health = {
            **basic_health,
            "system": {
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "memory_usage_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2),
                "disk_usage_gb": round(psutil.disk_usage('/').used / 1024 / 1024 / 1024, 2),
                "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
            }
        }
        
        return detailed_health
        
    except Exception as e:
        logger.error("Failed to get system metrics", error=str(e))
        return {
            **basic_health,
            "system": {"error": "Failed to collect system metrics"}
        }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting development server")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_config=None  # Use our custom logging
    )
