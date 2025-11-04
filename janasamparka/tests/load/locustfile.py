"""
Load testing configuration for Janasamparka API
"""
from locust import HttpUser, task, between
import random
import json


class JanasamparkaUser(HttpUser):
    """Simulate different user types using the Janasamparka system"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Generate test phone number
        self.phone = f"+9198{random.randint(10000000, 99999999)}"
        self.name = f"Load Test User {random.randint(1, 10000)}"
        self.email = f"loadtest{random.randint(1, 10000)}@test.com"
        
        # Request OTP
        self.client.post("/api/auth/request-otp", json={"phone": self.phone})
        
        # Verify OTP and get token
        response = self.client.post("/api/auth/verify-otp", json={
            "phone": self.phone,
            "otp": "123456"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            
            # Update profile
            self.client.patch("/api/auth/profile", json={
                "name": self.name,
                "email": self.email,
                "role": "citizen"
            }, headers=self.headers)
        else:
            self.token = None
            self.headers = {}

    @task(3)
    def view_complaints_list(self):
        """View complaints list - most common operation"""
        if self.token:
            self.client.get("/api/complaints/", headers=self.headers)

    @task(2)
    def view_complaint_details(self):
        """View specific complaint details"""
        if self.token:
            # First get list to find a complaint ID
            response = self.client.get("/api/complaints/", headers=self.headers)
            if response.status_code == 200:
                complaints = response.json().get("items", [])
                if complaints:
                    complaint_id = complaints[0]["id"]
                    self.client.get(f"/api/complaints/{complaint_id}", headers=self.headers)

    @task(1)
    def create_complaint(self):
        """Create a new complaint"""
        if self.token:
            categories = ["road", "water", "electricity", "street_light", "garbage"]
            complaint_data = {
                "title": f"Load Test Complaint {random.randint(1, 10000)}",
                "description": f"This is a load test complaint created at {random.randint(1, 10000)}",
                "category": random.choice(categories),
                "lat": str(random.uniform(12.8, 13.2)),
                "lng": str(random.uniform(77.4, 77.8)),
                "location_description": f"Load test location {random.randint(1, 100)}",
                "constituency_id": "12345678-1234-1234-1234-123456789012"  # Test constituency ID
            }
            self.client.post("/api/complaints/", json=complaint_data, headers=self.headers)

    @task(1)
    def view_departments(self):
        """View departments list"""
        if self.token:
            self.client.get("/api/departments/", headers=self.headers)

    @task(1)
    def view_analytics(self):
        """View analytics dashboard"""
        if self.token:
            self.client.get("/api/analytics/overview", headers=self.headers)

    @task(1)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")

    @task(1)
    def get_current_user(self):
        """Get current user profile"""
        if self.token:
            self.client.get("/api/auth/me", headers=self.headers)


class AdminUser(HttpUser):
    """Simulate admin user for admin operations"""
    
    wait_time = between(2, 5)
    weight = 1  # Fewer admin users than regular users
    
    def on_start(self):
        """Admin login"""
        admin_phone = "+919876543210"
        
        # Request OTP
        self.client.post("/api/auth/request-otp", json={"phone": admin_phone})
        
        # Verify OTP
        response = self.client.post("/api/auth/verify-otp", json={
            "phone": admin_phone,
            "otp": "123456"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def admin_view_all_complaints(self):
        """Admin views all complaints"""
        if self.token:
            self.client.get("/api/complaints/", headers=self.headers)

    @task(2)
    def admin_view_users(self):
        """Admin views users list"""
        if self.token:
            self.client.get("/api/users/", headers=self.headers)

    @task(2)
    def admin_view_analytics(self):
        """Admin views analytics"""
        if self.token:
            self.client.get("/api/analytics/overview", headers=self.headers)
            self.client.get("/api/complaints/stats/summary", headers=self.headers)

    @task(1)
    def admin_view_constituencies(self):
        """Admin views constituencies"""
        if self.token:
            self.client.get("/api/constituencies/", headers=self.headers)

    @task(1)
    def admin_update_complaint_status(self):
        """Admin updates complaint status"""
        if self.token:
            # Get a complaint
            response = self.client.get("/api/complaints/", headers=self.headers)
            if response.status_code == 200:
                complaints = response.json().get("items", [])
                if complaints:
                    complaint_id = complaints[0]["id"]
                    # Update status
                    self.client.patch(f"/api/complaints/{complaint_id}/status", 
                                    json={
                                        "status": "assigned",
                                        "note": "Load test status update"
                                    }, 
                                    headers=self.headers)


class AnonymousUser(HttpUser):
    """Simulate anonymous user (no authentication)"""
    
    wait_time = between(1, 2)
    weight = 2  # Some anonymous traffic

    @task(3)
    def view_health_check(self):
        """Health check - accessible without auth"""
        self.client.get("/health")

    @task(2)
    def view_root_endpoint(self):
        """Root endpoint"""
        self.client.get("/")

    @task(1)
    def attempt_unauthorized_access(self):
        """Attempt unauthorized access (should fail)"""
        self.client.get("/api/complaints/", catch_response=True) \
            .catch_response()

    @task(1)
    def request_otp(self):
        """Request OTP - accessible without auth"""
        phone = f"+9198{random.randint(10000000, 99999999)}"
        self.client.post("/api/auth/request-otp", json={"phone": phone})
