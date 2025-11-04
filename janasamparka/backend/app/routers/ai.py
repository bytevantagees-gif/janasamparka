"""
AI router - Duplicate detection and AI-powered features
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import numpy as np

from app.core.database import get_db
from app.models.complaint import Complaint

router = APIRouter()

# Global variable for model and index (will be initialized on first use)
_model = None
_faiss_index = None
_complaint_embeddings = {}


def get_embedding_model():
    """
    Lazy load the sentence transformer model
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Use multilingual model for Kannada + English support
            _model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI model not available. Please install sentence-transformers."
            )
    return _model


def get_faiss_index():
    """
    Lazy load the FAISS index
    """
    global _faiss_index
    if _faiss_index is None:
        try:
            import faiss
            # Initialize with dimension 768 (model embedding size)
            _faiss_index = faiss.IndexFlatL2(768)
        except Exception as e:
            print(f"Error loading FAISS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FAISS not available. Please install faiss-cpu."
            )
    return _faiss_index


def generate_embedding(text: str):
    """
    Generate embedding for given text
    """
    model = get_embedding_model()
    embedding = model.encode([text])[0]
    return embedding


@router.post("/duplicate-check")
async def check_for_duplicates(
    title: str,
    description: str,
    threshold: float = 0.85,
    db: Session = Depends(get_db)
):
    """
    Check if a complaint is a duplicate of existing complaints
    
    Returns list of similar complaints with similarity scores
    """
    try:
        model = get_embedding_model()
        
        # Combine title and description for embedding
        complaint_text = f"{title} {description}"
        new_embedding = generate_embedding(complaint_text)
        
        # Get all complaints for comparison
        complaints = db.query(Complaint).all()
        
        if not complaints:
            return {
                "is_duplicate": False,
                "similar_complaints": [],
                "message": "No existing complaints to compare"
            }
        
        # Calculate similarities
        similar_complaints = []
        
        for complaint in complaints:
            existing_text = f"{complaint.title} {complaint.description}"
            existing_embedding = generate_embedding(existing_text)
            
            # Calculate cosine similarity
            similarity = np.dot(new_embedding, existing_embedding) / (
                np.linalg.norm(new_embedding) * np.linalg.norm(existing_embedding)
            )
            
            if similarity >= threshold:
                similar_complaints.append({
                    "complaint_id": str(complaint.id),
                    "title": complaint.title,
                    "description": complaint.description,
                    "similarity_score": round(float(similarity), 3),
                    "status": complaint.status.value if hasattr(complaint.status, 'value') else complaint.status,
                    "created_at": complaint.created_at.isoformat() if complaint.created_at else None
                })
        
        # Sort by similarity
        similar_complaints.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return {
            "is_duplicate": len(similar_complaints) > 0,
            "duplicate_count": len(similar_complaints),
            "similar_complaints": similar_complaints[:5],  # Top 5 similar
            "threshold": threshold,
            "message": "Potential duplicates found" if similar_complaints else "No duplicates found"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking for duplicates: {str(e)}"
        )


@router.get("/complaints/{complaint_id}/similar")
async def find_similar_complaints(
    complaint_id: UUID,
    limit: int = 5,
    threshold: float = 0.75,
    db: Session = Depends(get_db)
):
    """
    Find complaints similar to a given complaint
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    try:
        model = get_embedding_model()
        
        # Get embedding for target complaint
        target_text = f"{complaint.title} {complaint.description}"
        target_embedding = generate_embedding(target_text)
        
        # Get all other complaints
        other_complaints = db.query(Complaint).filter(Complaint.id != complaint_id).all()
        
        similar_complaints = []
        
        for other in other_complaints:
            other_text = f"{other.title} {other.description}"
            other_embedding = generate_embedding(other_text)
            
            # Calculate similarity
            similarity = np.dot(target_embedding, other_embedding) / (
                np.linalg.norm(target_embedding) * np.linalg.norm(other_embedding)
            )
            
            if similarity >= threshold:
                similar_complaints.append({
                    "complaint_id": str(other.id),
                    "title": other.title,
                    "description": other.description,
                    "similarity_score": round(float(similarity), 3),
                    "status": other.status.value if hasattr(other.status, 'value') else other.status,
                    "category": other.category,
                    "created_at": other.created_at.isoformat() if other.created_at else None
                })
        
        # Sort by similarity
        similar_complaints.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return {
            "target_complaint_id": str(complaint_id),
            "similar_count": len(similar_complaints),
            "similar_complaints": similar_complaints[:limit],
            "threshold": threshold
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar complaints: {str(e)}"
        )


@router.post("/complaints/merge")
async def merge_complaints(
    primary_id: UUID,
    duplicate_ids: List[UUID],
    db: Session = Depends(get_db)
):
    """
    Merge duplicate complaints into a primary complaint
    """
    primary = db.query(Complaint).filter(Complaint.id == primary_id).first()
    
    if not primary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Primary complaint not found"
        )
    
    duplicates = db.query(Complaint).filter(Complaint.id.in_(duplicate_ids)).all()
    
    if len(duplicates) != len(duplicate_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some duplicate complaints not found"
        )
    
    # Merge logic:
    # 1. Mark duplicates as closed with reference to primary
    # 2. Transfer media from duplicates to primary (optional)
    # 3. Add note in status log
    
    merged_ids = []
    for duplicate in duplicates:
        duplicate.status = "closed"
        duplicate.updated_at = datetime.utcnow()
        # Add a note field if it exists
        # duplicate.merge_note = f"Merged into complaint {primary_id}"
        merged_ids.append(str(duplicate.id))
    
    db.commit()
    
    return {
        "primary_complaint_id": str(primary_id),
        "merged_complaint_ids": merged_ids,
        "merged_count": len(merged_ids),
        "message": f"Successfully merged {len(merged_ids)} complaints into primary complaint"
    }


@router.post("/summarize")
async def summarize_complaint(
    title: str,
    description: str
):
    """
    Generate AI summary of complaint
    
    Note: Requires OpenAI API key configuration
    """
    try:
        import openai
        from app.core.config import settings
        
        # This would require OpenAI API key in settings
        # For now, return a placeholder
        
        return {
            "original": {
                "title": title,
                "description": description
            },
            "summary": "AI summarization requires OpenAI API configuration",
            "key_points": [
                "Feature not yet configured",
                "Requires OpenAI API key"
            ],
            "note": "To enable: Add OPENAI_API_KEY to environment variables"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="AI summarization not configured"
        )
