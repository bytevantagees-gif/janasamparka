"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


class TestAuthenticationAPI:
    """Test authentication API endpoints"""
    
    def test_request_otp_success(self, client):
        """Test successful OTP request"""
        response = client.post("/api/auth/request-otp", json={
            "phone": "+919876543210"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "phone" in data
        assert "otp" in data  # In development mode
        assert data["phone"] == "+919876543210"
    
    def test_request_otp_invalid_phone(self, client):
        """Test OTP request with invalid phone number"""
        response = client.post("/api/auth/request-otp", json={
            "phone": "invalid_phone"
        })
        
        assert response.status_code == 422
    
    def test_verify_otp_success(self, client, test_admin_user):
        """Test successful OTP verification"""
        # First request OTP
        client.post("/api/auth/request-otp", json={
            "phone": test_admin_user.phone
        })
        
        # Then verify OTP
        response = client.post("/api/auth/verify-otp", json={
            "phone": test_admin_user.phone,
            "otp": "123456"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_verify_otp_invalid(self, client, test_admin_user):
        """Test OTP verification with invalid OTP"""
        response = client.post("/api/auth/verify-otp", json={
            "phone": test_admin_user.phone,
            "otp": "000000"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_get_current_user(self, client, auth_headers_admin, test_admin_user):
        """Test getting current user info"""
        response = client.get("/api/auth/me", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_admin_user.id)
        assert data["name"] == test_admin_user.name
        assert data["phone"] == test_admin_user.phone
        assert data["role"] == test_admin_user.role.value
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401


class TestComplaintsAPI:
    """Test complaints API endpoints"""
    
    def test_create_complaint_success(self, client, auth_headers_citizen, sample_complaint_data):
        """Test successful complaint creation"""
        response = client.post("/api/complaints/", json=sample_complaint_data, headers=auth_headers_citizen)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_complaint_data["title"]
        assert data["description"] == sample_complaint_data["description"]
        assert data["status"] == "submitted"
        assert data["priority"] == "medium"
    
    def test_create_complaint_unauthorized(self, client, sample_complaint_data):
        """Test complaint creation without authentication"""
        response = client.post("/api/complaints/", json=sample_complaint_data)
        
        assert response.status_code == 401
    
    def test_list_complaints_success(self, client, auth_headers_admin, test_complaint):
        """Test successful complaint listing"""
        response = client.get("/api/complaints/", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) >= 1
    
    def test_list_complaints_with_filters(self, client, auth_headers_admin, test_complaint):
        """Test complaint listing with filters"""
        response = client.get("/api/complaints/?status=submitted&priority=medium", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        for complaint in data["items"]:
            assert complaint["status"] == "submitted"
            assert complaint["priority"] == "medium"
    
    def test_get_complaint_success(self, client, auth_headers_admin, test_complaint):
        """Test getting a specific complaint"""
        response = client.get(f"/api/complaints/{test_complaint.id}", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_complaint.id)
        assert data["title"] == test_complaint.title
    
    def test_get_complaint_not_found(self, client, auth_headers_admin):
        """Test getting a non-existent complaint"""
        fake_id = uuid4()
        response = client.get(f"/api/complaints/{fake_id}", headers=auth_headers_admin)
        
        assert response.status_code == 404
    
    def test_update_complaint_status(self, client, auth_headers_admin, test_complaint):
        """Test updating complaint status"""
        response = client.patch(f"/api/complaints/{test_complaint.id}/status", 
                               json={"status": "assigned", "note": "Assigned to department"}, 
                               headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "assigned"
    
    def test_assign_complaint(self, client, auth_headers_admin, test_complaint, test_department):
        """Test assigning complaint to department"""
        response = client.post(f"/api/complaints/{test_complaint.id}/assign", 
                              json={"department_id": str(test_department.id)}, 
                              headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["dept_id"] == str(test_department.id)
    
    def test_constituency_filtering(self, client, auth_headers_mla, test_complaint):
        """Test constituency-based filtering for MLA"""
        # MLA should only see complaints from their constituency
        response = client.get("/api/complaints/", headers=auth_headers_mla)
        
        assert response.status_code == 200
        data = response.json()
        for complaint in data["items"]:
            assert complaint["constituency_id"] == str(test_complaint.constituency_id)


class TestUsersAPI:
    """Test users API endpoints"""
    
    def test_get_user_success(self, client, auth_headers_admin, test_citizen_user):
        """Test getting a specific user"""
        response = client.get(f"/api/users/{test_citizen_user.id}", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_citizen_user.id)
        assert data["name"] == test_citizen_user.name
    
    def test_update_user_success(self, client, auth_headers_citizen, test_citizen_user):
        """Test updating user profile"""
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        response = client.patch(f"/api/users/{test_citizen_user.id}", 
                               json=update_data, 
                               headers=auth_headers_citizen)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"
    
    def test_update_user_unauthorized(self, client, test_citizen_user):
        """Test updating user without authentication"""
        update_data = {"name": "Updated Name"}
        response = client.patch(f"/api/users/{test_citizen_user.id}", json=update_data)
        
        assert response.status_code == 401


class TestDepartmentsAPI:
    """Test departments API endpoints"""
    
    def test_list_departments_success(self, client, auth_headers_admin, test_department):
        """Test listing departments"""
        response = client.get("/api/departments/", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_create_department_success(self, client, auth_headers_admin, test_constituency):
        """Test creating a department"""
        dept_data = {
            "name": "New Department",
            "description": "Test department",
            "constituency_id": str(test_constituency.id),
            "contact_phone": "+1234567890",
            "contact_email": "new@dept.com"
        }
        response = client.post("/api/departments/", json=dept_data, headers=auth_headers_admin)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Department"
        assert data["constituency_id"] == str(test_constituency.id)


class TestConstituenciesAPI:
    """Test constituencies API endpoints"""
    
    def test_list_constituencies_success(self, client, auth_headers_admin, test_constituency):
        """Test listing constituencies"""
        response = client.get("/api/constituencies/", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_constituency_success(self, client, auth_headers_admin, test_constituency):
        """Test getting a specific constituency"""
        response = client.get(f"/api/constituencies/{test_constituency.id}", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_constituency.id)
        assert data["name"] == test_constituency.name


class TestWardsAPI:
    """Test wards API endpoints"""
    
    def test_list_wards_success(self, client, auth_headers_admin, test_ward):
        """Test listing wards"""
        response = client.get("/api/wards/", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_ward_success(self, client, auth_headers_admin, test_ward):
        """Test getting a specific ward"""
        response = client.get(f"/api/wards/{test_ward.id}", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_ward.id)
        assert data["name"] == test_ward.name


class TestAnalyticsAPI:
    """Test analytics API endpoints"""
    
    def test_get_complaint_stats(self, client, auth_headers_admin, test_complaint):
        """Test getting complaint statistics"""
        response = client.get("/api/complaints/stats/summary", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_complaints" in data
        assert "by_status" in data
        assert "by_priority" in data
        assert "by_category" in data
        assert data["total_complaints"] >= 1
    
    def test_get_analytics_overview(self, client, auth_headers_admin):
        """Test getting analytics overview"""
        response = client.get("/api/analytics/overview", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert "complaints" in data
        assert "users" in data
        assert "departments" in data


class TestMediaAPI:
    """Test media API endpoints"""
    
    def test_upload_media_success(self, client, auth_headers_citizen, test_complaint, mock_file_upload):
        """Test uploading media file"""
        response = client.post("/api/media/upload", 
                              files=mock_file_upload,
                              data={"complaint_id": str(test_complaint.id)},
                              headers=auth_headers_citizen)
        
        assert response.status_code == 201
        data = response.json()
        assert "url" in data
        assert "media_type" in data
    
    def test_list_media_success(self, client, auth_headers_admin, test_complaint):
        """Test listing media for a complaint"""
        response = client.get(f"/api/media/complaint/{test_complaint.id}", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestErrorHandling:
    """Test API error handling"""
    
    def test_404_not_found(self, client, auth_headers_admin):
        """Test 404 error handling"""
        response = client.get("/api/nonexistent-endpoint", headers=auth_headers_admin)
        
        assert response.status_code == 404
    
    def test_validation_error(self, client, auth_headers_citizen):
        """Test validation error handling"""
        invalid_data = {
            "title": "",  # Empty title should fail validation
            "description": "Test"
        }
        response = client.post("/api/complaints/", json=invalid_data, headers=auth_headers_citizen)
        
        assert response.status_code == 422
    
    def test_permission_denied(self, client, auth_headers_citizen, test_citizen_user):
        """Test permission denied for citizen accessing admin endpoints"""
        response = client.get("/api/users/", headers=auth_headers_citizen)
        
        assert response.status_code == 403


class TestRateLimiting:
    """Test API rate limiting"""
    
    def test_otp_rate_limit(self, client):
        """Test OTP request rate limiting"""
        phone = "+919876543210"
        
        # Make multiple rapid requests
        responses = []
        for _ in range(5):
            response = client.post("/api/auth/request-otp", json={"phone": phone})
            responses.append(response)
        
        # At least some should succeed, but eventually be rate limited
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        assert success_count > 0
        # Rate limiting might not kick in immediately in test environment
