# 📋 Manual Setup Guide - Step by Step

Choose **ONE** of these options:

---

## ✅ **Option A: Docker Setup (Recommended - Easiest)**

### 1. Start Docker Desktop
- Open Docker Desktop application
- Wait until it shows "Docker Desktop is running"

### 2. Start Database
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up -d
```

### 3. Continue to "Backend Setup" below

---

## ✅ **Option B: Local PostgreSQL (Manual)**

### 1. Setup Database

**Method 1: Using SQL file**
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
psql -f setup_db.sql
# Enter your PostgreSQL password when prompted
```

**Method 2: Manual commands**
```bash
# Create database
createdb janasamparka_db

# Enable PostGIS
psql janasamparka_db
```

Then inside psql:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
\q
```

---

## 🔧 Backend Setup (Same for Both Options)

### 1. Setup Python Environment

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/backend

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database Connection

Edit `backend/.env` (or create it from `.env.example`):

**For Docker:**
```bash
DATABASE_URL=postgresql://janasamparka:janasamparka123@localhost:5432/janasamparka_db
```

**For Local PostgreSQL:**
```bash
DATABASE_URL=postgresql://srbhandary:YOUR_PASSWORD@localhost:5432/janasamparka_db
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

### 3. Run Migrations

```bash
# Make sure you're in backend/ with .venv activated
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_multi_tenant
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
```

### 4. Load Seed Data

```bash
python seed_data.py
```

**Expected output:**
```
🌱 Starting seed data creation...
📍 Creating Puttur constituency...
✅ Puttur constituency created with 5 wards and 5 departments
📍 Creating Mangalore North constituency...
✅ Mangalore North constituency created with 5 wards and 5 departments
📍 Creating Udupi constituency...
✅ Udupi constituency created with 5 wards and 5 departments
👤 Creating super admin user...

============================================================
🎉 Seed data created successfully!
============================================================
```

### 5. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### 6. Test Backend (New Terminal)

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test constituencies
curl http://localhost:8000/api/constituencies/

# Open browser
open http://localhost:8000/docs
```

---

## 🎨 Admin Dashboard Setup

### 1. Install Dependencies

```bash
# New terminal window
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/admin-dashboard

# Install npm packages
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

**Expected output:**
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### 3. Test Admin Dashboard

Open browser: **http://localhost:3000**

You should see:
- Dashboard page
- Sidebar navigation
- 3 constituencies displayed

---

## ✅ Verification Checklist

Run these tests to verify everything works:

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","app":"Janasamparka MLA Connect"}
```

### Test 2: List Constituencies
```bash
curl http://localhost:8000/api/constituencies/
# Should return JSON with 3 constituencies
```

### Test 3: Request OTP
```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918242226666"}'
  
# Should return OTP (123456 in dev mode)
```

### Test 4: Verify OTP
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918242226666", "otp": "123456"}'
  
# Should return access token and user info
```

### Test 5: Admin Dashboard
- Open http://localhost:3000
- Should see Dashboard with stats
- Click "Constituencies" - should show 3 items
- Click on "Puttur" - should show details

---

## 🐛 Troubleshooting

### Backend won't start - "Database connection failed"

**Check if database is running:**

```bash
# For Docker:
docker-compose ps

# For Local PostgreSQL:
pg_isready
```

**Test connection manually:**
```bash
# For Docker:
psql -h localhost -U janasamparka -d janasamparka_db
# Password: janasamparka123

# For Local PostgreSQL:
psql -d janasamparka_db
```

### Backend won't start - "ModuleNotFoundError"

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Migrations fail

```bash
# Check current revision
alembic current

# If empty, make sure database is accessible
# Try migrations again
alembic upgrade head
```

### Seed data fails

```bash
# Check if tables exist
psql janasamparka_db -c "\dt"

# If no tables, run migrations first
alembic upgrade head

# Then try seed again
python seed_data.py
```

### Admin Dashboard - Network error

- Make sure backend is running on port 8000
- Check: http://localhost:8000/health
- Check browser console for errors

### Port already in use

```bash
# Find process using port
lsof -i :8000  # for backend
lsof -i :3000  # for frontend

# Kill process
kill -9 <PID>
```

---

## 🔄 Reset Everything (If needed)

```bash
# Stop all servers (Ctrl+C in terminals)

# Drop database and start fresh
psql -c "DROP DATABASE IF EXISTS janasamparka_db;"
psql -c "CREATE DATABASE janasamparka_db;"
psql janasamparka_db -c "CREATE EXTENSION postgis;"

# Re-run migrations and seed
cd backend
source .venv/bin/activate
alembic upgrade head
python seed_data.py
```

---

## 📝 Summary

Once everything is running, you'll have:

**Terminal 1:** Backend API on http://localhost:8000
**Terminal 2:** Admin Dashboard on http://localhost:3000

**Test Credentials:**
- Puttur MLA: +918242226666
- Mangalore MLA: +918242227777
- Udupi MLA: +918252255555
- Super Admin: +919999999999

**All OTPs in development mode:** 123456

---

## ✅ You're Ready!

Once both servers are running and you can access the admin dashboard, you're ready to proceed to **Step 2: Adding Authentication**!

Let me know when you have everything running and we'll move to the next step.
