"""
Database management router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import database

router = APIRouter()

# Include all database endpoints
router.include_router(database.router, prefix="")
