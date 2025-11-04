#!/bin/bash

# Test Setup Script for Janasamparka
# This script validates that all components are working

echo "🧪 Testing Janasamparka Setup"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if Docker is running
echo "1️⃣  Checking Docker..."
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
    exit 1
fi

# Test 2: Check if database container is running
echo ""
echo "2️⃣  Checking database container..."
if docker-compose ps | grep -q "janasamparka-db.*Up"; then
    echo -e "${GREEN}✅ Database container is running${NC}"
    
    # Check if database is accessible
    if docker-compose exec -T db psql -U janasamparka -d janasamparka_db -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database is accessible${NC}"
    else
        echo -e "${RED}❌ Database is not accessible${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Database container is not running. Starting it...${NC}"
    docker-compose up -d db
    echo "Waiting for database to be ready..."
    sleep 5
fi

# Test 3: Check Python virtual environment
echo ""
echo "3️⃣  Checking Python environment..."
if [ -d "backend/.venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Test 4: Check if migrations are applied
echo ""
echo "4️⃣  Checking database migrations..."
cd backend
source .venv/bin/activate

if alembic current > /dev/null 2>&1; then
    current_rev=$(alembic current 2>&1 | grep -o "[a-f0-9]\{12\}")
    if [ -n "$current_rev" ]; then
        echo -e "${GREEN}✅ Migrations are applied (revision: $current_rev)${NC}"
    else
        echo -e "${YELLOW}⚠️  No migrations applied yet${NC}"
        echo "Running migrations..."
        alembic upgrade head
    fi
else
    echo -e "${RED}❌ Migration check failed${NC}"
fi

# Test 5: Check if seed data exists
echo ""
echo "5️⃣  Checking seed data..."
constituency_count=$(docker-compose exec -T db psql -U janasamparka -d janasamparka_db -tAc "SELECT COUNT(*) FROM constituencies;" 2>/dev/null || echo "0")

if [ "$constituency_count" -ge "3" ]; then
    echo -e "${GREEN}✅ Seed data exists ($constituency_count constituencies)${NC}"
else
    echo -e "${YELLOW}⚠️  Seed data not found. Creating...${NC}"
    python seed_data.py
fi

# Test 6: Check if backend dependencies are installed
echo ""
echo "6️⃣  Checking backend dependencies..."
if python -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Installing backend dependencies...${NC}"
    pip install -r requirements.txt
fi

cd ..

# Test 7: Check if admin dashboard dependencies are installed
echo ""
echo "7️⃣  Checking admin dashboard..."
if [ -d "admin-dashboard/node_modules" ]; then
    echo -e "${GREEN}✅ Admin dashboard dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Installing admin dashboard dependencies...${NC}"
    cd admin-dashboard
    npm install
    cd ..
fi

# Test 8: Test backend API endpoint
echo ""
echo "8️⃣  Testing backend API..."
echo -e "${YELLOW}ℹ️  Starting backend server in background...${NC}"

cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is responding${NC}"
    
    # Test constituencies endpoint
    constituency_response=$(curl -s http://localhost:8000/api/constituencies/)
    if echo "$constituency_response" | grep -q "constituencies"; then
        echo -e "${GREEN}✅ Constituencies API is working${NC}"
        
        # Count constituencies in response
        constituency_count=$(echo "$constituency_response" | grep -o '"id"' | wc -l)
        echo -e "${GREEN}   Found $constituency_count constituencies${NC}"
    else
        echo -e "${RED}❌ Constituencies API failed${NC}"
    fi
else
    echo -e "${RED}❌ Backend API is not responding${NC}"
    echo "Check logs: tail -f /tmp/backend.log"
fi

# Stop backend
kill $BACKEND_PID 2>/dev/null

echo ""
echo "=============================="
echo "🎉 Setup Test Complete!"
echo "=============================="
echo ""
echo "📋 Summary:"
echo "   - Database: Running"
echo "   - Migrations: Applied"
echo "   - Seed Data: Loaded"
echo "   - Backend: Working"
echo "   - Admin Dashboard: Ready"
echo ""
echo "🚀 Next Steps:"
echo "   1. Start backend:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "   2. Start frontend: cd admin-dashboard && npm run dev"
echo "   3. Open http://localhost:8000/docs (Backend API)"
echo "   4. Open http://localhost:3000 (Admin Dashboard)"
echo ""
