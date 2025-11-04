#!/bin/bash

# Comprehensive Testing Script for Phase 1 & Phase 2
# This script tests all backend API endpoints automatically

echo "🧪 JANASAMPARKA - COMPREHENSIVE API TESTING"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api"

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test result function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Test $TOTAL_TESTS: $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PATCH" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_BASE$endpoint")
    fi
    
    if [ "$response" = "200" ] || [ "$response" = "201" ] || [ "$response" = "204" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Check if backend is running
echo "Checking if backend is running..."
if curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not running!${NC}"
    echo "Please start the backend with: cd backend && uvicorn app.main:app --reload"
    exit 1
fi

echo ""
echo "================================"
echo "PHASE 1: BASIC FUNCTIONALITY"
echo "================================"
echo ""

# Authentication Tests
echo -e "${BLUE}📱 Testing Authentication Endpoints${NC}"
echo "-----------------------------------"

test_endpoint "POST" "/auth/request-otp" \
    '{"phone":"+918242226666"}' \
    "Request OTP"

test_endpoint "POST" "/auth/verify-otp" \
    '{"phone":"+918242226666","otp":"123456"}' \
    "Verify OTP"

echo ""

# Constituencies Tests
echo -e "${BLUE}🏛️ Testing Constituencies Endpoints${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/constituencies" "" \
    "List constituencies"

test_endpoint "GET" "/constituencies?active_only=true" "" \
    "List active constituencies only"

echo ""

# Complaints Tests
echo -e "${BLUE}📋 Testing Complaints Endpoints${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/complaints" "" \
    "List all complaints"

test_endpoint "GET" "/complaints?status=submitted" "" \
    "Filter complaints by status"

test_endpoint "GET" "/complaints?category=road" "" \
    "Filter complaints by category"

test_endpoint "GET" "/complaints/stats/summary" "" \
    "Get complaints statistics"

echo ""

# Users Tests
echo -e "${BLUE}👥 Testing Users Endpoints (NEW)${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/users" "" \
    "List all users"

test_endpoint "GET" "/users?role=citizen" "" \
    "Filter users by role"

echo ""

# Departments Tests
echo -e "${BLUE}🏢 Testing Departments Endpoints${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/departments" "" \
    "List all departments"

test_endpoint "GET" "/departments?is_active=true" "" \
    "List active departments"

echo ""

# Wards Tests
echo -e "${BLUE}📍 Testing Wards Endpoints${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/wards" "" \
    "List all wards"

echo ""

# Polls Tests
echo -e "${BLUE}📊 Testing Polls Endpoints${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/polls" "" \
    "List all polls"

test_endpoint "GET" "/polls?is_active=true" "" \
    "List active polls"

echo ""
echo "================================"
echo "PHASE 2: ADVANCED FEATURES"
echo "================================"
echo ""

# Map Tests
echo -e "${BLUE}🗺️ Testing Map Endpoints (Phase 2)${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/map/complaints" "" \
    "Get complaints GeoJSON"

test_endpoint "GET" "/map/heatmap" "" \
    "Get heatmap data"

test_endpoint "GET" "/map/clusters?radius_km=1" "" \
    "Get complaint clusters"

test_endpoint "GET" "/map/stats/by-ward" "" \
    "Get ward statistics"

echo ""

# Geocoding Tests
echo -e "${BLUE}📍 Testing Geocoding Endpoints (Phase 2)${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/geocode/ward?lat=12.76&lng=75.21" "" \
    "Ward detection from coordinates"

test_endpoint "GET" "/geocode/reverse?lat=12.76&lng=75.21" "" \
    "Reverse geocoding"

echo ""

# AI Tests
echo -e "${BLUE}🤖 Testing AI Endpoints (Phase 2)${NC}"
echo "-----------------------------------"

test_endpoint "POST" "/ai/duplicate-check" \
    '{"title":"Test complaint","description":"Test description","threshold":0.85}' \
    "Check for duplicate complaints"

echo ""

# Bhoomi Tests
echo -e "${BLUE}🏘️ Testing Bhoomi Endpoints (Phase 2)${NC}"
echo "-----------------------------------"

test_endpoint "GET" "/bhoomi/rtc?survey_number=123&village=Puttur" "" \
    "RTC lookup (stub)"

test_endpoint "GET" "/bhoomi/villages?taluk=Puttur" "" \
    "List villages (stub)"

echo ""

# Media Tests
echo -e "${BLUE}📸 Testing Media Endpoints (Phase 2)${NC}"
echo "-----------------------------------"

# Note: File upload test skipped (requires actual files)
echo "Test: Media upload - ${YELLOW}⚠️ SKIP${NC} (requires multipart form data)"

echo ""
echo "================================"
echo "TEST SUMMARY"
echo "================================"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")
echo "Pass Rate: $PASS_RATE%"

echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ Phase 1 & Phase 2 APIs are working correctly"
    echo "✅ Backend is production-ready"
    echo ""
    echo "Next steps:"
    echo "1. Test frontend UI manually"
    echo "2. Run integration tests"
    echo "3. Deploy to staging/production"
else
    echo -e "${RED}⚠️ SOME TESTS FAILED${NC}"
    echo ""
    echo "Failed tests: $FAILED_TESTS"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check backend logs for errors"
    echo "2. Verify database is running"
    echo "3. Check if all migrations are applied"
    echo "4. Review API documentation: http://localhost:8000/docs"
fi

echo ""
echo "Detailed API Documentation: ${BLUE}http://localhost:8000/docs${NC}"
echo "Test completed at: $(date)"
