"""
Unit tests for database models
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

from app.models.user import User, UserRole
from app.models.complaint import Complaint, ComplaintStatus, ComplaintPriority, Media, MediaType, StatusLog
from app.models.constituency import Constituency
from app.models.department import Department
from app.models.ward import Ward


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, test_constituency):
        """Test creating a user"""
        user = User(
            name="Test User",
            phone="+919876543210",
            email="test@example.com",
            role=UserRole.CITIZEN,
            constituency_id=test_constituency.id,
            is_active=True,
            is_verified=True
        )
        
        assert user.name == "Test User"
        assert user.phone == "+919876543210"
        assert user.email == "test@example.com"
        assert user.role == UserRole.CITIZEN
        assert user.constituency_id == test_constituency.id
        assert user.is_active is True
        assert user.is_verified is True
    
    def test_user_role_enum(self):
        """Test user role enum values"""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MLA.value == "mla"
        assert UserRole.MODERATOR.value == "moderator"
        assert UserRole.DEPARTMENT_OFFICER.value == "department_officer"
        assert UserRole.CITIZEN.value == "citizen"
        assert UserRole.AUDITOR.value == "auditor"
    
    def test_user_repr(self, test_constituency):
        """Test user string representation"""
        user = User(
            name="Test User",
            phone="+919876543210",
            role=UserRole.CITIZEN,
            constituency_id=test_constituency.id
        )
        
        repr_str = repr(user)
        assert "Test User" in repr_str
        assert "+919876543210" in repr_str
    
    def test_user_admin_no_constituency(self):
        """Test admin user doesn't require constituency"""
        admin_user = User(
            name="Admin User",
            phone="+919876543210",
            role=UserRole.ADMIN,
            constituency_id=None  # Admin can have None
        )
        
        assert admin_user.role == UserRole.ADMIN
        assert admin_user.constituency_id is None


class TestConstituencyModel:
    """Test Constituency model functionality"""
    
    def test_constituency_creation(self):
        """Test creating a constituency"""
        constituency = Constituency(
            name="Test Constituency",
            description="Test constituency description",
            is_active=True
        )
        
        assert constituency.name == "Test Constituency"
        assert constituency.description == "Test constituency description"
        assert constituency.is_active is True
        assert constituency.id is not None
    
    def test_constituency_repr(self):
        """Test constituency string representation"""
        constituency = Constituency(name="Test Constituency")
        repr_str = repr(constituency)
        assert "Test Constituency" in repr_str


class TestDepartmentModel:
    """Test Department model functionality"""
    
    def test_department_creation(self, test_constituency):
        """Test creating a department"""
        department = Department(
            name="Test Department",
            description="Test department description",
            constituency_id=test_constituency.id,
            contact_phone="+1234567890",
            contact_email="dept@example.com"
        )
        
        assert department.name == "Test Department"
        assert department.constituency_id == test_constituency.id
        assert department.contact_phone == "+1234567890"
        assert department.contact_email == "dept@example.com"
    
    def test_department_repr(self, test_constituency):
        """Test department string representation"""
        department = Department(
            name="Test Department",
            constituency_id=test_constituency.id
        )
        repr_str = repr(department)
        assert "Test Department" in repr_str


class TestWardModel:
    """Test Ward model functionality"""
    
    def test_ward_creation(self, test_constituency):
        """Test creating a ward"""
        ward = Ward(
            name="Test Ward",
            number=1,
            constituency_id=test_constituency.id,
            population=5000,
            area=10.5
        )
        
        assert ward.name == "Test Ward"
        assert ward.number == 1
        assert ward.constituency_id == test_constituency.id
        assert ward.population == 5000
        assert ward.area == 10.5
    
    def test_ward_repr(self, test_constituency):
        """Test ward string representation"""
        ward = Ward(
            name="Test Ward",
            number=1,
            constituency_id=test_constituency.id
        )
        repr_str = repr(ward)
        assert "Test Ward" in repr_str


