"""Predictive planning service with multilingual support for Kannada and English."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
import re

from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint


class MultilingualNormalizer:
    """Normalize Kannada and English text with spelling correction."""
    
    # Common Kannada words (transliterated) and their English equivalents
    KANNADA_ENGLISH_MAP = {
        # Infrastructure
        "raste": "road",
        "bandi": "road",
        "niru": "water",
        "jala": "water",
        "bavi": "well",
        "borewell": "borewell",
        "current": "electricity",
        "light": "light",
        "streetlight": "streetlight",
        "gutter": "drainage",
        "drainage": "drainage",
        "kachada": "garbage",
        "sewage": "sewage",
        
        # Issues
        "guddi": "hole",
        "hole": "hole",
        "broken": "broken",
        "damage": "damaged",
        "problem": "problem",
        "kodilla": "not working",
        "illa": "no",
        "yake": "why",
        
        # Severity
        "emergency": "emergency",
        "urgent": "urgent",
        "bega": "urgent",
        "immediately": "immediately",
        "sikkantu": "urgent",
        
        # Locations
        "mane": "house",
        "school": "school",
        "hospital": "hospital",
        "circle": "circle",
        "cross": "intersection",
        "main road": "main road",
        
        # Common misspellings
        "watter": "water",
        "watr": "water",
        "rodd": "road",
        "rode": "road",
        "elctricity": "electricity",
        "electrisity": "electricity",
        "lihgt": "light",
        "litte": "light",
        "garbge": "garbage",
        "garbaze": "garbage",
        "drainge": "drainage",
        "drenage": "drainage",
        "brokan": "broken",
        "brokn": "broken",
        "urgant": "urgent",
        "emergancy": "emergency",
        "imidiately": "immediately",
        "problm": "problem",
        "issu": "issue",
    }
    
    # Category keywords in both languages
    CATEGORY_KEYWORDS = {
        "roads": [
            "road", "raste", "bandi", "pothole", "guddi", "hole", "crack", "broken road",
            "tar", "asphalt", "highway", "street", "path", "walked", "vehicle"
        ],
        "water": [
            "water", "niru", "jala", "bavi", "well", "borewell", "pipeline", "pipe burst",
            "tap", "supply", "drinking water", "no water", "water shortage", "leakage"
        ],
        "electricity": [
            "electricity", "current", "power", "light", "bulb", "streetlight", "pole",
            "wire", "transformer", "no power", "power cut", "voltage", "shock"
        ],
        "drainage": [
            "drainage", "gutter", "sewage", "clog", "block", "overflow", "smell",
            "stagnant", "manhole", "dirty water", "flooding", "rain water"
        ],
        "sanitation": [
            "garbage", "kachada", "waste", "trash", "dustbin", "collection", "cleaning",
            "sweeping", "dirty", "unhygienic", "mosquito", "smell bad"
        ],
        "streetlight": [
            "streetlight", "street light", "lamp", "pole light", "night", "dark",
            "not working", "fused", "broken light"
        ]
    }
    
    def normalize_text(self, text: str) -> str:
        """Normalize Kannada/English mixed text with spelling correction."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace Kannada transliterations and fix spellings
        words = text.split()
        normalized_words = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            # Check if it's a known Kannada word or common misspelling
            if clean_word in self.KANNADA_ENGLISH_MAP:
                normalized_words.append(self.KANNADA_ENGLISH_MAP[clean_word])
            else:
                # Try fuzzy matching for severe misspellings
                normalized_words.append(self._fuzzy_correct(clean_word))
        
        return " ".join(normalized_words)
    
    def _fuzzy_correct(self, word: str) -> str:
        """Simple fuzzy matching for severe misspellings."""
        if len(word) < 3:
            return word
        
        # Check for phonetic similarities
        for known_word, correct in self.KANNADA_ENGLISH_MAP.items():
            if self._levenshtein_distance(word, known_word) <= 2:
                return correct
        
        return word
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate edit distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def detect_category(self, text: str) -> Optional[str]:
        """Detect complaint category from multilingual text."""
        normalized = self.normalize_text(text)
        
        scores = defaultdict(int)
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in normalized:
                    scores[category] += 1
        
        if not scores:
            return None
        
        # Return category with highest score
        return max(scores.items(), key=lambda x: x[1])[0]


