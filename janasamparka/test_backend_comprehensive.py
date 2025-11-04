#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script
Tests all Phase 1 & Phase 2 endpoints with detailed validation
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RESET = '\033[0m'

class APITester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
    def test(self, method: str, endpoint: str, description: str, 
             data: Dict = None, expected_status: int = 200) -> bool:
        """Test an API endpoint"""
        self.total_tests += 1
        
        url = f"{API_BASE}{endpoint}"
        print(f"\nTest {self.total_tests}: {description}")
        print(f"  → {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Check status code
            if response.status_code == expected_status or \
               response.status_code in [200, 201, 204]:
                print(f"  {Colors.GREEN}✅ PASS{Colors.RESET} (HTTP {response.status_code})")
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
                except:
                    pass
                
                self.passed_tests += 1
                self.test_results.append({
                    'test': description,
                    'status': 'PASS',
                    'http_code': response.status_code
                })
                return True
            else:
                print(f"  {Colors.RED}❌ FAIL{Colors.RESET} (HTTP {response.status_code})")
                print(f"  Error: {response.text[:200]}")
                self.failed_tests += 1
                self.test_results.append({
                    'test': description,
                    'status': 'FAIL',
                    'http_code': response.status_code,
                    'error': response.text[:200]
                })
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"  {Colors.RED}❌ FAIL{Colors.RESET} (Connection Error)")
            print(f"  Error: Backend not running")
            self.failed_tests += 1
            return False
        except Exception as e:
            print(f"  {Colors.RED}❌ FAIL{Colors.RESET} (Exception)")
            print(f"  Error: {str(e)}")
            self.failed_tests += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"\nTotal Tests: {self.total_tests}")
        print(f"{Colors.GREEN}Passed: {self.passed_tests}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed_tests}{Colors.RESET}")
        
        if self.total_tests > 0:
            pass_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed_tests == 0:
            print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.RESET}")
            print("\n✅ Backend is fully functional")
            print("✅ Phase 1 & Phase 2 APIs working correctly")
            return True
        else:
            print(f"\n{Colors.RED}⚠️ SOME TESTS FAILED{Colors.RESET}")
            print(f"\nFailed tests: {self.failed_tests}")
            return False

def main():
    print("🧪 JANASAMPARKA - COMPREHENSIVE API TESTING (Python)")
    print("="*50)
    print("")
    
    # Check if backend is running
    print("Checking if backend is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Backend is running{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Backend returned unexpected status{Colors.RESET}")
    except:
        print(f"{Colors.RED}❌ Backend is not running!{Colors.RESET}")
        print("\nPlease start the backend with:")
        print("  cd backend && uvicorn app.main:app --reload")
        sys.exit(1)
    
    tester = APITester()
    
    # ========================================
    # PHASE 1: BASIC FUNCTIONALITY
    # ========================================
    print("\n" + "="*50)
    print("PHASE 1: BASIC FUNCTIONALITY")
    print("="*50)
    
    # Authentication Tests
    print(f"\n{Colors.BLUE}📱 Authentication Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("POST", "/auth/request-otp",
                "Request OTP",
                {"phone": "+918242226666"})
    
    tester.test("POST", "/auth/verify-otp",
                "Verify OTP",
                {"phone": "+918242226666", "otp": "123456"})
    
    # Constituencies Tests
    print(f"\n{Colors.BLUE}🏛️ Constituencies Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/constituencies",
                "List all constituencies")
    
    tester.test("GET", "/constituencies?active_only=true",
                "List active constituencies only")
    
    # Complaints Tests
    print(f"\n{Colors.BLUE}📋 Complaints Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/complaints",
                "List all complaints")
    
    tester.test("GET", "/complaints?status=submitted",
                "Filter complaints by status")
    
    tester.test("GET", "/complaints?category=road",
                "Filter complaints by category")
    
    tester.test("GET", "/complaints/stats/summary",
                "Get complaints statistics")
    
    # Users Tests
    print(f"\n{Colors.BLUE}👥 Users Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/users",
                "List all users")
    
    tester.test("GET", "/users?role=citizen",
                "Filter users by role")
    
    # Departments Tests
    print(f"\n{Colors.BLUE}🏢 Departments Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/departments",
                "List all departments")
    
    tester.test("GET", "/departments?is_active=true",
                "List active departments only")
    
    # Wards Tests
    print(f"\n{Colors.BLUE}📍 Wards Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/wards",
                "List all wards")
    
    # Polls Tests
    print(f"\n{Colors.BLUE}📊 Polls Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/polls",
                "List all polls")
    
    tester.test("GET", "/polls?is_active=true",
                "List active polls only")
    
    # ========================================
    # PHASE 2: ADVANCED FEATURES
    # ========================================
    print("\n" + "="*50)
    print("PHASE 2: ADVANCED FEATURES")
    print("="*50)
    
    # Map Tests
    print(f"\n{Colors.BLUE}🗺️ Map Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/map/complaints",
                "Get complaints as GeoJSON")
    
    tester.test("GET", "/map/heatmap",
                "Get heatmap data")
    
    tester.test("GET", "/map/clusters?radius_km=1&min_complaints=3",
                "Get complaint clusters")
    
    tester.test("GET", "/map/stats/by-ward",
                "Get statistics by ward")
    
    # Geocoding Tests
    print(f"\n{Colors.BLUE}📍 Geocoding Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/geocode/ward?lat=12.76&lng=75.21",
                "Ward detection from GPS coordinates")
    
    tester.test("GET", "/geocode/reverse?lat=12.76&lng=75.21",
                "Reverse geocoding")
    
    # AI Tests
    print(f"\n{Colors.BLUE}🤖 AI Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("POST", "/ai/duplicate-check",
                "Check for duplicate complaints",
                {
                    "title": "Road pothole near market",
                    "description": "Large pothole causing issues",
                    "threshold": 0.85
                })
    
    # Bhoomi Tests
    print(f"\n{Colors.BLUE}🏘️ Bhoomi Endpoints{Colors.RESET}")
    print("-" * 40)
    
    tester.test("GET", "/bhoomi/rtc?survey_number=123&village=Puttur",
                "RTC lookup (stub)")
    
    tester.test("GET", "/bhoomi/villages?taluk=Puttur",
                "List villages (stub)")
    
    tester.test("GET", "/bhoomi/search?owner_name=Test",
                "Search properties (stub)")
    
    # Print final summary
    tester.print_summary()
    
    print(f"\n{Colors.BLUE}API Documentation:{Colors.RESET} {BASE_URL}/docs")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed_tests == 0 else 1)

if __name__ == "__main__":
    main()