class TestComplaintModel:
    """Test Complaint model functionality"""
    
    def test_complaint_creation(self, test_constituency, test_citizen_user, test_department):
        """Test creating a complaint"""
        complaint = Complaint(
            title="Test Complaint",
            description="This is a test complaint",
            category="road",
            constituency_id=test_constituency.id,
            user_id=test_citizen_user.id,
            dept_id=test_department.id,
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.MEDIUM,
            lat=Decimal("12.9716"),
            lng=Decimal("77.5946"),
            location_description="Near bus stand"
        )
        
        assert complaint.title == "Test Complaint"
        assert complaint.description == "This is a test complaint"
        assert complaint.category == "road"
        assert complaint.constituency_id == test_constituency.id
        assert complaint.user_id == test_citizen_user.id
        assert complaint.dept_id == test_department.id
        assert complaint.status == ComplaintStatus.SUBMITTED
        assert complaint.priority == ComplaintPriority.MEDIUM
        assert complaint.lat == Decimal("12.9716")
        assert complaint.lng == Decimal("77.5946")
        assert complaint.location_description == "Near bus stand"
        assert complaint.is_emergency is False
        assert complaint.is_duplicate is False
    
    def test_complaint_enums(self):
        """Test complaint enum values"""
        # Status enum
        assert ComplaintStatus.SUBMITTED.value == "submitted"
        assert ComplaintStatus.ASSIGNED.value == "assigned"
        assert ComplaintStatus.IN_PROGRESS.value == "in_progress"
        assert ComplaintStatus.RESOLVED.value == "resolved"
        assert ComplaintStatus.CLOSED.value == "closed"
        assert ComplaintStatus.REJECTED.value == "rejected"
        
        # Priority enum
        assert ComplaintPriority.LOW.value == "low"
        assert ComplaintPriority.MEDIUM.value == "medium"
        assert ComplaintPriority.HIGH.value == "high"
        assert ComplaintPriority.URGENT.value == "urgent"
    
    def test_complaint_timestamps(self, test_constituency, test_citizen_user, test_department):
        """Test complaint timestamp functionality"""
        before_creation = datetime.now(timezone.utc)
        
        complaint = Complaint(
            title="Test Complaint",
            description="This is a test complaint",
            constituency_id=test_constituency.id,
            user_id=test_citizen_user.id,
            dept_id=test_department.id
        )
        
        after_creation = datetime.now(timezone.utc)
        
        assert complaint.created_at is not None
        assert complaint.updated_at is not None
        assert complaint.last_activity_at is not None
        assert before_creation <= complaint.created_at <= after_creation
    
    def test_complaint_emergency_flag(self, test_constituency, test_citizen_user, test_department):
        """Test emergency complaint functionality"""
        complaint = Complaint(
            title="Emergency Complaint",
            description="This is an emergency",
            constituency_id=test_constituency.id,
            user_id=test_citizen_user.id,
            dept_id=test_department.id,
            is_emergency=True
        )
        
        assert complaint.is_emergency is True
    
    def test_complaint_duplicate_handling(self, test_constituency, test_citizen_user, test_department):
        """Test duplicate complaint handling"""
        parent_complaint_id = uuid4()
        
        complaint = Complaint(
            title="Duplicate Complaint",
            description="This is a duplicate",
            constituency_id=test_constituency.id,
            user_id=test_citizen_user.id,
            dept_id=test_department.id,
            is_duplicate=True,
            parent_complaint_id=parent_complaint_id,
            duplicate_count=2
        )
        
        assert complaint.is_duplicate is True
        assert complaint.parent_complaint_id == parent_complaint_id
        assert complaint.duplicate_count == 2
    
    def test_complaint_repr(self, test_constituency, test_citizen_user, test_department):
        """Test complaint string representation"""
        complaint = Complaint(
            title="Test Complaint with a very long title that should be truncated",
            description="Test description",
            constituency_id=test_constituency.id,
            user_id=test_citizen_user.id,
            dept_id=test_department.id
        )
        
        repr_str = repr(complaint)
        assert str(complaint.id) in repr_str
        assert len(repr_str) < 100  # Should be truncated