class PredictivePlanningService:
    """Predictive planning and forecasting service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.normalizer = MultilingualNormalizer()
    
    async def predict_seasonal_trends(
        self,
        constituency_id: UUID,
        months_ahead: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Predict complaint trends based on seasonal patterns.
        
        Example: Monsoon season = drainage issues spike
        """
        current_month = datetime.now().month
        
        # Get historical data for same months in previous years
        predictions = []
        
        for month_offset in range(1, months_ahead + 1):
            target_month = (current_month + month_offset - 1) % 12 + 1
            
            # Query historical complaints for this month
            query = select(
                Complaint.category,
                func.count(Complaint.id).label('count')
            ).where(
                and_(
                    Complaint.constituency_id == constituency_id,
                    extract('month', Complaint.created_at) == target_month,
                    Complaint.created_at >= datetime.now() - timedelta(days=365 * 3)  # Last 3 years
                )
            ).group_by(Complaint.category)
            
            result = await self.db.execute(query)
            category_counts = dict(result.all())
            
            # Seasonal adjustments
            seasonal_factors = self._get_seasonal_factors(target_month)
            
            adjusted_predictions = {}
            for category, base_count in category_counts.items():
                factor = seasonal_factors.get(category, 1.0)
                adjusted_predictions[category] = int(base_count * factor / 3)  # Average over 3 years
            
            predictions.append({
                "month": target_month,
                "month_name": datetime(2024, target_month, 1).strftime("%B"),
                "predicted_complaints": adjusted_predictions,
                "total_predicted": sum(adjusted_predictions.values()),
                "recommendations": self._get_seasonal_recommendations(target_month)
            })
        
        return predictions
    
    def _get_seasonal_factors(self, month: int) -> Dict[str, float]:
        """Get seasonal adjustment factors for each category."""
        # Monsoon months (June-September) in India
        if month in [6, 7, 8, 9]:
            return {
                "drainage": 2.5,      # 150% increase
                "roads": 1.8,         # 80% increase (potholes after rain)
                "sanitation": 1.5,    # 50% increase (garbage disposal issues)
                "water": 0.8,         # 20% decrease (sufficient water)
                "electricity": 1.2,   # 20% increase (lightning damage)
                "streetlight": 1.1    # 10% increase
            }
        
        # Summer months (March-May)
        elif month in [3, 4, 5]:
            return {
                "water": 2.0,         # 100% increase (water shortage)
                "electricity": 1.5,   # 50% increase (high AC usage)
                "drainage": 0.7,      # 30% decrease
                "roads": 1.0,
                "sanitation": 1.2,    # 20% increase (decomposition faster)
                "streetlight": 1.0
            }
        
        # Winter/Festival season (October-February)
        elif month in [10, 11, 12, 1, 2]:
            return {
                "streetlight": 1.4,   # 40% increase (darker earlier)
                "roads": 1.3,         # 30% increase (more travel during festivals)
                "sanitation": 1.3,    # 30% increase (festival waste)
                "water": 1.0,
                "electricity": 1.2,   # 20% increase (festivals)
                "drainage": 0.9       # 10% decrease
            }
        
        return {}
    
    def _get_seasonal_recommendations(self, month: int) -> List[str]:
        """Get proactive maintenance recommendations for the season."""
        # Pre-monsoon (May-June)
        if month in [5, 6]:
            return [
                "Clean all drainage systems before monsoon",
                "Inspect and repair roads to prevent monsoon damage",
                "Check water storage facilities",
                "Trim trees near power lines",
                "Install additional drainage capacity in flood-prone areas"
            ]
        
        # During monsoon (July-September)
        elif month in [7, 8, 9]:
            return [
                "Deploy emergency drainage cleaning teams",
                "Keep road repair materials ready for quick fixes",
                "Monitor water quality in affected areas",
                "Have backup power generators for critical areas",
                "Increase sanitation collection frequency"
            ]
        
        # Pre-summer (February-March)
        elif month in [2, 3]:
            return [
                "Service all borewells and water pumps",
                "Check water pipeline integrity",
                "Prepare for increased electricity demand",
                "Plan water tanker routes for shortage areas",
                "Clean water storage tanks"
            ]
        
        # Summer (April-May)
        elif month in [4, 5]:
            return [
                "Deploy water tankers to shortage areas",
                "Monitor transformer capacity",
                "Increase frequency of sanitation in hot areas",
                "Check and refill streetlight reservoirs if solar",
                "Have emergency water response teams ready"
            ]
        
        return ["Regular maintenance and inspection"]
    
    async def forecast_budget_needs(
        self,
        constituency_id: UUID,
        months_ahead: int = 6
    ) -> Dict[str, Any]:
        """
        Forecast budget requirements based on predicted complaints and resolution costs.
        """
        # Get seasonal predictions
        predictions = await self.predict_seasonal_trends(constituency_id, months_ahead)
        
        # Cost per complaint by category (in rupees)
        avg_costs = {
            "roads": 50000,
            "water": 25000,
            "electricity": 15000,
            "sanitation": 20000,
            "streetlight": 8000,
            "drainage": 40000
        }
        
        total_budget_needed = 0
        category_budgets = defaultdict(int)
        monthly_breakdown = []
        
        for prediction in predictions:
            month_total = 0
            month_categories = {}
            
            for category, count in prediction["predicted_complaints"].items():
                cost = count * avg_costs.get(category, 30000)
                category_budgets[category] += cost
                month_total += cost
                month_categories[category] = cost
            
            monthly_breakdown.append({
                "month": prediction["month_name"],
                "total_budget": month_total,
                "by_category": month_categories
            })
            
            total_budget_needed += month_total
        
        return {
            "period": f"Next {months_ahead} months",
            "total_budget_needed": total_budget_needed,
            "monthly_average": total_budget_needed // months_ahead,
            "by_category": dict(category_budgets),
            "monthly_breakdown": monthly_breakdown,
            "critical_months": self._identify_critical_months(monthly_breakdown)
        }
    
    def _identify_critical_months(self, monthly_breakdown: List[Dict]) -> List[str]:
        """Identify months requiring highest budget allocation."""
        avg_budget = sum(m["total_budget"] for m in monthly_breakdown) / len(monthly_breakdown)
        
        critical = [
            m["month"] for m in monthly_breakdown 
            if m["total_budget"] > avg_budget * 1.5
        ]
        
        return critical
    
    async def suggest_proactive_maintenance(
        self,
        constituency_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Suggest proactive maintenance based on complaint history and patterns.
        """
        # Find areas with recurring complaints
        query = select(
            Complaint.category,
            Complaint.location_description,
            func.count(Complaint.id).label('complaint_count'),
            func.avg(Complaint.lat).label('avg_lat'),
            func.avg(Complaint.lng).label('avg_lng')
        ).where(
            and_(
                Complaint.constituency_id == constituency_id,
                Complaint.created_at >= datetime.now() - timedelta(days=180),  # Last 6 months
                Complaint.status == "resolved"
            )
        ).group_by(
            Complaint.category,
            Complaint.location_description
        ).having(
            func.count(Complaint.id) >= 3  # At least 3 complaints
        ).order_by(
            func.count(Complaint.id).desc()
        )
        
        result = await self.db.execute(query)
        recurring_issues = result.all()
        
        suggestions = []
        for issue in recurring_issues[:20]:  # Top 20 recurring issues
            suggestion = {
                "priority": "HIGH" if issue.complaint_count >= 5 else "MEDIUM",
                "category": issue.category,
                "location": issue.location_description or "Unknown location",
                "coordinates": {
                    "lat": float(issue.avg_lat) if issue.avg_lat else None,
                    "lng": float(issue.avg_lng) if issue.avg_lng else None
                },
                "complaint_count": issue.complaint_count,
                "recommendation": self._get_maintenance_recommendation(
                    issue.category,
                    issue.complaint_count
                ),
                "estimated_cost": self._estimate_preventive_cost(
                    issue.category,
                    issue.complaint_count
                ),
                "expected_benefit": f"Prevents {issue.complaint_count * 2} future complaints"
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def _get_maintenance_recommendation(self, category: str, count: int) -> str:
        """Generate specific maintenance recommendation."""
        recommendations = {
            "roads": f"Schedule comprehensive road resurfacing. {count} repairs done already - permanent fix needed.",
            "water": f"Replace aging pipeline section. {count} leaks indicate systemic issue.",
            "electricity": f"Upgrade electrical infrastructure. {count} complaints suggest capacity issue.",
            "drainage": f"Redesign drainage system. {count} blockages indicate design flaw.",
            "sanitation": f"Increase collection frequency or add bins. {count} complaints show insufficient coverage.",
            "streetlight": f"Replace entire streetlight system. {count} failures indicate end of life."
        }
        
        return recommendations.get(category, f"Proactive inspection needed. {count} complaints in same area.")
    
    def _estimate_preventive_cost(self, category: str, complaint_count: int) -> int:
        """Estimate cost of preventive maintenance vs. reactive fixes."""
        reactive_cost_per_complaint = {
            "roads": 50000,
            "water": 25000,
            "electricity": 15000,
            "drainage": 40000,
            "sanitation": 20000,
            "streetlight": 8000
        }
        
        # Preventive maintenance typically costs 2-3x one complaint but prevents 5-10 future issues
        reactive_total = complaint_count * reactive_cost_per_complaint.get(category, 30000)
        preventive_cost = reactive_total * 0.4  # 40% of total reactive cost
        
        return int(preventive_cost)
    
    async def analyze_complaint_with_nlp(
        self,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Analyze complaint text in Kannada/English and extract insights.
        """
        # Normalize text
        normalized_title = self.normalizer.normalize_text(title)
        normalized_description = self.normalizer.normalize_text(description)
        
        # Detect category
        detected_category = self.normalizer.detect_category(
            f"{normalized_title} {normalized_description}"
        )
        
        # Extract urgency indicators
        urgency_keywords = ["emergency", "urgent", "immediately", "dangerous", "critical"]
        is_urgent = any(keyword in normalized_description for keyword in urgency_keywords)
        
        # Extract location hints
        location_keywords = ["near", "opposite", "behind", "front", "next to", "circle", "cross"]
        has_location = any(keyword in normalized_description for keyword in location_keywords)
        
        return {
            "original_title": title,
            "original_description": description,
            "normalized_title": normalized_title,
            "normalized_description": normalized_description,
            "detected_category": detected_category,
            "is_urgent": is_urgent,
            "has_location_context": has_location,
            "language_quality": "multilingual" if self._has_kannada(title + description) else "english",
            "suggested_improvements": self._suggest_text_improvements(
                normalized_title,
                normalized_description,
                has_location
            )
        }
    
    def _has_kannada(self, text: str) -> bool:
        """Detect if text has Kannada transliteration."""
        kannada_indicators = ["raste", "bandi", "niru", "jala", "mane", "guddi", "kachada"]
        return any(word in text.lower() for word in kannada_indicators)
    
    def _suggest_text_improvements(
        self,
        title: str,
        description: str,
        has_location: bool
    ) -> List[str]:
        """Suggest improvements to complaint description."""
        suggestions = []
        
        if not has_location:
            suggestions.append("Add location details: 'near [landmark]' or 'opposite [place]'")
        
        if len(description.split()) < 5:
            suggestions.append("Provide more details about the problem")
        
        if "broken" in description and "since" not in description:
            suggestions.append("Mention when the problem started: 'since yesterday' or 'last week'")
        
        return suggestions
