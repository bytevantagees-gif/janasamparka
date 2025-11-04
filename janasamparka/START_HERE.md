# 🚀 START HERE - Step-by-Step Setup

Follow these steps **in order** to get your system running.

---

## ✅ Step 1: Test Your Setup (5 minutes)

### Option A: Quick Python Test (Recommended)

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/backend

# Activate virtual environment
source .venv/bin/activate

# Run validation script
python test_system.py
```

**Expected Output:**
```
🚀 Janasamparka System Validation
✅ PASS - Imports
✅ PASS - Database
✅ PASS - Models
✅ PASS - Migrations
✅ PASS - Seed Data
✅ PASS - Constituencies
🎉 All tests passed! System is ready.
```

### Option B: Bash Test Script

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
./test_setup.sh
```

### 🔧 If Tests Fail

**Database not running?**
```bash
docker-compose up -d db
# Wait 5 seconds
docker-compose logs db
```

**Migrations not applied?**
```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

**No seed data?**
```bash
cd backend
source .venv/bin/activate
python seed_data.py
```

---

## 🚀 Step 2: Start Backend Server

```bash
# Terminal 1
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/backend

# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### ✅ Verify Backend is Running

**Open in browser:**
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

**Test API:**
```bash
# In another terminal
curl http://localhost:8000/api/constituencies/
```

Should return JSON with 3 constituencies.

---

## 🎨 Step 3: Start Admin Dashboard

```bash
# Terminal 2 (new terminal window)
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/admin-dashboard

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**You should see:**
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### ✅ Verify Admin Dashboard

**Open in browser:** http://localhost:3000

You should see:
- ✅ Sidebar with "ಜನಸಂಪರ್ಕ" logo
- ✅ Dashboard page with statistics
- ✅ "3" active constituencies
- ✅ Performance metrics

**Click around:**
1. Click "Constituencies" in sidebar
2. Should see 3 constituency cards (Puttur, Mangalore, Udupi)
3. Click on "Puttur"
4. Should see detailed info with MLA name, stats, etc.

---

## 🧪 Step 4: Test API Features

### Test 1: List All Constituencies

**Browser:** http://localhost:8000/docs
- Find `GET /api/constituencies/`
- Click "Try it out"
- Click "Execute"
- Should see 3 constituencies

### Test 2: Get Constituency Details

**Browser:** http://localhost:8000/docs
- Find `GET /api/constituencies/{constituency_id}`
- Click "Try it out"
- Copy any `id` from previous response
- Paste in `constituency_id` field
- Click "Execute"
- Should see full details with statistics

### Test 3: Request OTP (Authentication)

**Method 1: Via Swagger UI**
- Find `POST /api/auth/request-otp`
- Click "Try it out"
- Enter: `{"phone": "+918242226666"}` (Puttur MLA)
- Click "Execute"
- Response includes OTP (in development mode)

**Method 2: Via cURL**
```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918242226666"}'
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "phone": "+918242226666",
  "otp": "123456",
  "expires_in_minutes": 5
}
```

### Test 4: Verify OTP and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+918242226666",
    "otp": "123456"
  }'
```

**Response includes:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "name": "Ashok Kumar Rai",
    "phone": "+918242226666",
    "role": "mla"
  }
}
```

### Test 5: Create a Complaint

```bash
curl -X POST http://localhost:8000/api/complaints/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pothole on Main Road",
    "description": "Large pothole near bus stand",
    "category": "road",
    "lat": 12.7644,
    "lng": 75.4088
  }'
```

### Test 6: Get Complaint Statistics

**Browser:** http://localhost:8000/api/complaints/stats/summary

---

## 🎉 Success! What's Running?

If all tests pass, you now have:

### ✅ Backend API (Port 8000)
- FastAPI server
- PostgreSQL database with PostGIS
- 3 constituencies loaded
- Authentication working
- All CRUD endpoints functional

### ✅ Admin Dashboard (Port 3000)
- React frontend
- Tailwind CSS styling
- TanStack Query for data fetching
- Connected to backend API
- Real-time data updates

---

## 🔍 Troubleshooting

### Backend won't start

**Error: "Port 8000 already in use"**
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

**Error: "Database connection failed"**
```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

**Error: "ModuleNotFoundError"**
```bash
# Reinstall dependencies
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Admin Dashboard won't start

**Error: "Port 3000 already in use"**
```bash
lsof -i :3000
kill -9 <PID>
```

**Error: "Cannot find module"**
```bash
cd admin-dashboard
rm -rf node_modules package-lock.json
npm install
```

**Error: "Network request failed" / "API not responding"**
- Make sure backend is running on port 8000
- Check: http://localhost:8000/health
- Check CORS settings in backend

### Database issues

**Reset database (⚠️ WARNING: Deletes all data)**
```bash
docker-compose down -v
docker-compose up -d db
cd backend
source .venv/bin/activate
alembic upgrade head
python seed_data.py
```

---

## 📚 Next Steps

Now that everything is running, you can:

### 1. Explore the Admin Dashboard
- View all 3 constituencies
- Check performance metrics
- Compare constituency statistics

### 2. Test API Endpoints
- Use Swagger UI: http://localhost:8000/docs
- Create test complaints
- Assign complaints to departments
- Update complaint status

### 3. Add More Data
- Create additional wards
- Add department officers
- Submit more complaints
- Create polls

### 4. Development
Ready to add features? Check:
- **SETUP_COMPLETE.md** - Full roadmap
- **MULTI_TENANT_ARCHITECTURE.md** - Architecture details
- **admin-dashboard/README.md** - Frontend development

---

## 🎯 What's Next?

I recommend implementing in this order:

### **Priority 1: Authentication for Admin Dashboard** 🔐
Add login screen and protected routes

### **Priority 2: Complaint Management UI** 📋
Complete interface for managing complaints

### **Priority 3: Ward Management** 🗺️
Interface for creating/editing wards

### **Priority 4: Mobile App** 📱
Flutter app for citizens

---

## 📞 Quick Commands Reference

### Start Everything
```bash
# Terminal 1: Backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd admin-dashboard && npm run dev
```

### Stop Everything
```bash
# Ctrl+C in both terminals
docker-compose down  # Stops database
```

### Restart Database
```bash
docker-compose restart db
```

### View Logs
```bash
# Backend logs: visible in terminal
# Database logs:
docker-compose logs -f db
```

### Apply New Migrations
```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## ✅ Checklist

- [ ] Database running (`docker-compose ps`)
- [ ] Migrations applied (`alembic current`)
- [ ] Seed data loaded (`python test_system.py`)
- [ ] Backend API running (http://localhost:8000/docs)
- [ ] Admin dashboard running (http://localhost:3000)
- [ ] Can view 3 constituencies
- [ ] Can request/verify OTP
- [ ] Can create complaints

---

🎉 **You're all set! Happy coding!** 🎉

**Questions?** Check the documentation files or create an issue.

---

**Created:** October 27, 2025  
**Version:** 1.0.0-alpha
