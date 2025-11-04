"""
Map router - GeoJSON endpoints for map visualization
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import json

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.models.complaint import Complaint, ComplaintStatus
from app.models.ward import Ward
from app.models.user import User

router = APIRouter()


@router.get("/complaints")
async def get_complaints_geojson(
    status: Optional[str] = None,
    category: Optional[str] = None,
    ward_id: Optional[UUID] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get all complaints as GeoJSON FeatureCollection
    Suitable for map visualization
    Non-admin users only see complaints from their own constituency
    """
    # Build query
    query = db.query(Complaint).filter(
        Complaint.lat.isnot(None),
        Complaint.lng.isnot(None)
    )
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    # Apply filters
    if status:
        query = query.filter(Complaint.status == status)
    
    if category:
        query = query.filter(Complaint.category == category)
    
    if ward_id:
        query = query.filter(Complaint.ward_id == ward_id)
    
    if date_from:
        query = query.filter(Complaint.created_at >= date_from)
    
    if date_to:
        query = query.filter(Complaint.created_at <= date_to)
    
    complaints = query.all()
    
    # Convert to GeoJSON FeatureCollection
    features = []
    for complaint in complaints:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(complaint.lng), float(complaint.lat)]  # [lng, lat] for GeoJSON
            },
            "properties": {
                "id": str(complaint.id),
                "title": complaint.title,
                "description": complaint.description,
                "category": complaint.category,
                "status": complaint.status.value if hasattr(complaint.status, 'value') else complaint.status,
                "priority": complaint.priority.value if hasattr(complaint.priority, 'value') else complaint.priority,
                "location_description": complaint.location_description,
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
                "ward_id": str(complaint.ward_id) if complaint.ward_id else None,
                "dept_id": str(complaint.dept_id) if complaint.dept_id else None,
                "user_id": str(complaint.user_id) if complaint.user_id else None
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "count": len(features),
            "filters": {
                "status": status,
                "category": category,
                "ward_id": str(ward_id) if ward_id else None,
                "date_from": date_from,
                "date_to": date_to
            }
        }
    }


