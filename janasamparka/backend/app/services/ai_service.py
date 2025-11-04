"""
AI/ML services for Janasamparka
"""
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pickle

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import faiss

from app.core.logging import logger
from app.core.config import settings


class ComplaintClassifier:
    """AI-powered complaint classification and categorization"""
    
    def __init__(self):
        self.model = None
        self.categories = [
            "road", "water", "electricity", "street_light", "garbage", 
            "drainage", "tree", "noise", "parking", "public_transport",
            "healthcare", "education", "corruption", "land", "building"
        ]
        self.category_embeddings = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models"""
        try:
            # Load sentence transformer model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Pre-compute category embeddings
            category_descriptions = {
                "road": "Road damage potholes street repair traffic accident",
                "water": "Water supply pipeline leakage drainage sewage",
                "electricity": "Power outage electricity transformer wiring",
                "street_light": "Street light pole illumination dark night",
                "garbage": "Waste disposal trash collection sanitation cleaning",
                "drainage": "Drain blockage rainwater flooding sewer",
                "tree": "Tree cutting branches falling plantation greenery",
                "noise": "Noise pollution loud speakers construction traffic",
                "parking": "Parking violation vehicle tow illegal parking",
                "public_transport": "Bus transport schedule route fare ticket",
                "healthcare": "Hospital medical facility doctor medicine",
                "education": "School college teacher infrastructure quality",
                "corruption": "Bribe corruption illegal demand harassment",
                "land": "Land record property dispute encroachment",
                "building": "Building construction illegal demolition permit"
            }
            
            category_texts = [category_descriptions[cat] for cat in self.categories]
            self.category_embeddings = self.model.encode(category_texts)
            
            logger.info("AI models loaded successfully")
            
        except Exception as e:
            logger.error("Failed to load AI models", error=str(e))
            self.model = None
    
    def classify_complaint(self, title: str, description: str) -> Dict[str, Any]:
        """Classify complaint into categories"""
        if not self.model:
            return {"category": "general", "confidence": 0.0}
        
        try:
            # Combine title and description
            text = f"{title} {description}"
            
            # Generate embedding
            text_embedding = self.model.encode([text])
            
            # Calculate similarities
            similarities = cosine_similarity(text_embedding, self.category_embeddings)[0]
            
            # Get top prediction
            top_idx = np.argmax(similarities)
            confidence = float(similarities[top_idx])
            predicted_category = self.categories[top_idx]
            
            # Get top 3 predictions
            top_3_idx = np.argsort(similarities)[-3:][::-1]
            top_predictions = [
                {
                    "category": self.categories[idx],
                    "confidence": float(similarities[idx])
                }
                for idx in top_3_idx
            ]
            
            return {
                "category": predicted_category,
                "confidence": confidence,
                "top_predictions": top_predictions
            }
            
        except Exception as e:
            logger.error("Failed to classify complaint", error=str(e))
            return {"category": "general", "confidence": 0.0}
    
    def extract_priority(self, title: str, description: str) -> str:
        """Extract priority level from complaint text"""
        text = f"{title} {description}".lower()
        
        # Emergency keywords
        emergency_keywords = [
            "emergency", "urgent", "critical", "danger", "life threatening",
            "accident", "fire", "flood", "collapse", "immediate"
        ]
        
        # High priority keywords
        high_keywords = [
            "blocked", "no water", "power outage", "dark", "dangerous",
            "broken", "damaged", "leaking", "overflowing"
        ]
        
        # Check for emergency
        if any(keyword in text for keyword in emergency_keywords):
            return "urgent"
        
        # Check for high priority
        if any(keyword in text for keyword in high_keywords):
            return "high"
        
        # Default to medium
        return "medium"


class DuplicateDetector:
    """AI-powered duplicate complaint detection"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.complaint_data = []
        self.embedding_dim = 384  # For all-MiniLM-L6-v2
        self.similarity_threshold = 0.8
        self._load_models()
    
    def _load_models(self):
        """Load models and initialize index"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            logger.info("Duplicate detection models loaded")
        except Exception as e:
            logger.error("Failed to load duplicate detection models", error=str(e))
    
    def add_complaint(self, complaint_id: str, title: str, description: str, 
                     category: str, location: str = ""):
        """Add complaint to the index"""
        if not self.model:
            return
        
        try:
            # Create searchable text
            text = f"{title} {description} {category} {location}"
            
            # Generate embedding
            embedding = self.model.encode([text])[0]
            
            # Normalize embedding for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            
            # Add to index
            self.index.add(np.array([embedding], dtype=np.float32))
            
            # Store complaint data
            self.complaint_data.append({
                "id": complaint_id,
                "text": text,
                "embedding": embedding
            })
            
        except Exception as e:
            logger.error("Failed to add complaint to duplicate detector", error=str(e))
    
    def find_duplicates(self, title: str, description: str, category: str, 
                        location: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """Find potential duplicate complaints"""
        if not self.model or not self.index or len(self.complaint_data) == 0:
            return []
        
        try:
            # Create searchable text
            text = f"{title} {description} {category} {location}"
            
            # Generate embedding
            embedding = self.model.encode([text])[0]
            embedding = embedding / np.linalg.norm(embedding)
            
            # Search in index
            embedding_array = np.array([embedding], dtype=np.float32)
            similarities, indices = self.index.search(embedding_array, min(limit, len(self.complaint_data)))
            
            # Filter by similarity threshold
            duplicates = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity >= self.similarity_threshold:
                    complaint = self.complaint_data[idx]
                    duplicates.append({
                        "complaint_id": complaint["id"],
                        "similarity": float(similarity),
                        "text": complaint["text"]
                    })
            
            return duplicates
            
        except Exception as e:
            logger.error("Failed to find duplicates", error=str(e))
            return []
    
    def save_index(self, filepath: str):
        """Save the FAISS index and data"""
        try:
            if self.index:
                faiss.write_index(self.index, f"{filepath}.index")
            
            with open(f"{filepath}.pkl", "wb") as f:
                pickle.dump(self.complaint_data, f)
            
            logger.info("Duplicate detector index saved", filepath=filepath)
            
        except Exception as e:
            logger.error("Failed to save duplicate detector index", error=str(e))
    
    def load_index(self, filepath: str):
        """Load the FAISS index and data"""
        try:
            if Path(f"{filepath}.index").exists():
                self.index = faiss.read_index(f"{filepath}.index")
            
            if Path(f"{filepath}.pkl").exists():
                with open(f"{filepath}.pkl", "rb") as f:
                    self.complaint_data = pickle.load(f)
            
            logger.info("Duplicate detector index loaded", filepath=filepath)
            
        except Exception as e:
            logger.error("Failed to load duplicate detector index", error=str(e))


class SentimentAnalyzer:
    """Sentiment analysis for complaint feedback"""
    
    def __init__(self):
        self.positive_words = [
            "good", "excellent", "satisfied", "happy", "resolved", "quick",
            "efficient", "helpful", "thank", "thanks", "appreciate", "great"
        ]
        
        self.negative_words = [
            "bad", "poor", "unsatisfied", "unhappy", "slow", "delayed",
            "useless", "waste", "terrible", "awful", "disappointed", "frustrated"
        ]
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of feedback text"""
        text_lower = text.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # Calculate sentiment score
        total_words = positive_count + negative_count
        if total_words == 0:
            sentiment = "neutral"
            score = 0.0
        else:
            score = (positive_count - negative_count) / total_words
            if score > 0.1:
                sentiment = "positive"
            elif score < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_words": positive_count,
            "negative_words": negative_count
        }


