"""Geographic clustering service for batch complaint resolution."""

from typing import Optional
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint


@dataclass
class ComplaintCluster:
    """Represents a cluster of nearby complaints."""
    
    cluster_id: str
    category: str
    complaint_ids: list[UUID]
    center_lat: float
    center_lng: float
    radius_meters: float
    estimated_cost_individual: float
    estimated_cost_batch: float
    savings_percentage: float
    complaint_count: int
    location_description: str


class ClusteringService:
    """Service for identifying complaint clusters for batch resolution."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_complaint_clusters(
        self,
        constituency_id: UUID,
        category: Optional[str] = None,
        min_cluster_size: int = 3,
        max_radius_meters: int = 500
    ) -> list[ComplaintCluster]:
        """
        Find clusters of nearby complaints that can be resolved together.
        
        Args:
            constituency_id: Constituency to analyze
            category: Optional category filter
            min_cluster_size: Minimum complaints in a cluster
            max_radius_meters: Maximum radius for clustering
            
        Returns:
            List of ComplaintCluster objects
        """
        # Get unresolved complaints with location
        query = select(Complaint).where(
            and_(
                Complaint.constituency_id == constituency_id,
                Complaint.status.in_(["submitted", "assigned"]),
                Complaint.lat.isnot(None),
                Complaint.lng.isnot(None),
                Complaint.is_duplicate == False
            )
        )
        
        if category:
            query = query.where(Complaint.category == category)
        
        result = await self.db.execute(query)
        complaints = result.scalars().all()
        
        if len(complaints) < min_cluster_size:
            return []
        
        # Simple clustering algorithm (can be replaced with DBSCAN for better results)
        clusters = []
        processed = set()
        
        for i, complaint in enumerate(complaints):
            if complaint.id in processed:
                continue
            
            # Find nearby complaints
            cluster_complaints = [complaint]
            processed.add(complaint.id)
            
            for j, other in enumerate(complaints):
                if i != j and other.id not in processed:
                    distance = self._calculate_distance(
                        float(complaint.lat), float(complaint.lng),
                        float(other.lat), float(other.lng)
                    )
                    
                    if distance <= max_radius_meters and complaint.category == other.category:
                        cluster_complaints.append(other)
                        processed.add(other.id)
            
            # Only create cluster if meets minimum size
            if len(cluster_complaints) >= min_cluster_size:
                cluster = self._create_cluster(cluster_complaints, max_radius_meters)
                clusters.append(cluster)
        
        return clusters
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points in meters using Haversine formula.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lng = radians(lng2 - lng1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _create_cluster(
        self,
        complaints: list[Complaint],
        max_radius: float
    ) -> ComplaintCluster:
        """Create a cluster object from a list of complaints."""
        # Calculate center point (centroid)
        center_lat = sum(float(c.lat) for c in complaints) / len(complaints)
        center_lng = sum(float(c.lng) for c in complaints) / len(complaints)
        
        # Calculate actual radius (max distance from center)
        max_dist = 0
        for complaint in complaints:
            dist = self._calculate_distance(
                center_lat, center_lng,
                float(complaint.lat), float(complaint.lng)
            )
            max_dist = max(max_dist, dist)
        
        # Estimate costs (these would come from a real cost database)
        cost_per_complaint = self._estimate_individual_cost(complaints[0].category)
        individual_cost = cost_per_complaint * len(complaints)
        
        # Batch resolution typically saves 30-40% due to economies of scale
        batch_cost = individual_cost * 0.65  # 35% savings
        savings = ((individual_cost - batch_cost) / individual_cost) * 100
        
        # Generate location description
        location_desc = self._generate_location_description(complaints)
        
        return ComplaintCluster(
            cluster_id=f"{complaints[0].category}_{int(center_lat*1000)}_{int(center_lng*1000)}",
            category=complaints[0].category or "general",
            complaint_ids=[c.id for c in complaints],
            center_lat=center_lat,
            center_lng=center_lng,
            radius_meters=round(max_dist, 1),
            estimated_cost_individual=individual_cost,
            estimated_cost_batch=batch_cost,
            savings_percentage=round(savings, 1),
            complaint_count=len(complaints),
            location_description=location_desc
        )
    
    def _estimate_individual_cost(self, category: Optional[str]) -> float:
        """Estimate cost per complaint based on category (in rupees)."""
        cost_estimates = {
            "roads": 50000,      # ₹50,000 per pothole
            "water": 25000,      # ₹25,000 per water issue
            "electricity": 15000, # ₹15,000 per electrical issue
            "sanitation": 20000,  # ₹20,000 per sanitation issue
            "streetlight": 8000,  # ₹8,000 per streetlight
            "drainage": 40000,    # ₹40,000 per drainage issue
            "default": 30000      # ₹30,000 default
        }
        
        category_key = category.lower() if category else "default"
        return cost_estimates.get(category_key, cost_estimates["default"])
    
    def _generate_location_description(self, complaints: list[Complaint]) -> str:
        """Generate a human-readable location description for the cluster."""
        # Try to extract common location elements
        location_words = []
        for complaint in complaints:
            if complaint.location_description:
                location_words.extend(complaint.location_description.lower().split())
        
        # Find most common location terms
        if location_words:
            from collections import Counter
            common_words = Counter(location_words).most_common(3)
            location = " ".join([word for word, _ in common_words if len(word) > 3])
            return f"Near {location}" if location else "Multiple locations"
        
        return "Multiple locations in the area"
    
    async def suggest_batch_project(
        self,
        cluster: ComplaintCluster
    ) -> dict:
        """Generate a batch project suggestion from a cluster."""
        # Get complaint details
        result = await self.db.execute(
            select(Complaint).where(Complaint.id.in_(cluster.complaint_ids))
        )
        complaints = result.scalars().all()
        
        # Generate project description
        category_names = {
            "roads": "Road Repair Project",
            "water": "Water Supply Maintenance",
            "electricity": "Electrical Infrastructure Upgrade",
            "sanitation": "Sanitation Improvement",
            "streetlight": "Street Lighting Installation",
            "drainage": "Drainage System Repair",
            "default": "Infrastructure Project"
        }
        
        project_name = category_names.get(cluster.category, category_names["default"])
        
        # Calculate expected timeline (batch projects take longer but resolve more)
        days_per_complaint = 2  # Assume 2 days per complaint in batch
        estimated_days = max(7, len(complaints) * days_per_complaint)
        
        return {
            "project_id": cluster.cluster_id,
            "project_name": f"{project_name}: {cluster.location_description}",
            "category": cluster.category,
            "location": {
                "center_lat": cluster.center_lat,
                "center_lng": cluster.center_lng,
                "radius_meters": cluster.radius_meters,
                "description": cluster.location_description
            },
            "complaints": {
                "count": cluster.complaint_count,
                "ids": cluster.complaint_ids
            },
            "cost": {
                "individual_total": cluster.estimated_cost_individual,
                "batch_total": cluster.estimated_cost_batch,
                "savings": cluster.estimated_cost_individual - cluster.estimated_cost_batch,
                "savings_percentage": cluster.savings_percentage,
                "currency": "INR"
            },
            "timeline": {
                "estimated_days": estimated_days,
                "estimated_completion": f"{estimated_days} days from start"
            },
            "benefits": [
                f"Resolves {cluster.complaint_count} complaints at once",
                f"Saves ₹{int(cluster.estimated_cost_individual - cluster.estimated_cost_batch):,}",
                f"{cluster.savings_percentage}% cost reduction",
                "Single project coordination",
                "Comprehensive area coverage"
            ]
        }
