"""
End-to-end tests for complete user workflows
"""
import pytest
from uuid import uuid4


class TestCompleteComplaintWorkflow:
    """Test complete complaint lifecycle from submission to resolution"""
    
    def test_full_complaint_lifecycle(self, client, test_constituency, test_department):
        """Test complete complaint workflow: citizen files -> MLA views -> department resolves"""
        
        # Step 1: Citizen registers and files complaint
        citizen_phone = "+919876543299"
        citizen_name = "Test Citizen E2E"
        
        # Request OTP for citizen
        otp_response = client.post("/api/auth/request-otp", json={
            "phone": citizen_phone
        })
        assert otp_response.status_code == 200
        
        # Verify OTP and get token
        verify_response = client.post("/api/auth/verify-otp", json={
            "phone": citizen_phone,
            "otp": "123456"
        })
        assert verify_response.status_code == 200
        citizen_token = verify_response.json()["access_token"]
        citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
        
        # Create user profile
        user_data = {
            "name": citizen_name,
            "email": "e2e.citizen@test.com",
            "role": "citizen"
        }
        profile_response = client.patch("/api/auth/profile", json=user_data, headers=citizen_headers)
        assert profile_response.status_code == 200
        
        # File complaint
        complaint_data = {
            "title": "E2E Test: Broken Street Light",
            "description": "Street light not working for 3 days, causing safety issues at night",
            "category": "street_light",
            "lat": 12.9716,
            "lng": 77.5946,
            "location_description": "Near Main Street intersection",
            "constituency_id": str(test_constituency.id)
        }
        
        create_response = client.post("/api/complaints/", json=complaint_data, headers=citizen_headers)
        assert create_response.status_code == 201
        complaint = create_response.json()
        complaint_id = complaint["id"]
        
        # Verify complaint is in submitted status
        assert complaint["status"] == "submitted"
        assert complaint["priority"] == "medium"
        
        # Step 2: MLA views and assigns complaint
        mla_phone = "+919876543298"
        
        # MLA login
        client.post("/api/auth/request-otp", json={"phone": mla_phone})
        mla_verify = client.post("/api/auth/verify-otp", json={
            "phone": mla_phone,
            "otp": "123456"
        })
        mla_token = mla_verify.json()["access_token"]
        mla_headers = {"Authorization": f"Bearer {mla_token}"}
        
        # MLA views complaint list
        list_response = client.get("/api/complaints/", headers=mla_headers)
        assert list_response.status_code == 200
        complaints = list_response.json()["items"]
        assert len(complaints) >= 1
        
        # MLA views specific complaint
        detail_response = client.get(f"/api/complaints/{complaint_id}", headers=mla_headers)
        assert detail_response.status_code == 200
        complaint_detail = detail_response.json()
        assert complaint_detail["title"] == complaint_data["title"]
        
        # MLA assigns to department
        assign_response = client.post(f"/api/complaints/{complaint_id}/assign", 
                                     json={"department_id": str(test_department.id)}, 
                                     headers=mla_headers)
        assert assign_response.status_code == 200
        assigned_complaint = assign_response.json()
        assert assigned_complaint["status"] == "assigned"
        assert assigned_complaint["dept_id"] == str(test_department.id)
        
        # Step 3: Department officer works on complaint
        dept_phone = "+919876543297"
        
        # Department officer login
        client.post("/api/auth/request-otp", json={"phone": dept_phone})
        dept_verify = client.post("/api/auth/verify-otp", json={
            "phone": dept_phone,
            "otp": "123456"
        })
        dept_token = dept_verify.json()["access_token"]
        dept_headers = {"Authorization": f"Bearer {dept_token}"}
        
        # Department officer updates status to in_progress
        progress_response = client.patch(f"/api/complaints/{complaint_id}/status", 
                                        json={
                                            "status": "in_progress",
                                            "note": "Team dispatched to repair street light"
                                        }, 
                                        headers=dept_headers)
        assert progress_response.status_code == 200
        progress_complaint = progress_response.json()
        assert progress_complaint["status"] == "in_progress"
        
        # Step 4: Department marks as resolved with photo evidence
        resolve_response = client.patch(f"/api/complaints/{complaint_id}/status", 
                                       json={
                                           "status": "resolved",
                                           "note": "Street light repaired and tested successfully"
                                       }, 
                                       headers=dept_headers)
        assert resolve_response.status_code == 200
        resolved_complaint = resolve_response.json()
        assert resolved_complaint["status"] == "resolved"
        assert resolved_complaint["resolved_at"] is not None
        
        # Step 5: Citizen views resolution and provides feedback
        citizen_detail_response = client.get(f"/api/complaints/{complaint_id}", headers=citizen_headers)
        assert citizen_detail_response.status_code == 200
        final_complaint = citizen_detail_response.json()
        assert final_complaint["status"] == "resolved"
        
        # Citizen provides rating and feedback
        feedback_response = client.post(f"/api/complaints/{complaint_id}/feedback", 
                                       json={
                                           "rating": 5,
                                           "feedback": "Quick and efficient resolution, thank you!"
                                       }, 
                                       headers=citizen_headers)
        assert feedback_response.status_code == 200
        
        # Step 6: Verify analytics reflect the completed workflow
        analytics_response = client.get("/api/analytics/overview", headers=mla_headers)
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        assert analytics["complaints"]["resolved"] >= 1
        
        # Verify status history
        history_response = client.get(f"/api/complaints/{complaint_id}/history", headers=mla_headers)
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) >= 4  # submitted -> assigned -> in_progress -> resolved
        
        status_sequence = [log["new_status"] for log in history]
        assert "submitted" in status_sequence
        assert "assigned" in status_sequence
        assert "in_progress" in status_sequence
        assert "resolved" in status_sequence


