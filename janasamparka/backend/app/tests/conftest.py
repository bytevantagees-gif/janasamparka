"""
Pytest configuration and fixtures for Janasamparka testing
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.complaint import Complaint, ComplaintStatus, ComplaintPriority
from app.models.constituency import Constituency
from app.models.department import Department
from app.models.ward import Ward


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db() -> Generator:
    """Create a fresh database for each test"""
    # Create test database engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db) -> Generator:
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(test_db) -> AsyncGenerator:
    """Create an async test client"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_constituency(test_db) -> Constituency:
    """Create a test constituency"""
    constituency = Constituency(
        name="Test Constituency",
        description="Test constituency for unit tests",
        is_active=True
    )
    test_db.add(constituency)
    test_db.commit()
    test_db.refresh(constituency)
    return constituency


@pytest.fixture
def test_department(test_db, test_constituency) -> Department:
    """Create a test department"""
    department = Department(
        name="Test Department",
        description="Test department for unit tests",
        constituency_id=test_constituency.id,
        contact_phone="+1234567890",
        contact_email="test@dept.com"
    )
    test_db.add(department)
    test_db.commit()
    test_db.refresh(department)
    return department


@pytest.fixture
def test_ward(test_db, test_constituency) -> Ward:
    """Create a test ward"""
    ward = Ward(
        name="Test Ward",
        number=1,
        constituency_id=test_constituency.id,
        population=1000
    )
    test_db.add(ward)
    test_db.commit()
    test_db.refresh(ward)
    return ward


@pytest.fixture
def test_admin_user(test_db, test_constituency) -> User:
    """Create a test admin user"""
    admin_user = User(
        name="Test Admin",
        phone="+919876543210",
        email="admin@test.com",
        role=UserRole.ADMIN,
        constituency_id=None,  # Admin can access all
        is_active=True,
        is_verified=True
    )
    test_db.add(admin_user)
    test_db.commit()
    test_db.refresh(admin_user)
    return admin_user


@pytest.fixture
def test_mla_user(test_db, test_constituency) -> User:
    """Create a test MLA user"""
    mla_user = User(
        name="Test MLA",
        phone="+919876543211",
        email="mla@test.com",
        role=UserRole.MLA,
        constituency_id=test_constituency.id,
        is_active=True,
        is_verified=True
    )
    test_db.add(mla_user)
    test_db.commit()
    test_db.refresh(mla_user)
    return mla_user


@pytest.fixture
def test_citizen_user(test_db, test_constituency) -> User:
    """Create a test citizen user"""
    citizen_user = User(
        name="Test Citizen",
        phone="+919876543212",
        email="citizen@test.com",
        role=UserRole.CITIZEN,
        constituency_id=test_constituency.id,
        is_active=True,
        is_verified=True
    )
    test_db.add(citizen_user)
    test_db.commit()
    test_db.refresh(citizen_user)
    return citizen_user


@pytest.fixture
def test_complaint(test_db, test_constituency, test_citizen_user, test_department) -> Complaint:
    """Create a test complaint"""
    complaint = Complaint(
        title="Test Complaint",
        description="This is a test complaint for unit testing",
        category="road",
        constituency_id=test_constituency.id,
        user_id=test_citizen_user.id,
        dept_id=test_department.id,
        status=ComplaintStatus.SUBMITTED,
        priority=ComplaintPriority.MEDIUM,
        lat=12.9716,
        lng=77.5946
    )
    test_db.add(complaint)
    test_db.commit()
    test_db.refresh(complaint)
    return complaint


@pytest.fixture
def auth_headers_admin(client, test_admin_user) -> dict:
    """Get authentication headers for admin user"""
    # Request OTP
    client.post("/api/auth/request-otp", json={"phone": test_admin_user.phone})
    
    # Verify OTP and get token
    response = client.post("/api/auth/verify-otp", json={
        "phone": test_admin_user.phone,
        "otp": "123456"  # Default test OTP
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_mla(client, test_mla_user) -> dict:
    """Get authentication headers for MLA user"""
    # Request OTP
    client.post("/api/auth/request-otp", json={"phone": test_mla_user.phone})
    
    # Verify OTP and get token
    response = client.post("/api/auth/verify-otp", json={
        "phone": test_mla_user.phone,
        "otp": "123456"  # Default test OTP
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_citizen(client, test_citizen_user) -> dict:
    """Get authentication headers for citizen user"""
    # Request OTP
    client.post("/api/auth/request-otp", json={"phone": test_citizen_user.phone})
    
    # Verify OTP and get token
    response = client.post("/api/auth/verify-otp", json={
        "phone": test_citizen_user.phone,
        "otp": "123456"  # Default test OTP
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing"""
    return {
        "file": ("test.jpg", b"fake image data", "image/jpeg")
    }


# Test data fixtures
@pytest.fixture
def sample_complaint_data(test_constituency):
    """Sample complaint data for testing"""
    return {
        "title": "Pothole on Main Road",
        "description": "Large pothole causing accidents",
        "category": "road",
        "lat": 12.9716,
        "lng": 77.5946,
        "location_description": "Near bus stand",
        "constituency_id": str(test_constituency.id)
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "name": "Test User",
        "phone": "+919876543219",
        "email": "newuser@test.com",
        "role": "citizen"
    }


# Performance testing fixtures
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests"""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return PerformanceMonitor()


# Mock external services
@pytest.fixture
def mock_sms_service():
    """Mock SMS service for testing"""
    class MockSMS:
        def __init__(self):
            self.sent_messages = []
        
        def send_otp(self, phone: str, otp: str):
            self.sent_messages.append({
                "phone": phone,
                "otp": otp,
                "timestamp": "2024-01-01T00:00:00Z"
            })
            return True
    
    return MockSMS()


@pytest.fixture
def mock_file_storage():
    """Mock file storage for testing"""
    class MockStorage:
        def __init__(self):
            self.uploaded_files = []
        
        def upload(self, file_data, filename):
            self.uploaded_files.append({
                "filename": filename,
                "size": len(file_data),
                "url": f"http://test-uploads/{filename}"
            })
            return f"http://test-uploads/{filename}"
    
    return MockStorage()
