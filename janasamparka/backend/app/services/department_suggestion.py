"""Department suggestion service for smart routing of complaints."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.schemas.case_management import DepartmentSuggestion


# Department keywords and categories mapping
DEPARTMENT_KEYWORDS = {
    "roads": {
        "keywords": [
            "road", "pothole", "street", "highway", "bridge", "footpath", "sidewalk",
            "pavement", "traffic", "signal", "crossing", "junction", "intersection",
            "asphalt", "tar", "cement", "crack", "damage"
        ],
        "codes": ["PWD", "BBMP_ROADS", "NHAI"],
        "confidence_boost": 0.3
    },
    "water": {
        "keywords": [
            "water", "supply", "tap", "pipeline", "leak", "shortage", "drainage",
            "sewage", "manhole", "underground", "valve", "tank", "reservoir",
            "contamination", "dirty", "smell", "overflow"
        ],
        "codes": ["BWSSB", "WATER_SUPPLY"],
        "confidence_boost": 0.3
    },
    "electricity": {
        "keywords": [
            "electricity", "power", "light", "streetlight", "lamp", "pole", "wire",
            "cable", "transformer", "meter", "billing", "outage", "blackout",
            "voltage", "connection", "supply", "electric"
        ],
        "codes": ["BESCOM", "ELECTRICITY"],
        "confidence_boost": 0.3
    },
    "health": {
        "keywords": [
            "health", "hospital", "clinic", "doctor", "nurse", "medicine", "medical",
            "patient", "ambulance", "emergency", "treatment", "disease", "illness",
            "vaccination", "immunization", "surgery", "diagnosis"
        ],
        "codes": ["HEALTH", "BBMP_HEALTH"],
        "confidence_boost": 0.3
    },
    "education": {
        "keywords": [
            "school", "education", "student", "teacher", "college", "university",
            "classroom", "study", "exam", "admission", "fee", "scholarship",
            "library", "book", "learning", "training"
        ],
        "codes": ["EDUCATION", "DEPT_EDUCATION"],
        "confidence_boost": 0.3
    },
    "sanitation": {
        "keywords": [
            "garbage", "waste", "trash", "sweeping", "cleaning", "toilet", "sanitation",
            "dustbin", "collection", "disposal", "dump", "smell", "dirty", "hygiene",
            "cleanliness", "sweeper"
        ],
        "codes": ["BBMP_SANITATION", "SANITATION"],
        "confidence_boost": 0.3
    },
    "police": {
        "keywords": [
            "police", "crime", "theft", "robbery", "safety", "security", "violence",
            "assault", "harassment", "fir", "complaint", "station", "law", "order"
        ],
        "codes": ["POLICE", "LAW_ORDER"],
        "confidence_boost": 0.3
    },
    "environment": {
        "keywords": [
            "tree", "forest", "park", "garden", "pollution", "air", "noise",
            "environment", "green", "plant", "deforestation", "conservation"
        ],
        "codes": ["FOREST", "ENVIRONMENT", "PARKS"],
        "confidence_boost": 0.2
    }
}


class DepartmentSuggestionService:
    """Service for suggesting appropriate departments based on complaint content."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def suggest_departments(
        self,
        title: str,
        description: str,
        constituency_id: UUID,
        category: Optional[str] = None,
        location_description: Optional[str] = None
    ) -> list[DepartmentSuggestion]:
        """
        Suggest departments based on complaint content using keyword matching.
        
        Args:
            title: Complaint title
            description: Complaint description
            constituency_id: Constituency ID
            category: Optional category
            location_description: Optional location details
        
        Returns:
            List of department suggestions sorted by confidence
        """
        # Combine all text for analysis
        combined_text = f"{title} {description}"
        if category:
            combined_text += f" {category}"
        if location_description:
            combined_text += f" {location_description}"
        
        combined_text = combined_text.lower()
        
        # Get all departments in the constituency
        result = await self.db.execute(
            select(Department).where(Department.constituency_id == constituency_id)
        )
        departments = result.scalars().all()
        
        # Calculate confidence scores for each department
        suggestions = []
        
        for dept in departments:
            confidence = 0.0
            matched_categories = []
            
            # Check each category's keywords
            for category_name, category_data in DEPARTMENT_KEYWORDS.items():
                # Check if department code matches this category
                if any(code.lower() in dept.code.lower() for code in category_data["codes"]):
                    # Count keyword matches
                    keyword_matches = sum(
                        1 for keyword in category_data["keywords"]
                        if keyword in combined_text
                    )
                    
                    if keyword_matches > 0:
                        # Calculate confidence based on matches
                        match_ratio = keyword_matches / len(category_data["keywords"])
                        category_confidence = match_ratio + category_data["confidence_boost"]
                        confidence = max(confidence, min(category_confidence, 1.0))
                        matched_categories.append(category_name)
            
            # Add department if it has any confidence
            if confidence > 0.1:
                reason = f"Matched keywords related to: {', '.join(matched_categories)}"
                suggestions.append(
                    DepartmentSuggestion(
                        dept_id=dept.id,
                        dept_name=dept.name,
                        dept_code=dept.code,
                        confidence=round(confidence, 2),
                        reason=reason
                    )
                )
        
        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        # Return top 3 suggestions
        return suggestions[:3]
    
    async def get_department_by_code_prefix(
        self,
        code_prefix: str,
        constituency_id: UUID
    ) -> Optional[Department]:
        """Get department by code prefix in a constituency."""
        result = await self.db.execute(
            select(Department).where(
                Department.constituency_id == constituency_id,
                Department.code.ilike(f"{code_prefix}%")
            )
        )
        return result.scalar_one_or_none()