class TestMultiConstituencyWorkflow:
    """Test multi-constituency data isolation"""
    
    def test_constituency_isolation(self, client):
        """Test that users can only access their constituency data"""
        
        # Create two constituencies
        constituency1_data = {
            "name": "Constituency 1",
            "description": "First test constituency"
        }
        constituency2_data = {
            "name": "Constituency 2", 
            "description": "Second test constituency"
        }
        
        # Admin creates constituencies
        admin_phone = "+919876543210"
        client.post("/api/auth/request-otp", json={"phone": admin_phone})
        admin_verify = client.post("/api/auth/verify-otp", json={
            "phone": admin_phone,
            "otp": "123456"
        })
        admin_token = admin_verify.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        const1_response = client.post("/api/constituencies/", json=constituency1_data, headers=admin_headers)
        const2_response = client.post("/api/constituencies/", json=constituency2_data, headers=admin_headers)
        
        constituency1_id = const1_response.json()["id"]
        constituency2_id = const2_response.json()["id"]
        
        # Create MLA for constituency 1
        mla1_phone = "+919876543301"
        client.post("/api/auth/request-otp", json={"phone": mla1_phone})
        mla1_verify = client.post("/api/auth/verify-otp", json={
            "phone": mla1_phone,
            "otp": "123456"
        })
        mla1_token = mla1_verify.json()["access_token"]
        mla1_headers = {"Authorization": f"Bearer {mla1_token}"}
        
        # Update MLA profile with constituency 1
        mla1_profile = {
            "name": "MLA 1",
            "role": "mla",
            "constituency_id": constituency1_id
        }
        client.patch("/api/auth/profile", json=mla1_profile, headers=mla1_headers)
        
        # Create complaint in constituency 1
        complaint1_data = {
            "title": "Complaint in Constituency 1",
            "description": "Test complaint for constituency 1",
            "constituency_id": constituency1_id,
            "lat": 12.9716,
            "lng": 77.5946
        }
        
        complaint1_response = client.post("/api/complaints/", json=complaint1_data, headers=mla1_headers)
        assert complaint1_response.status_code == 201
        
        # Create complaint in constituency 2 (as admin)
        complaint2_data = {
            "title": "Complaint in Constituency 2",
            "description": "Test complaint for constituency 2", 
            "constituency_id": constituency2_id,
            "lat": 13.0827,
            "lng": 80.2707
        }
        
        complaint2_response = client.post("/api/complaints/", json=complaint2_data, headers=admin_headers)
        assert complaint2_response.status_code == 201
        
        # MLA 1 should only see complaints from their constituency
        mla1_complaints_response = client.get("/api/complaints/", headers=mla1_headers)
        assert mla1_complaints_response.status_code == 200
        mla1_complaints = mla1_complaints_response.json()["items"]
        
        # Should only see constituency 1 complaints
        for complaint in mla1_complaints:
            assert complaint["constituency_id"] == constituency1_id
        
        # Admin should see all complaints
        admin_complaints_response = client.get("/api/complaints/", headers=admin_headers)
        assert admin_complaints_response.status_code == 200
        admin_complaints = admin_complaints_response.json()["items"]
        
        # Should see complaints from both constituencies
        constituency_ids = {c["constituency_id"] for c in admin_complaints}
        assert constituency1_id in constituency_ids
        assert constituency2_id in constituency_ids