class LocationAnalyzer:
    """AI-powered location analysis for complaints"""
    
    def __init__(self):
        self.clusters = {}
        self.cluster_radius = 0.01  # ~1km radius
    
    def add_complaint_location(self, complaint_id: str, lat: float, lng: float):
        """Add complaint location for clustering"""
        # Simple grid-based clustering
        grid_lat = int(lat / self.cluster_radius)
        grid_lng = int(lng / self.cluster_radius)
        cluster_key = f"{grid_lat},{grid_lng}"
        
        if cluster_key not in self.clusters:
            self.clusters[cluster_key] = []
        
        self.clusters[cluster_key].append({
            "complaint_id": complaint_id,
            "lat": lat,
            "lng": lng
        })
    
    def find_nearby_complaints(self, lat: float, lng: float, 
                              radius_km: float = 1.0) -> List[Dict[str, Any]]:
        """Find complaints within specified radius"""
        nearby = []
        
        for cluster in self.clusters.values():
            for complaint in cluster:
                # Simple distance calculation (haversine would be more accurate)
                distance = np.sqrt(
                    (complaint["lat"] - lat) ** 2 + 
                    (complaint["lng"] - lng) ** 2
                ) * 111  # Rough conversion to km
                
                if distance <= radius_km:
                    nearby.append({
                        "complaint_id": complaint["complaint_id"],
                        "distance_km": distance,
                        "lat": complaint["lat"],
                        "lng": complaint["lng"]
                    })
        
        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])
        return nearby
    
    def get_hotspots(self, min_complaints: int = 5) -> List[Dict[str, Any]]:
        """Identify complaint hotspots"""
        hotspots = []
        
        for cluster_key, complaints in self.clusters.items():
            if len(complaints) >= min_complaints:
                # Calculate cluster center
                avg_lat = np.mean([c["lat"] for c in complaints])
                avg_lng = np.mean([c["lng"] for c in complaints])
                
                hotspots.append({
                    "center_lat": avg_lat,
                    "center_lng": avg_lng,
                    "complaint_count": len(complaints),
                    "complaints": [c["complaint_id"] for c in complaints]
                })
        
        # Sort by complaint count
        hotspots.sort(key=lambda x: x["complaint_count"], reverse=True)
        return hotspots


