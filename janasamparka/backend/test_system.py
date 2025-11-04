"""
Quick system validation script
Run this to check if everything is set up correctly
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required packages are installed"""
    print("🧪 Testing Python imports...")
    try:
        import fastapi
        import sqlalchemy
        import alembic
        import pydantic
        import geoalchemy2
        print("✅ All Python packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing database connection...")
    try:
        from app.core.database import SessionLocal, engine
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(sa.text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure PostgreSQL is running: docker-compose up -d db")
        return False

def test_models():
    """Test if models are properly defined"""
    print("\n🧪 Testing database models...")
    try:
        from app.models import (
            Constituency, User, Ward, Department, 
            Complaint, Media, StatusLog, Poll, PollOption, Vote
        )
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_migrations():
    """Check migration status"""
    print("\n🧪 Checking database migrations...")
    try:
        from alembic.config import Config
        from alembic import command
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        from app.core.database import engine
        
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
            if current_rev:
                print(f"✅ Migrations applied (revision: {current_rev[:12]})")
                return True
            else:
                print("⚠️  No migrations applied yet")
                print("💡 Run: alembic upgrade head")
                return False
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

def test_seed_data():
    """Check if seed data exists"""
    print("\n🧪 Checking seed data...")
    try:
        from app.core.database import SessionLocal
        from app.models import Constituency
        import sqlalchemy as sa
        
        db = SessionLocal()
        count = db.query(Constituency).count()
        db.close()
        
        if count >= 3:
            print(f"✅ Seed data exists ({count} constituencies)")
            return True
        else:
            print(f"⚠️  Only {count} constituencies found")
            print("💡 Run: python seed_data.py")
            return False
    except Exception as e:
        print(f"❌ Seed data check failed: {e}")
        return False

def test_constituencies():
    """List constituencies if they exist"""
    print("\n📋 Listing constituencies...")
    try:
        from app.core.database import SessionLocal
        from app.models import Constituency
        
        db = SessionLocal()
        constituencies = db.query(Constituency).all()
        
        if constituencies:
            for c in constituencies:
                print(f"   • {c.name} ({c.code}) - {c.mla_name}")
            db.close()
            return True
        else:
            print("   No constituencies found")
            db.close()
            return False
    except Exception as e:
        print(f"❌ Failed to list constituencies: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Janasamparka System Validation")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database_connection()))
    results.append(("Models", test_models()))
    results.append(("Migrations", test_migrations()))
    results.append(("Seed Data", test_seed_data()))
    results.append(("Constituencies", test_constituencies()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\n🚀 Start the servers:")
        print("   Backend:  uvicorn app.main:app --reload")
        print("   Frontend: cd ../admin-dashboard && npm run dev")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    # Import sqlalchemy for database test
    import sqlalchemy as sa
    
    success = main()
    sys.exit(0 if success else 1)
