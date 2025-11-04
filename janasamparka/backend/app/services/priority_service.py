"""Priority scoring and SLA management service."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint


# SLA Configuration by Category (in days)
SLA_CONFIG = {
    "water": {
        "emergency": 1,
        "high": 3,
        "medium": 7,
        "low": 14,
        "expected_resolution": "7-14 days",
        "success_rate": 0.78
    },
    "roads": {
        "emergency": 1,
        "high": 7,
        "medium": 30,
        "low": 45,
        "expected_resolution": "30-45 days",
        "success_rate": 0.65
    },
    "electricity": {
        "emergency": 1,
        "high": 2,
        "medium": 3,
        "low": 7,
        "expected_resolution": "3-7 days",
        "success_rate": 0.92
    },
    "sanitation": {
        "emergency": 1,
        "high": 7,
        "medium": 14,
        "low": 21,
        "expected_resolution": "14-21 days",
        "success_rate": 0.71
    },
    "health": {
        "emergency": 1,
        "high": 1,
        "medium": 7,
        "low": 14,
        "expected_resolution": "1-7 days",
        "success_rate": 0.85
    },
    "education": {
        "emergency": 3,
        "high": 7,
        "medium": 14,
        "low": 30,
        "expected_resolution": "14-30 days",
        "success_rate": 0.73
    },
    "police": {
        "emergency": 1,
        "high": 1,
        "medium": 3,
        "low": 7,
        "expected_resolution": "1-3 days",
        "success_rate": 0.88
    },
    "default": {
        "emergency": 1,
        "high": 7,
        "medium": 14,
        "low": 30,
        "expected_resolution": "14-30 days",
        "success_rate": 0.70
    }
}

# Emergency keywords - trigger immediate priority
EMERGENCY_KEYWORDS = [
    "accident", "death", "injury", "fire", "flood", "explosion", "collapse",
    "gas leak", "chemical", "poison", "emergency", "urgent", "immediate",
    "life threatening", "danger", "hazard", "unsafe", "critical", "severe"
]

# High impact keywords
HIGH_IMPACT_KEYWORDS = [
    "main road", "highway", "hospital", "school", "market", "junction",
    "entire area", "whole street", "many people", "everyone", "community",
    "public place", "busy area"
]

# Recurrence indicators
RECURRENCE_KEYWORDS = [
    "again", "repeated", "multiple times", "still not fixed", "previously reported",
    "second time", "third time", "once again", "already complained"
]

# Vulnerability indicators
VULNERABILITY_KEYWORDS = [
    "elderly", "senior citizen", "children", "pregnant", "disabled",
    "handicapped", "blind", "slum", "poor", "ration card", "bpl"
]


class PriorityCalculationService:
    """Service for calculating complaint priority scores."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_priority_score(
        self,
        title: str,
        description: str,
        category: Optional[str],
        location_description: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None
    ) -> dict:
        """
        Calculate priority score for a complaint.
        
        Returns:
            dict with priority_score, is_emergency, affected_population_estimate, priority_level
        """
        combined_text = f"{title} {description} {location_description or ''}".lower()
        
        # 1. Severity Factor (0-1)
        severity_score = self._calculate_severity(combined_text, category)
        
        # 2. Affected Population (0-1)
        population_score, population_estimate = self._estimate_affected_population(
            combined_text, lat, lng
        )
        
        # 3. Legal/Urgency Factor (0-1)
        urgency_score, is_emergency = self._calculate_urgency(combined_text, category)
        
        # 4. Recurrence Factor (0-1)
        recurrence_score = self._check_recurrence(combined_text)
        
        # 5. Vulnerability Factor (0-1)
        vulnerability_score = self._check_vulnerability(combined_text)
        
        # Calculate weighted priority score
        priority_score = (
            severity_score * 0.4 +
            population_score * 0.25 +
            urgency_score * 0.15 +
            recurrence_score * 0.10 +
            vulnerability_score * 0.10
        )
        
        # Determine priority level
        if is_emergency or priority_score >= 0.85:
            priority_level = "urgent"
        elif priority_score >= 0.65:
            priority_level = "high"
        elif priority_score >= 0.35:
            priority_level = "medium"
        else:
            priority_level = "low"
        
        return {
            "priority_score": round(priority_score, 2),
            "is_emergency": is_emergency,
            "affected_population_estimate": population_estimate,
            "priority_level": priority_level,
            "factors": {
                "severity": round(severity_score, 2),
                "population": round(population_score, 2),
                "urgency": round(urgency_score, 2),
                "recurrence": round(recurrence_score, 2),
                "vulnerability": round(vulnerability_score, 2)
            }
        }
    
    def _calculate_severity(self, text: str, category: Optional[str]) -> float:
        """Calculate severity score based on keywords."""
        score = 0.0
        
        # Check for emergency keywords
        emergency_matches = sum(1 for keyword in EMERGENCY_KEYWORDS if keyword in text)
        if emergency_matches > 0:
            score = min(1.0, 0.8 + (emergency_matches * 0.1))
            return score
        
        # Category-based severity
        severe_categories = ["health", "police", "fire", "water"]
        if category and any(cat in category.lower() for cat in severe_categories):
            score += 0.3
        
        # Check for severity indicators
        severity_words = ["major", "serious", "severe", "critical", "big", "large", "huge"]
        severity_matches = sum(1 for word in severity_words if word in text)
        score += min(0.4, severity_matches * 0.1)
        
        return min(1.0, score)
    
    def _estimate_affected_population(
        self, text: str, lat: Optional[float], lng: Optional[float]
    ) -> tuple[float, int]:
        """Estimate affected population and return score."""
        # Default estimate
        estimate = 1
        
        # Check for high impact keywords
        high_impact_matches = sum(1 for keyword in HIGH_IMPACT_KEYWORDS if keyword in text)
        if high_impact_matches > 0:
            estimate = 100 + (high_impact_matches * 50)
        
        # Look for number mentions
        if "hundred" in text or "100" in text:
            estimate = max(estimate, 100)
        if "thousand" in text or "1000" in text:
            estimate = max(estimate, 1000)
        
        # Location-based estimation (if we have coordinates)
        if lat and lng:
            # In a real system, we'd query population density data
            # For now, assume urban areas have higher population
            estimate = max(estimate, 50)
        
        # Convert estimate to score (0-1)
        # 1 person = 0, 1000+ people = 1
        score = min(1.0, estimate / 1000.0)
        
        return score, estimate
    
    def _calculate_urgency(self, text: str, category: Optional[str]) -> tuple[float, bool]:
        """Calculate urgency score and check if emergency."""
        is_emergency = False
        score = 0.0
        
        # Check for emergency keywords
        emergency_matches = sum(1 for keyword in EMERGENCY_KEYWORDS if keyword in text)
        if emergency_matches > 0:
            is_emergency = True
            score = 1.0
            return score, is_emergency
        
        # Urgent categories
        if category:
            urgent_categories = ["health", "police", "fire", "gas", "electricity"]
            if any(cat in category.lower() for cat in urgent_categories):
                score += 0.5
        
        # Time-sensitive words
        urgent_words = ["urgent", "immediate", "asap", "quickly", "soon", "now"]
        urgent_matches = sum(1 for word in urgent_words if word in text)
        score += min(0.5, urgent_matches * 0.15)
        
        return min(1.0, score), is_emergency
    
    def _check_recurrence(self, text: str) -> float:
        """Check if this is a recurring issue."""
        recurrence_matches = sum(1 for keyword in RECURRENCE_KEYWORDS if keyword in text)
        return min(1.0, recurrence_matches * 0.3)
    
    def _check_vulnerability(self, text: str) -> float:
        """Check if vulnerable populations are affected."""
        vulnerability_matches = sum(1 for keyword in VULNERABILITY_KEYWORDS if keyword in text)
        return min(1.0, vulnerability_matches * 0.4)
    
    def get_sla_for_category(self, category: Optional[str], priority_level: str) -> dict:
        """Get SLA configuration for a category and priority level."""
        category_key = category.lower() if category else "default"
        
        # Get category config or fallback to default
        config = SLA_CONFIG.get(category_key, SLA_CONFIG["default"])
        
        # Get SLA days for the priority level
        sla_days = config.get(priority_level, config["medium"])
        
        return {
            "sla_days": sla_days,
            "expected_resolution": config["expected_resolution"],
            "success_rate": config["success_rate"],
            "due_date": datetime.utcnow() + timedelta(days=sla_days)
        }
    
    async def detect_nearby_duplicates(
        self,
        complaint_id: UUID,
        lat: float,
        lng: float,
        category: str,
        radius_meters: int = 200
    ) -> list[Complaint]:
        """
        Detect potential duplicate complaints within a radius.
        
        Uses geographic distance and category matching.
        """
        # Calculate approximate degree offset for radius
        # 1 degree latitude ≈ 111 km
        lat_offset = radius_meters / 111000.0
        lng_offset = radius_meters / (111000.0 * abs(float(lng)))
        
        # Query for nearby complaints in same category
        result = await self.db.execute(
            select(Complaint).where(
                and_(
                    Complaint.id != complaint_id,
                    Complaint.category == category,
                    Complaint.lat.between(lat - lat_offset, lat + lat_offset),
                    Complaint.lng.between(lng - lng_offset, lng + lng_offset),
                    Complaint.status.in_(["submitted", "assigned", "in_progress"]),
                    Complaint.is_duplicate == False
                )
            ).limit(20)
        )
        
        return result.scalars().all()
    
    async def calculate_queue_position(
        self,
        complaint_id: UUID,
        constituency_id: UUID,
        department_id: Optional[UUID] = None
    ) -> dict:
        """Calculate complaint's position in the queue."""
        # Get the complaint
        result = await self.db.execute(
            select(Complaint).where(Complaint.id == complaint_id)
        )
        complaint = result.scalar_one_or_none()
        
        if not complaint:
            return {"position": 0, "total": 0}
        
        # Build query for complaints ahead in queue
        query = select(func.count()).where(
            and_(
                Complaint.constituency_id == constituency_id,
                Complaint.status.in_(["submitted", "assigned"]),
                Complaint.priority_score > complaint.priority_score
            )
        )
        
        if department_id:
            query = query.where(Complaint.dept_id == department_id)
        
        result = await self.db.execute(query)
        position = result.scalar() + 1  # +1 because this complaint counts
        
        # Get total in queue
        total_query = select(func.count()).where(
            and_(
                Complaint.constituency_id == constituency_id,
                Complaint.status.in_(["submitted", "assigned"])
            )
        )
        
        if department_id:
            total_query = total_query.where(Complaint.dept_id == department_id)
        
        result = await self.db.execute(total_query)
        total = result.scalar()
        
        return {
            "position": position,
            "total": total,
            "percentile": round((1 - (position / max(total, 1))) * 100, 1)
        }