@router.get("/wards")
async def get_wards_geojson(
    constituency_id: Optional[UUID] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get ward boundaries as GeoJSON FeatureCollection
    Non-admin users only see wards from their own constituency
    
    Note: Requires ward.boundary column to be populated with GeoJSON polygons
    """
    query = db.query(Ward)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Ward.constituency_id == constituency_filter)
    elif constituency_id:  # Only allow explicit filter if admin
        query = query.filter(Ward.constituency_id == constituency_id)
    
    wards = query.all()
    
    features = []
    for ward in wards:
        # Check if ward has boundary data
        if hasattr(ward, 'boundary') and ward.boundary:
            try:
                # If boundary is stored as GeoJSON string
                if isinstance(ward.boundary, str):
                    geometry = json.loads(ward.boundary)
                else:
                    # If boundary is PostGIS geometry, convert to GeoJSON
                    # This requires geoalchemy2
                    from geoalchemy2.shape import to_shape
                    from shapely.geometry import mapping
                    shape = to_shape(ward.boundary)
                    geometry = mapping(shape)
            except:
                # If no valid boundary, create a point geometry as placeholder
                geometry = {
                    "type": "Point",
                    "coordinates": [0, 0]  # Placeholder
                }
        else:
            # No boundary data available
            continue
        
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": str(ward.id),
                "name": ward.name,
                "ward_number": ward.ward_number,
                "taluk": ward.taluk,
                "constituency_id": str(ward.constituency_id),
                "population": ward.population,
                "area_sq_km": float(ward.area_sq_km) if ward.area_sq_km else None
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "count": len(features),
            "constituency_id": str(constituency_id) if constituency_id else None
        }
    }


@router.get("/heatmap")
async def get_heatmap_data(
    status: Optional[str] = None,
    category: Optional[str] = None,
    intensity_field: str = "count",
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get heatmap data for complaint density visualization
    Returns array of [lat, lng, intensity] for leaflet.heat
    Non-admin users only see data from their own constituency
    """
    query = db.query(Complaint).filter(
        Complaint.lat.isnot(None),
        Complaint.lng.isnot(None)
    )
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    # Apply filters
    if status:
        query = query.filter(Complaint.status == status)
    
    if category:
        query = query.filter(Complaint.category == category)
    
    complaints = query.all()
    
    # Build heatmap data array
    heatmap_data = []
    for complaint in complaints:
        # Intensity can be based on different factors
        if intensity_field == "priority":
            intensity_map = {"low": 0.3, "medium": 0.6, "high": 0.9, "urgent": 1.0}
            priority = complaint.priority.value if hasattr(complaint.priority, 'value') else complaint.priority
            intensity = intensity_map.get(priority, 0.5)
        else:
            # Default: uniform intensity
            intensity = 1.0
        
        heatmap_data.append([
            float(complaint.lat),
            float(complaint.lng),
            intensity
        ])
    
    return {
        "data": heatmap_data,
        "metadata": {
            "count": len(heatmap_data),
            "intensity_field": intensity_field,
            "filters": {
                "status": status,
                "category": category
            }
        }
    }


@router.get("/clusters")
async def get_complaint_clusters(
    radius_km: float = 1.0,
    min_complaints: int = 3,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get complaint clusters (hotspots)
    Identifies areas with high complaint density
    Non-admin users only see clusters from their own constituency
    
    Note: This is a basic implementation. For production, use PostGIS ST_ClusterDBSCAN
    """
    query = db.query(Complaint).filter(
        Complaint.lat.isnot(None),
        Complaint.lng.isnot(None)
    )
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    complaints = query.all()
    
    # Simple clustering algorithm (can be improved with PostGIS)
    # For now, return grid-based clusters
    
    clusters = []
    grid_size = radius_km / 111.0  # Approximate degrees
    
    # Group complaints by grid cell
    from collections import defaultdict
    grid = defaultdict(list)
    
    for complaint in complaints:
        lat_grid = int(float(complaint.lat) / grid_size)
        lng_grid = int(float(complaint.lng) / grid_size)
        grid[(lat_grid, lng_grid)].append(complaint)
    
    # Create cluster objects
    cluster_id = 0
    for (lat_grid, lng_grid), complaint_list in grid.items():
        if len(complaint_list) >= min_complaints:
            # Calculate cluster center
            avg_lat = sum(float(c.lat) for c in complaint_list) / len(complaint_list)
            avg_lng = sum(float(c.lng) for c in complaint_list) / len(complaint_list)
            
            # Count by status
            status_counts = {}
            for c in complaint_list:
                status = c.status.value if hasattr(c.status, 'value') else c.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            clusters.append({
                "cluster_id": cluster_id,
                "center": {
                    "lat": avg_lat,
                    "lng": avg_lng
                },
                "complaint_count": len(complaint_list),
                "complaint_ids": [str(c.id) for c in complaint_list],
                "status_breakdown": status_counts,
                "dominant_status": max(status_counts.items(), key=lambda x: x[1])[0] if status_counts else None
            })
            cluster_id += 1
    
    return {
        "clusters": clusters,
        "metadata": {
            "cluster_count": len(clusters),
            "total_complaints": len(complaints),
            "parameters": {
                "radius_km": radius_km,
                "min_complaints": min_complaints
            }
        }
    }


@router.get("/stats/by-ward")
async def get_ward_statistics(
    constituency_id: Optional[UUID] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get complaint statistics grouped by ward
    Non-admin users only see statistics from their own constituency
    Useful for ward-level heatmap
    """
    from sqlalchemy import func
    
    query = db.query(
        Ward.id.label('ward_id'),
        Ward.name.label('ward_name'),
        Ward.ward_number,
        func.count(Complaint.id).label('total_complaints'),
        func.count(Complaint.id).filter(Complaint.status == ComplaintStatus.SUBMITTED).label('submitted'),
        func.count(Complaint.id).filter(Complaint.status == ComplaintStatus.ASSIGNED).label('assigned'),
        func.count(Complaint.id).filter(Complaint.status == ComplaintStatus.IN_PROGRESS).label('in_progress'),
        func.count(Complaint.id).filter(Complaint.status == ComplaintStatus.RESOLVED).label('resolved'),
        func.count(Complaint.id).filter(Complaint.status == ComplaintStatus.CLOSED).label('closed')
    ).outerjoin(Complaint, Ward.id == Complaint.ward_id).group_by(Ward.id)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.filter(Ward.constituency_id == constituency_filter)
    elif constituency_id:  # Only allow explicit filter if admin
        query = query.filter(Ward.constituency_id == constituency_id)
    
    results = query.all()
    
    ward_stats = []
    for row in results:
        ward_stats.append({
            "ward_id": str(row.ward_id),
            "ward_name": row.ward_name,
            "ward_number": row.ward_number,
            "total_complaints": row.total_complaints,
            "by_status": {
                "submitted": row.submitted,
                "assigned": row.assigned,
                "in_progress": row.in_progress,
                "resolved": row.resolved,
                "closed": row.closed
            }
        })
    
    return {
        "wards": ward_stats,
        "metadata": {
            "ward_count": len(ward_stats),
            "constituency_id": str(constituency_id) if constituency_id else None
        }
    }
