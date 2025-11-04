# ⚡ Quick Start Guide - 5 Minutes to Running Backend

## Option 1: Docker Compose (Fastest - Recommended)

### Step 1: Start Everything
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka

# Start database and backend
docker-compose up -d

# Watch the logs
docker-compose logs -f backend
```

### Step 2: Open API Documentation
Visit http://localhost:8000/docs

### Step 3: Test the API
```bash
# Health check
curl http://localhost:8000/health

# Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# You'll get back an OTP (in development mode)
# Use it to verify and get a token
```

**That's it! Your backend is running!** 🎉

---

## Option 2: Manual Setup (If Docker Not Available)

### Step 1: Install PostgreSQL with PostGIS
```bash
# macOS
brew install postgresql postgis

# Start PostgreSQL
brew services start postgresql

# Create database
createdb janasamparka_db

# Enable PostGIS
psql janasamparka_db -c "CREATE EXTENSION postgis;"
```

### Step 2: Set Up Python Environment
```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# The default settings should work for local PostgreSQL
```

### Step 4: Run Migrations
```bash
# Initialize database schema
alembic upgrade head
```

### Step 5: Start the Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Access API
Open http://localhost:8000/docs

---

## 🧪 Quick API Tests

### 1. Request OTP
```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "phone": "+919876543210",
  "otp": "123456",
  "expires_in_minutes": 5
}
```

### 2. Verify OTP
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "otp": "123456"}'
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "name": "User 3210",
    "phone": "+919876543210",
    "role": "citizen"
  }
}
```

### 3. Create a Complaint
```bash
curl -X POST http://localhost:8000/api/complaints/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pothole on Main Road",
    "description": "Large pothole near bus stand",
    "category": "road",
    "lat": 12.9141,
    "lng": 75.2479
  }'
```

### 4. Get All Complaints
```bash
curl http://localhost:8000/api/complaints/
```

### 5. Get Statistics
```bash
curl http://localhost:8000/api/complaints/stats/summary
```

---

## 🛠️ Common Commands

### Docker
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart backend only
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build
```

### Database Migrations
```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Development
```bash
# Run tests
pytest

# Format code
black app/

# Check types
mypy app/
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps

# Or for manual setup
pg_isready
```

### Migration Issues
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d

# Run migrations
cd backend
alembic upgrade head
```

---

## 📚 Next Steps

1. ✅ Backend is running
2. 🔜 Test all API endpoints via Swagger UI
3. 🔜 Set up Flutter mobile app
4. 🔜 Set up React admin dashboard
5. 🔜 Add authentication middleware
6. 🔜 Implement file uploads
7. 🔜 Add voice-to-text integration

---

## 🎯 What You Have Now

✅ **Working Backend API** with:
- User authentication (OTP-based)
- Complaint management
- Status tracking
- Basic analytics
- PostgreSQL + PostGIS database
- API documentation
- Docker setup

✅ **Database Models** for:
- Users
- Wards (with geographic data)
- Departments
- Complaints
- Media attachments
- Status logs
- Polls & voting

✅ **Ready for**:
- Mobile app integration
- Admin dashboard integration
- External API connections
- Production deployment

---

## 💡 Pro Tips

1. **Always use Swagger UI** for testing: http://localhost:8000/docs
2. **Check logs** if something doesn't work: `docker-compose logs -f`
3. **Database changes?** Run `alembic revision --autogenerate`
4. **Need to reset?** `docker-compose down -v && docker-compose up -d`

---

Happy Coding! 🚀