class TestMediaModel:
    """Test Media model functionality"""
    
    def test_media_creation(self, test_complaint):
        """Test creating media attachment"""
        media = Media(
            complaint_id=test_complaint.id,
            url="http://example.com/image.jpg",
            media_type=MediaType.PHOTO,
            file_size=1024.5,
            lat=Decimal("12.9716"),
            lng=Decimal("77.5946"),
            proof_type="before",
            photo_type="evidence",
            caption="Photo of the issue"
        )
        
        assert media.complaint_id == test_complaint.id
        assert media.url == "http://example.com/image.jpg"
        assert media.media_type == MediaType.PHOTO
        assert media.file_size == 1024.5
        assert media.lat == Decimal("12.9716")
        assert media.lng == Decimal("77.5946")
        assert media.proof_type == "before"
        assert media.photo_type == "evidence"
        assert media.caption == "Photo of the issue"
    
    def test_media_enum(self):
        """Test media type enum values"""
        assert MediaType.PHOTO.value == "photo"
        assert MediaType.VIDEO.value == "video"
        assert MediaType.AUDIO.value == "audio"
        assert MediaType.DOCUMENT.value == "document"
    
    def test_media_repr(self, test_complaint):
        """Test media string representation"""
        media = Media(
            complaint_id=test_complaint.id,
            url="http://example.com/image.jpg",
            media_type=MediaType.PHOTO
        )
        
        repr_str = repr(media)
        assert "photo" in repr_str
        assert "http://example.com/image.jpg" in repr_str


class TestStatusLogModel:
    """Test StatusLog model functionality"""
    
    def test_status_log_creation(self, test_complaint, test_citizen_user):
        """Test creating status log"""
        status_log = StatusLog(
            complaint_id=test_complaint.id,
            old_status=ComplaintStatus.SUBMITTED.value,
            new_status=ComplaintStatus.ASSIGNED.value,
            changed_by=test_citizen_user.id,
            note="Status updated for testing"
        )
        
        assert status_log.complaint_id == test_complaint.id
        assert status_log.old_status == ComplaintStatus.SUBMITTED.value
        assert status_log.new_status == ComplaintStatus.ASSIGNED.value
        assert status_log.changed_by == test_citizen_user.id
        assert status_log.note == "Status updated for testing"
    
    def test_status_log_repr(self, test_complaint, test_citizen_user):
        """Test status log string representation"""
        status_log = StatusLog(
            complaint_id=test_complaint.id,
            old_status="submitted",
            new_status="assigned",
            changed_by=test_citizen_user.id
        )
        
        repr_str = repr(status_log)
        assert "submitted" in repr_str
        assert "assigned" in repr_str


class TestModelRelationships:
    """Test model relationships"""
    
    def test_complaint_user_relationship(self, test_complaint, test_citizen_user):
        """Test complaint-user relationship"""
        # This would be tested with actual database session
        # For unit tests, we just verify the foreign key is set
        assert test_complaint.user_id == test_citizen_user.id
    
    def test_complaint_department_relationship(self, test_complaint, test_department):
        """Test complaint-department relationship"""
        assert test_complaint.dept_id == test_department.id
    
    def test_complaint_constituency_relationship(self, test_complaint, test_constituency):
        """Test complaint-constituency relationship"""
        assert test_complaint.constituency_id == test_constituency.id
    
    def test_department_constituency_relationship(self, test_department, test_constituency):
        """Test department-constituency relationship"""
        assert test_department.constituency_id == test_constituency.id
    
    def test_ward_constituency_relationship(self, test_ward, test_constituency):
        """Test ward-constituency relationship"""
        assert test_ward.constituency_id == test_constituency.id