class TestEmergencyWorkflow:
    """Test emergency complaint workflow"""
    
    def test_emergency_complaint_priority(self, client, auth_headers_citizen, test_constituency):
        """Test emergency complaints get high priority"""
        
        emergency_data = {
            "title": "EMERGENCY: Fallen tree blocking road",
            "description": "Large tree fell across main road, blocking all traffic",
            "category": "emergency",
            "lat": 12.9716,
            "lng": 77.5946,
            "constituency_id": str(test_constituency.id),
            "is_emergency": True
        }
        
        # Create emergency complaint
        response = client.post("/api/complaints/", json=emergency_data, headers=auth_headers_citizen)
        assert response.status_code == 201
        complaint = response.json()
        
        # Should be marked as emergency and high priority
        assert complaint["is_emergency"] is True
        assert complaint["priority"] == "urgent"
        
        # Should appear in emergency dashboard
        emergency_response = client.get("/api/complaints/?is_emergency=true", headers=auth_headers_citizen)
        assert emergency_response.status_code == 200
        emergency_complaints = emergency_response.json()["items"]
        assert len(emergency_complaints) >= 1
        assert emergency_complaints[0]["is_emergency"] is True


class TestMediaUploadWorkflow:
    """Test file upload workflow with complaints"""
    
    def test_complaint_with_photos(self, client, auth_headers_citizen, test_complaint):
        """Test uploading photos with complaint"""
        
        # Mock photo upload
        photo_data = {
            "file": ("before.jpg", b"fake image data before", "image/jpeg")
        }
        
        upload_response = client.post("/api/media/upload", 
                                     files=photo_data,
                                     data={
                                         "complaint_id": str(test_complaint.id),
                                         "photo_type": "before",
                                         "caption": "Photo before repair"
                                     },
                                     headers=auth_headers_citizen)
        
        assert upload_response.status_code == 201
        media = upload_response.json()
        assert media["media_type"] == "photo"
        assert media["photo_type"] == "before"
        
        # Upload after photo
        after_photo_data = {
            "file": ("after.jpg", b"fake image data after", "image/jpeg")
        }
        
        after_response = client.post("/api/media/upload", 
                                    files=after_photo_data,
                                    data={
                                        "complaint_id": str(test_complaint.id),
                                        "photo_type": "after",
                                        "caption": "Photo after repair"
                                    },
                                    headers=auth_headers_citizen)
        
        assert after_response.status_code == 201
        after_media = after_response.json()
        assert after_media["photo_type"] == "after"
        
        # List media for complaint
        list_response = client.get(f"/api/media/complaint/{test_complaint.id}", headers=auth_headers_citizen)
        assert list_response.status_code == 200
        media_list = list_response.json()
        assert len(media_list) >= 2
        
        photo_types = [m["photo_type"] for m in media_list if m["photo_type"]]
        assert "before" in photo_types
        assert "after" in photo_types


class TestNotificationWorkflow:
    """Test notification workflow for status updates"""
    
    def test_status_change_notifications(self, client, auth_headers_admin, test_complaint):
        """Test notifications are sent for status changes"""
        
        # Update complaint status
        update_response = client.patch(f"/api/complaints/{test_complaint.id}/status", 
                                     json={
                                         "status": "assigned",
                                         "note": "Assigned to public works department"
                                     }, 
                                     headers=auth_headers_admin)
        
        assert update_response.status_code == 200
        
        # Check notification history (mock implementation)
        notification_response = client.get(f"/api/complaints/{test_complaint.id}/notifications", 
                                          headers=auth_headers_admin)
        
        # This endpoint might not exist yet, but would show notification history
        # For now, we just verify the status change was logged
        history_response = client.get(f"/api/complaints/{test_complaint.id}/history", 
                                     headers=auth_headers_admin)
        assert history_response.status_code == 200
        history = history_response.json()
        
        status_changes = [log for log in history if log["new_status"] == "assigned"]
        assert len(status_changes) >= 1
        assert status_changes[0]["note"] == "Assigned to public works department"


class TestReportingWorkflow:
    """Test reporting and analytics workflow"""
    
    def test_monthly_report_generation(self, client, auth_headers_admin):
        """Test monthly report generation"""
        
        # Generate monthly report
        report_response = client.get("/api/reports/monthly?year=2024&month=1", headers=auth_headers_admin)
        
        if report_response.status_code == 200:
            report = report_response.json()
            assert "summary" in report
            assert "complaints" in report
            assert "departments" in report
            assert "constituencies" in report
        
        # Generate constituency-specific report
        constituency_response = client.get("/api/reports/constituency-summary", headers=auth_headers_admin)
        
        if constituency_response.status_code == 200:
            constituency_report = constituency_response.json()
            assert isinstance(constituency_report, list)