class PredictionService:
    """Service for making predictions and recommendations"""
    
    def __init__(self):
        self.classifier = ComplaintClassifier()
        self.duplicate_detector = DuplicateDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.location_analyzer = LocationAnalyzer()
    
    def process_new_complaint(self, title: str, description: str, 
                             lat: float, lng: float, location_desc: str = "") -> Dict[str, Any]:
        """Process a new complaint with AI analysis"""
        
        # Classification
        classification = self.classifier.classify_complaint(title, description)
        priority = self.classifier.extract_priority(title, description)
        
        # Duplicate detection
        duplicates = self.duplicate_detector.find_duplicates(
            title, description, classification["category"], location_desc
        )
        
        # Location analysis
        nearby = self.location_analyzer.find_nearby_complaints(lat, lng)
        
        return {
            "classification": classification,
            "priority": priority,
            "duplicates": duplicates,
            "nearby_complaints": nearby,
            "is_duplicate": len(duplicates) > 0
        }
    
    def analyze_feedback(self, feedback: str) -> Dict[str, Any]:
        """Analyze user feedback sentiment"""
        return self.sentiment_analyzer.analyze_sentiment(feedback)
    
    def get_recommendations(self, constituency_id: str) -> List[Dict[str, Any]]:
        """Get AI-powered recommendations for constituency"""
        # This would integrate with historical data to provide insights
        recommendations = [
            {
                "type": "infrastructure",
                "title": "Focus on road maintenance",
                "description": "High number of road-related complaints in this area",
                "priority": "high",
                "data_points": 15
            },
            {
                "type": "resource_allocation",
                "title": "Increase street light maintenance",
                "description": "Street light complaints have 30% increase this month",
                "priority": "medium",
                "data_points": 8
            }
        ]
        
        return recommendations


# Global AI service instance
ai_service = PredictionService()
