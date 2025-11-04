"""
Test script for new intelligent complaint management features
"""
import sys
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.complaint import Complaint
from app.models.user import User
from app.models.constituency import Constituency
from app.models.ward import Ward
from app.models.department import Department
from app.models.budget import WardBudget, BudgetTransaction
from app.models.faq import FAQSolution


def test_duplicate_detection():
    """Test duplicate detection with geographic proximity"""
    print("\n=== Testing Duplicate Detection ===")
    
    db = SessionLocal()
    try:
        # Find two complaints in the same area
        complaints = db.execute(
            select(Complaint)
            .where(Complaint.lat.isnot(None), Complaint.lng.isnot(None))
            .limit(2)
        ).scalars().all()
        
        if len(complaints) < 2:
            print("❌ Need at least 2 complaints with coordinates to test")
            return
        
        c1, c2 = complaints[0], complaints[1]
        print(f"✓ Found complaint 1: {c1.title} at ({c1.lat}, {c1.lng})")
        print(f"✓ Found complaint 2: {c2.title} at ({c2.lat}, {c2.lng})")
        
        # Calculate distance
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371000  # Radius of earth in meters
            return c * r
        
        distance = haversine(c1.lng, c1.lat, c2.lng, c2.lat)
        print(f"✓ Distance between complaints: {distance:.2f}m")
        
        # Check new columns
        print(f"\nComplaint 1 attributes:")
        print(f"  - priority_score: {c1.priority_score}")
        print(f"  - is_emergency: {c1.is_emergency}")
        print(f"  - is_duplicate: {c1.is_duplicate}")
        print(f"  - duplicate_count: {c1.duplicate_count}")
    finally:
        db.close()


def test_budget_tracking():
    """Test budget tracking tables"""
    print("\n=== Testing Budget Tracking ===")
    
    db = SessionLocal()
    try:
        # Check if budget tables have data
        ward_budget = db.execute(select(WardBudget).limit(1)).scalar_one_or_none()
        
        if ward_budget:
            print(f"✓ Found ward budget:")
            print(f"  - Ward ID: {ward_budget.ward_id}")
            print(f"  - Financial Year: {ward_budget.financial_year}")
            print(f"  - Category: {ward_budget.category}")
            print(f"  - Allocated: ₹{ward_budget.allocated:,}")
            print(f"  - Spent: ₹{ward_budget.spent:,}")
            print(f"  - Remaining: ₹{ward_budget.remaining:,}")
            print(f"  - Utilization: {ward_budget.utilization_percentage:.1f}%")
        else:
            print("ℹ️  No ward budgets found in database")
            print("✓ Budget tables exist and are accessible")
    finally:
        db.close()


def test_faq_system():
    """Test FAQ/Knowledge base"""
    print("\n=== Testing FAQ System ===")
    
    db = SessionLocal()
    try:
        # Check if FAQ table has data
        faq = db.execute(select(FAQSolution).limit(1)).scalar_one_or_none()
        
        if faq:
            print(f"✓ Found FAQ:")
            print(f"  - Title: {faq.title}")
            print(f"  - Category: {faq.category}")
            print(f"  - Keywords: {faq.question_keywords}")
            print(f"  - View Count: {faq.view_count}")
            print(f"  - Helpful: {faq.helpful_count}")
            print(f"  - Prevented Complaints: {faq.prevented_complaints_count}")
            print(f"  - Success Rate: {faq.success_rate:.1f}%")
            print(f"  - Effectiveness Score: {faq.effectiveness_score:.1f}")
        else:
            print("ℹ️  No FAQs found in database")
            print("✓ FAQ tables exist and are accessible")
    finally:
        db.close()


def test_multilingual_normalizer():
    """Test multilingual text normalization"""
    print("\n=== Testing Multilingual NLP ===")
    
    from app.services.predictive_planning_service import MultilingualNormalizer
    
    normalizer = MultilingualNormalizer()
    
    test_cases = [
        "raste mele guddi ide bega fix maadi",
        "niru supply problemm very urgant",
        "bandi problm road brokan",
        "kachada problem entire ward",
    ]
    
    for text in test_cases:
        normalized = normalizer.normalize_text(text)
        print(f"✓ '{text}'")
        print(f"  → '{normalized}'")


def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING NEW INTELLIGENT COMPLAINT MANAGEMENT FEATURES")
    print("=" * 60)
    
    try:
        test_duplicate_detection()
        test_budget_tracking()
        test_faq_system()
        test_multilingual_normalizer()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
