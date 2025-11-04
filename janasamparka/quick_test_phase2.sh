#!/bin/bash

# Quick Test Script for Phase 2 Features
# This script helps you quickly test all Phase 2 features

echo "🧪 PHASE 2 - QUICK TEST SCRIPT"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "admin-dashboard" ] || [ ! -d "backend" ]; then
    echo "${RED}Error: Please run this script from the janasamparka root directory${NC}"
    exit 1
fi

echo "${YELLOW}Step 1: Installing Frontend Dependencies${NC}"
echo "=========================================="
cd admin-dashboard
npm install leaflet react-leaflet leaflet.heat leaflet.markercluster
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo "${RED}❌ Frontend installation failed${NC}"
    exit 1
fi
echo ""

echo "${YELLOW}Step 2: Installing Backend Dependencies${NC}"
echo "=========================================="
cd ../backend
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
pip install shapely geopy faiss-cpu -q
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo "${RED}❌ Backend installation failed${NC}"
    exit 1
fi
echo ""

echo "${YELLOW}Step 3: Running Database Migrations${NC}"
echo "=========================================="
echo "Running approval fields migration..."
psql -U postgres -d janasamparka -f migrations/add_approval_fields.sql > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Approval fields migration complete${NC}"
else
    echo "${YELLOW}⚠️  Approval migration may have already run${NC}"
fi

echo "Running PostGIS setup migration..."
psql -U postgres -d janasamparka -f migrations/setup_postgis.sql > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ PostGIS migration complete${NC}"
else
    echo "${YELLOW}⚠️  PostGIS migration may have already run${NC}"
fi
echo ""

echo "${YELLOW}Step 4: Starting Services${NC}"
echo "=========================================="
echo ""
echo "${GREEN}Ready to start testing!${NC}"
echo ""
echo "Open 3 terminals and run:"
echo ""
echo "Terminal 1 (Backend):"
echo "${YELLOW}cd backend && source .venv/bin/activate && uvicorn app.main:app --reload${NC}"
echo ""
echo "Terminal 2 (Frontend):"
echo "${YELLOW}cd admin-dashboard && npm run dev${NC}"
echo ""
echo "Terminal 3 (This terminal):"
echo "${YELLOW}Follow the testing guide in PHASE2_TESTING_GUIDE.md${NC}"
echo ""
echo "Quick links:"
echo "- Frontend: ${GREEN}http://localhost:3000${NC}"
echo "- Map View: ${GREEN}http://localhost:3000/map${NC}"
echo "- API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "Login credentials:"
echo "- Phone: ${GREEN}+918242226666${NC}"
echo "- OTP: ${GREEN}123456${NC}"
echo ""
echo "${GREEN}✅ Setup complete! Ready for testing.${NC}"
echo ""
echo "📋 Test checklist:"
echo "  [ ] Phase 2.1: Before/After photos (6 tests)"
echo "  [ ] Phase 2.2: Interactive map (5 tests)"
echo "  [ ] Phase 2.4: Heatmap & clustering (4 tests)"
echo "  [ ] Phase 2.3: Backend APIs (4 tests)"
echo "  [ ] Phase 2.5: AI features (3 tests)"
echo "  [ ] Phase 2.6: Bhoomi API (2 tests)"
echo "  [ ] Integration tests (3 tests)"
echo ""
echo "See PHASE2_TESTING_GUIDE.md for detailed instructions."
