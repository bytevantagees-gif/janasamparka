# 🚀 Setup Without Docker - Manual Installation

## Prerequisites

- Python 3.11+
- PostgreSQL 14+ with PostGIS extension
- Node.js 18+
- Homebrew (macOS)

---

## Step 1: Install PostgreSQL with PostGIS

```bash
# Install PostgreSQL and PostGIS
brew install postgresql@14 postgis

# Start PostgreSQL service
brew services start postgresql@14

# Wait a few seconds for service to start
sleep 3

# Create database
createdb janasamparka_db

# Enable PostGIS extension
psql janasamparka_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Verify installation
psql janasamparka_db -c "SELECT PostGIS_Version();"
```

---

## Step 2: Setup Backend

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (if not exists)
cp .env.example .env

# Edit .env to use local PostgreSQL
# Change DATABASE_URL to:
# DATABASE_URL=postgresql://YOUR_USERNAME@localhost/janasamparka_db
# (Replace YOUR_USERNAME with your Mac username)
```

---

## Step 3: Update .env File

Edit `backend/.env`:

```bash
# Application
APP_NAME=Janasamparka MLA Connect
APP_VERSION=1.0.0
DEBUG=true

# Database - LOCAL PostgreSQL
DATABASE_URL=postgresql://YOUR_MAC_USERNAME@localhost/janasamparka_db

# Security
SECRET_KEY=your-super-secret-key-change-in-production-12345678
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# OTP Settings
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5
OTP_MOCK=true

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

Replace `YOUR_MAC_USERNAME` with your actual username (run `whoami` to find it).

---

## Step 4: Run Database Migrations

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/backend

# Activate virtual environment
source .venv/bin/activate

# Run migrations
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001_multi_tenant
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
```

---

## Step 5: Load Seed Data

```bash
# Still in backend directory with .venv activated
python seed_data.py

# Expected output:
# 🌱 Starting seed data creation...
# 📍 Creating Puttur constituency...
# ✅ Puttur constituency created with 5 wards and 5 departments
# ... (similar for other constituencies)
# 🎉 Seed data created successfully!
```

---

## Step 6: Verify Database

```bash
# Check if constituencies were created
psql janasamparka_db -c "SELECT name, code, mla_name FROM constituencies;"

# Expected output:
#       name        |  code   |      mla_name       
# ------------------+---------+--------------------
#  Puttur           | PUT001  | Ashok Kumar Rai
#  Mangalore North  | MNG001  | B.A. Mohiuddin Bava
#  Udupi            | UDU001  | Yashpal A. Suvarna
```

---

## Step 7: Start Backend Server

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/backend
source .venv/bin/activate

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server should start at http://localhost:8000
```

### Test Backend

Open browser: **http://localhost:8000/docs**

Try:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/constituencies/
```

---

## Step 8: Setup Admin Dashboard

```bash
# New terminal
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/admin-dashboard

# Install dependencies
npm install

# Start development server
npm run dev

# Dashboard should start at http://localhost:3000
```

### Test Dashboard

Open browser: **http://localhost:3000**

Should show:
- Dashboard with statistics
- 3 constituencies
- Navigation working

---

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql@14

# Test connection
psql -l
```

### Permission Issues

```bash
# Create database with explicit user
createdb -U $(whoami) janasamparka_db

# Grant permissions
psql janasamparka_db -c "GRANT ALL PRIVILEGES ON DATABASE janasamparka_db TO $(whoami);"
```

### PostGIS Extension Error

```bash
# If PostGIS install failed, try:
psql janasamparka_db

# Inside psql:
CREATE EXTENSION IF NOT EXISTS postgis;
\q
```

---

## Stopping Services

### Stop Backend
Press `Ctrl+C` in backend terminal

### Stop Admin Dashboard
Press `Ctrl+C` in admin-dashboard terminal

### Stop PostgreSQL (Optional)
```bash
brew services stop postgresql@14
```

---

## Quick Start Commands

### Start Everything
```bash
# Terminal 1: Backend
cd ~/Documents/Projects/MLA/janasamparka/backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd ~/Documents/Projects/MLA/janasamparka/admin-dashboard
npm run dev
```

### Database Management
```bash
# Connect to database
psql janasamparka_db

# List tables
\dt

# View constituencies
SELECT * FROM constituencies;

# Exit
\q
```

---

✅ **That's it! You're running without Docker.**
