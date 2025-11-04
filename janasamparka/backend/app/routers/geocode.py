"""
Geocoding router - GPS-based ward detection
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.core.database import get_db
from app.models.ward import Ward

router = APIRouter()


@router.get("/ward")
async def detect_ward_from_coordinates(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    db: Session = Depends(get_db)
):
    """
    Detect ward from GPS coordinates using PostGIS spatial queries
    
    Note: Requires ward.boundary column to be populated with GeoJSON polygons
    """
    try:
        # Create point from coordinates (PostGIS uses lng, lat order)
        # Note: This requires PostGIS extension and geometry column in wards table
        from geoalchemy2.functions import ST_Contains, ST_MakePoint, ST_Distance
        from geoalchemy2 import Geometry
        
        # Create point geometry
        point = ST_MakePoint(lng, lat)
        
        # Find ward containing this point
        ward = db.query(Ward).filter(
            ST_Contains(Ward.boundary, point)
        ).first()
        
        if ward:
            return {
                "success": True,
                "ward_id": str(ward.id),
                "ward_name": ward.name,
                "ward_number": ward.ward_number,
                "constituency_id": str(ward.constituency_id),
                "lat": lat,
                "lng": lng,
                "accuracy": "high"
            }
        
        # If no exact match, find nearest ward
        nearest_wards = db.query(
            Ward,
            ST_Distance(Ward.boundary, point).label('distance')
        ).order_by('distance').limit(3).all()
        
        if nearest_wards:
            suggestions = [
                {
                    "ward_id": str(ward.id),
                    "ward_name": ward.name,
                    "ward_number": ward.ward_number,
                    "distance_km": round(distance * 111.32, 2)  # Convert degrees to km (approximate)
                }
                for ward, distance in nearest_wards
            ]
            
            return {
                "success": False,
                "error": "NO_EXACT_MATCH",
                "message": "No ward found for exact location. Here are nearby wards:",
                "lat": lat,
                "lng": lng,
                "suggestions": suggestions
            }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ward found for these coordinates. Please select manually."
        )
        
    except ImportError:
        # GeoAlchemy2 not installed or PostGIS not configured
        # Fallback: Simple distance calculation without spatial database
        
        # Get all wards with lat/lng (if you have ward center coordinates)
        wards = db.query(Ward).all()
        
        if not wards:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No wards found in database"
            )
        
        # For now, return a message that PostGIS is not configured
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Ward detection requires PostGIS to be configured. Please select ward manually for now."
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting ward: {str(e)}"
        )


@router.get("/reverse")
async def reverse_geocode(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude")
):
    """
    Reverse geocode coordinates to get address
    
    Note: This would typically integrate with Google Maps Geocoding API
    or OpenStreetMap Nominatim API
    """
    # TODO: Integrate with geocoding service
    # For now, return mock data
    
    return {
        "lat": lat,
        "lng": lng,
        "formatted_address": "Location address would appear here",
        "note": "Reverse geocoding requires external API integration"
    }
