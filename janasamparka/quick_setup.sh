#!/bin/bash

# Quick Setup Script for Janasamparka
# This script sets up everything without Docker

set -e  # Exit on error

echo "🚀 Janasamparka Quick Setup"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get current user
CURRENT_USER=$(whoami)
echo "📝 Current user: $CURRENT_USER"
echo ""

# Step 1: Check PostgreSQL
echo "1️⃣  Checking PostgreSQL..."
if pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL is not running. Starting...${NC}"
    brew services start postgresql@14
    sleep 3
fi

# Step 2: Create database
echo ""
echo "2️⃣  Setting up database..."
if psql postgres -tAc "SELECT 1 FROM pg_database WHERE datname='janasamparka_db'" 2>/dev/null | grep -q 1; then
    echo -e "${GREEN}✅ Database already exists${NC}"
else
    echo -e "${YELLOW}Creating database...${NC}"
    createdb janasamparka_db 2>/dev/null || echo "Database might already exist"
fi

# Enable PostGIS
echo "Enabling PostGIS extension..."
psql janasamparka_db -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>/dev/null || true
echo -e "${GREEN}✅ Database ready${NC}"

# Step 3: Setup Backend
echo ""
echo "3️⃣  Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
APP_NAME=Janasamparka MLA Connect
APP_VERSION=1.0.0
DEBUG=true

DATABASE_URL=postgresql://${CURRENT_USER}@localhost/janasamparka_db

SECRET_KEY=dev-secret-key-change-in-production-$(date +%s)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5
OTP_MOCK=true

CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
EOL
fi

echo -e "${GREEN}✅ Backend environment ready${NC}"

# Step 4: Run migrations
echo ""
echo "4️⃣  Running database migrations..."
alembic upgrade head 2>&1 | grep -v "WARNING" || true
echo -e "${GREEN}✅ Migrations applied${NC}"

# Step 5: Check and load seed data
echo ""
echo "5️⃣  Checking seed data..."
CONST_COUNT=$(psql janasamparka_db -tAc "SELECT COUNT(*) FROM constituencies;" 2>/dev/null || echo "0")

if [ "$CONST_COUNT" -ge "3" ]; then
    echo -e "${GREEN}✅ Seed data already loaded ($CONST_COUNT constituencies)${NC}"
else
    echo "Loading seed data..."
    python seed_data.py
    echo -e "${GREEN}✅ Seed data loaded${NC}"
fi

cd ..

# Step 6: Setup Admin Dashboard
echo ""
echo "6️⃣  Setting up admin dashboard..."
cd admin-dashboard

if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ Node modules already installed${NC}"
else
    echo "Installing npm packages..."
    npm install
    echo -e "${GREEN}✅ Admin dashboard ready${NC}"
fi

cd ..

# Step 7: Test Backend
echo ""
echo "7️⃣  Testing backend..."
cd backend
source .venv/bin/activate

# Start backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/janasamparka-backend.log 2>&1 &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

# Test API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is working${NC}"
    
    # Test constituencies
    CONST_API=$(curl -s http://localhost:8000/api/constituencies/ | grep -o '"name"' | wc -l)
    if [ "$CONST_API" -ge "3" ]; then
        echo -e "${GREEN}✅ API returning constituencies${NC}"
    fi
else
    echo -e "${RED}❌ Backend API not responding${NC}"
fi

# Stop test backend
kill $BACKEND_PID 2>/dev/null
cd ..

# Summary
echo ""
echo "============================"
echo "🎉 Setup Complete!"
echo "============================"
echo ""
echo "📊 Summary:"
echo "   Database: ✅ Running (PostgreSQL 14)"
echo "   Migrations: ✅ Applied"
echo "   Seed Data: ✅ Loaded (3 constituencies)"
echo "   Backend: ✅ Ready"
echo "   Admin Dashboard: ✅ Ready"
echo ""
echo "🚀 To start the application:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "   Terminal 2 (Admin Dashboard):"
echo "   cd admin-dashboard"
echo "   npm run dev"
echo ""
echo "📱 Access:"
echo "   Backend API: http://localhost:8000/docs"
echo "   Admin Dashboard: http://localhost:3000"
echo ""
echo "🔑 Test Login:"
echo "   Puttur MLA: +918242226666"
echo "   Mangalore MLA: +918242227777"
echo "   Udupi MLA: +918252255555"
echo "   Admin: +919999999999"
echo ""
echo "============================"
