"""
Test utilities and helper functions
"""
import random
import string
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any
from uuid import uuid4

from app.models.user import UserRole
from app.models.complaint import ComplaintStatus, ComplaintPriority, MediaType


def generate_test_phone() -> str:
    """Generate a random test phone number"""
    return f"+9198{random.randint(10000000, 99999999)}"


def generate_test_email() -> str:
    """Generate a random test email"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"test.{username}@janasamparka.test"


def generate_test_name() -> str:
    """Generate a random test name"""
    first_names = ["Ramu", "Sita", "Gopal", "Lakshmi", "Ravi", "Anita", "Kumar", "Priya"]
    last_names = ["Kumar", "Devi", "Singh", "Reddy", "Nair", "Iyer", "Patel", "Sharma"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_test_complaint_data(constituency_id: str) -> Dict[str, Any]:
    """Generate random complaint data for testing"""
    categories = ["road", "water", "electricity", "street_light", "garbage", "drainage", "tree"]
    titles = [
        "Pothole on main road",
        "Water supply interrupted", 
        "Street light not working",
        "Garbage not collected",
        "Drainage blocked",
        "Tree branches overhanging",
        "Power outage in area"
    ]
    
    return {
        "title": random.choice(titles),
        "description": f"This is a test complaint created at {datetime.now().isoformat()}",
        "category": random.choice(categories),
        "lat": str(Decimal(str(random.uniform(12.8, 13.2)))),
        "lng": str(Decimal(str(random.uniform(77.4, 77.8)))),
        "location_description": f"Test location {random.randint(1, 100)}",
        "constituency_id": constituency_id,
        "priority": random.choice(["low", "medium", "high"])
    }


def generate_test_user_data(role: UserRole = UserRole.CITIZEN) -> Dict[str, Any]:
    """Generate random user data for testing"""
    return {
        "name": generate_test_name(),
        "phone": generate_test_phone(),
        "email": generate_test_email(),
        "role": role.value
    }


def create_test_token(user_id: str, secret_key: str = "test-secret") -> str:
    """Create a test JWT token"""
    from jose import jwt
    
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    return jwt.encode(payload, secret_key, algorithm="HS256")


def assert_complaint_structure(complaint: Dict[str, Any]) -> None:
    """Assert complaint response has correct structure"""
    required_fields = [
        "id", "title", "description", "status", "priority", 
        "category", "created_at", "updated_at", "constituency_id"
    ]
    
    for field in required_fields:
        assert field in complaint, f"Missing required field: {field}"
    
    # Validate UUID format
    uuid.UUID(complaint["id"])
    uuid.UUID(complaint["constituency_id"])
    
    # Validate enum values
    assert complaint["status"] in [s.value for s in ComplaintStatus]
    assert complaint["priority"] in [p.value for p in ComplaintPriority]


def assert_user_structure(user: Dict[str, Any]) -> None:
    """Assert user response has correct structure"""
    required_fields = ["id", "name", "phone", "email", "role", "is_active"]
    
    for field in required_fields:
        assert field in user, f"Missing required field: {field}"
    
    # Validate UUID format
    uuid.UUID(user["id"])
    
    # Validate enum values
    assert user["role"] in [r.value for r in UserRole]


def assert_department_structure(department: Dict[str, Any]) -> None:
    """Assert department response has correct structure"""
    required_fields = ["id", "name", "description", "constituency_id"]
    
    for field in required_fields:
        assert field in department, f"Missing required field: {field}"
    
    # Validate UUID format
    uuid.UUID(department["id"])
    uuid.UUID(department["constituency_id"])


def assert_paginated_response(response: Dict[str, Any]) -> None:
    """Assert paginated response has correct structure"""
    required_fields = ["items", "total", "page", "size", "pages"]
    
    for field in required_fields:
        assert field in response, f"Missing required field: {field}"
    
    assert isinstance(response["items"], list)
    assert isinstance(response["total"], int)
    assert isinstance(response["page"], int)
    assert isinstance(response["size"], int)
    assert isinstance(response["pages"], int)


class TestDataGenerator:
    """Helper class for generating test data"""
    
    @staticmethod
    def constituency():
        """Generate test constituency data"""
        return {
            "name": f"Test Constituency {random.randint(1, 100)}",
            "description": f"Test constituency description {random.randint(1, 100)}",
            "is_active": True
        }
    
    @staticmethod
    def department(constituency_id: str):
        """Generate test department data"""
        return {
            "name": f"Test Department {random.randint(1, 100)}",
            "description": f"Test department description {random.randint(1, 100)}",
            "constituency_id": constituency_id,
            "contact_phone": generate_test_phone(),
            "contact_email": generate_test_email()
        }
    
    @staticmethod
    def ward(constituency_id: str):
        """Generate test ward data"""
        return {
            "name": f"Test Ward {random.randint(1, 100)}",
            "number": random.randint(1, 50),
            "constituency_id": constituency_id,
            "population": random.randint(1000, 10000),
            "area": round(random.uniform(1.0, 20.0), 2)
        }


class PerformanceTracker:
    """Track performance during tests"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_start = None
        self.memory_end = None
    
    def start(self):
        """Start tracking"""
        import time
        import psutil
        import os
        
        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        self.memory_start = process.memory_info().rss / 1024 / 1024  # MB
    
    def stop(self):
        """Stop tracking"""
        import time
        import psutil
        import os
        
        self.end_time = time.time()
        process = psutil.Process(os.getpid())
        self.memory_end = process.memory_info().rss / 1024 / 1024  # MB
    
    @property
    def duration(self) -> float:
        """Get duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def memory_used(self) -> float:
        """Get memory used in MB"""
        if self.memory_start and self.memory_end:
            return self.memory_end - self.memory_start
        return None
    
    def assert_performance(self, max_duration: float = 1.0, max_memory: float = 50.0):
        """Assert performance constraints"""
        if self.duration:
            assert self.duration < max_duration, f"Test took {self.duration:.2f}s, expected < {max_duration}s"
        
        if self.memory_used:
            assert self.memory_used < max_memory, f"Test used {self.memory_used:.2f}MB, expected < {max_memory}MB"


class MockResponse:
    """Mock HTTP response for testing"""
    
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code
    
    def json(self) -> Dict[str, Any]:
        return self._json_data
    
    @property
    def text(self) -> str:
        return str(self._json_data)


def create_mock_file(filename: str = "test.jpg", content: bytes = b"fake image data") -> Dict[str, Any]:
    """Create mock file data for upload testing"""
    return {
        "file": (filename, content, "image/jpeg")
    }


def assert_error_response(response: Dict[str, Any], expected_status: int, expected_detail: str = None):
    """Assert error response structure"""
    assert "detail" in response
    if expected_detail:
        assert expected_detail.lower() in response["detail"].lower()


class DatabaseCleaner:
    """Helper to clean test database"""
    
    @staticmethod
    def clean_all_tables(db_session):
        """Clean all test tables"""
        # Delete in order of dependencies
        db_session.execute("DELETE FROM status_logs")
        db_session.execute("DELETE FROM media")
        db_session.execute("DELETE FROM complaints")
        db_session.execute("DELETE FROM users")
        db_session.execute("DELETE FROM wards")
        db_session.execute("DELETE FROM departments")
        db_session.execute("DELETE FROM constituencies")
        db_session.commit()


def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
    """Wait for a condition to be true"""
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    
    raise TimeoutError(f"Condition not met within {timeout} seconds")
