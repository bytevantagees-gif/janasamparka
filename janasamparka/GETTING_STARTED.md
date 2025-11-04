# 🚀 Getting Started with Janasamparka Admin Dashboard

## Quick Start Guide

This guide will help you get the Janasamparka admin dashboard up and running on your local machine.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **PostgreSQL 14+** with PostGIS - Database
- **Docker** (optional) - For containerized database
- **Git** - Version control

---

## 🛠️ Installation Steps

### **Step 1: Clone the Repository**

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
```

---

### **Step 2: Setup Backend (FastAPI)**

#### **2.1: Navigate to Backend Directory**
```bash
cd backend
```

#### **2.2: Create Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### **2.3: Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **2.4: Configure Environment**
```bash
cp .env.example .env
```

Edit `.env` file with your settings:
```env
DATABASE_URL=postgresql://user:password@localhost:5433/janasamparka
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
```

#### **2.5: Start PostgreSQL (Docker)**
```bash
docker-compose up -d
```

Or install PostgreSQL locally and create database:
```sql
CREATE DATABASE janasamparka;
CREATE EXTENSION postgis;
```

#### **2.6: Run Migrations**
```bash
alembic upgrade head
```

#### **2.7: Seed Database**
```bash
python seed_data.py
```

#### **2.8: Start Backend Server**
```bash
uvicorn app.main:app --reload --port 8000
```

✅ **Backend should now be running at:** http://localhost:8000

---

### **Step 3: Setup Frontend (React)**

#### **3.1: Open New Terminal**
Keep the backend running and open a new terminal.

#### **3.2: Navigate to Frontend Directory**
```bash
cd admin-dashboard
```

#### **3.3: Install Dependencies**
```bash
npm install
```

#### **3.4: Start Development Server**
```bash
npm run dev
```

✅ **Frontend should now be running at:** http://localhost:3000

---

## 🔑 Test Login Credentials

Use these test accounts to login:

### **MLAs:**
1. **Puttur MLA**
   - Phone: `+918242226666`
   - OTP: `123456` (displayed on screen in dev mode)

2. **Mangalore North MLA**
   - Phone: `+918242227777`
   - OTP: `123456`

3. **Udupi MLA**
   - Phone: `+918252255555`
   - OTP: `123456`

### **Admin:**
- Phone: `+919999999999`
- OTP: `123456`

### **Test Citizen:**
- Phone: `+919876543210`
- OTP: `123456`

---

## 🗺️ Navigation Guide

### **Main Sections:**

1. **Dashboard** (`/dashboard`)
   - Overview statistics
   - Complaint trends
   - Recent activity

2. **Constituencies** (`/constituencies`)
   - View all constituencies
   - Manage constituency details

3. **Complaints** (`/complaints`)
   - List all complaints
   - Search and filter
   - View details
   - Update status
   - Assign departments
   - Upload photos

4. **Wards** (`/wards`)
   - Ward management
   - Demographics
   - Infrastructure tracking

5. **Departments** (`/departments`)
   - Department list
   - Performance metrics
   - Leaderboard

6. **Polls** (`/polls`)
   - View active polls
   - Monitor voting
   - See results

7. **Users** (`/users`)
   - User management
   - Role assignment
   - Search users

8. **Settings** (`/settings`)
   - Profile settings
   - Notifications
   - Privacy preferences

---

## 🧪 Testing the System

### **Test Complaint Workflow:**

1. **View Complaints**
   - Navigate to Complaints
   - Use search and filters

2. **View Complaint Detail**
   - Click any complaint
   - Review all information

3. **Update Status**
   - Click "Update Status"
   - Select new status
   - Add note
   - Submit

4. **Assign Department**
   - Click "Assign Department"
   - Select department
   - Choose officer (optional)
   - Set priority
   - Submit

5. **Upload Photos**
   - Click "Upload Photos"
   - Select photo type (Before/During/After)
   - Drag or select files
   - Add caption
   - Upload

### **Test Polls:**

1. Navigate to Polls
2. View active polls
3. Check vote distribution
4. See leading options

### **Test Department Performance:**

1. Navigate to Departments
2. View performance metrics
3. Check leaderboard
4. Review resolution rates

---

## 🔧 Troubleshooting

### **Backend Won't Start**

**Issue:** `ModuleNotFoundError: No module named 'app'`  
**Solution:** Ensure you're in the `backend` directory and virtual environment is activated

**Issue:** `sqlalchemy.exc.OperationalError: could not connect to server`  
**Solution:** Check PostgreSQL is running:
```bash
docker-compose ps
# or
pg_isready
```

### **Frontend Won't Start**

**Issue:** `Error: Cannot find module`  
**Solution:** Delete `node_modules` and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

**Issue:** `CORS Error when calling API`  
**Solution:** Check backend `.env` has correct CORS_ORIGINS

### **Login Issues**

**Issue:** OTP not working  
**Solution:** In development, OTP is automatically displayed on the login screen. Use `123456` for any phone number.

**Issue:** "Invalid credentials"  
**Solution:** Ensure seed_data.py has run successfully and created test users

---

## 🌐 API Documentation

Once the backend is running, visit:

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

---

## 📁 Project Structure

```
janasamparka/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── core/              # Core configuration
│   │   ├── models/            # Database models
│   │   ├── routers/           # API endpoints
│   │   ├── schemas/           # Pydantic schemas
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   ├── seed_data.py           # Sample data
│   └── .env                   # Environment variables
│
├── admin-dashboard/            # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── contexts/          # React contexts
│   │   ├── pages/             # Page components
│   │   ├── services/          # API clients
│   │   └── main.jsx           # Entry point
│   └── package.json
│
├── docker-compose.yml          # Docker configuration
└── Documentation/              # Project docs
```

---

## 🎯 Common Tasks

### **Add New User**

```bash
# Start Python shell in backend
python
```

```python
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = User(
    name="New User",
    phone="+911234567890",
    role="moderator",
    constituency_id="your-constituency-id"
)
db.add(user)
db.commit()
```

### **Reset Database**

```bash
cd backend
alembic downgrade base
alembic upgrade head
python seed_data.py
```

### **View Database**

```bash
# Using psql
psql -U postgres -d janasamparka -h localhost -p 5433

# List tables
\dt

# View users
SELECT * FROM users;
```

### **Build for Production**

**Backend:**
```bash
cd backend
pip install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
cd admin-dashboard
npm run build
# Deploy dist/ folder to web server
```

---

## 🔐 Security Best Practices

### **For Development:**
- ✅ Use `.env` for secrets
- ✅ Don't commit `.env` to git
- ✅ Use strong SECRET_KEY
- ✅ Enable CORS only for trusted origins

### **For Production:**
- ✅ Use environment variables
- ✅ Enable HTTPS/SSL
- ✅ Use strong database passwords
- ✅ Set up firewall rules
- ✅ Enable rate limiting
- ✅ Set up monitoring
- ✅ Regular backups
- ✅ Use CDN for static assets

---

## 📞 Support & Help

### **Common Issues:**

1. **Port Already in Use**
   ```bash
   # Kill process on port 8000
   lsof -ti:8000 | xargs kill -9
   
   # Kill process on port 3000
   lsof -ti:3000 | xargs kill -9
   ```

2. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure PostGIS extension is installed

3. **Module Import Errors**
   - Activate virtual environment
   - Reinstall dependencies
   - Check Python version (3.11+)

---

## 🎓 Next Steps

After getting the system running:

1. **Explore Features**
   - Try all navigation sections
   - Test complaint workflow
   - Create test polls
   - View analytics

2. **Customize**
   - Update branding
   - Modify colors in Tailwind config
   - Add your constituency data

3. **Deploy**
   - Set up production server
   - Configure SSL
   - Set up monitoring
   - Deploy to cloud

4. **Train Users**
   - MLA office staff
   - Department officers
   - Moderators

---

## ✅ Quick Checklist

- [ ] PostgreSQL running
- [ ] Backend dependencies installed
- [ ] Backend server running (port 8000)
- [ ] Frontend dependencies installed
- [ ] Frontend server running (port 3000)
- [ ] Can access login page
- [ ] Can login with test credentials
- [ ] Can navigate dashboard
- [ ] Can view complaints
- [ ] Can update complaint status
- [ ] Can assign departments
- [ ] Can upload photos

---

## 🎉 Success!

If you can complete the checklist above, you're all set! The Janasamparka admin dashboard is now running on your machine.

**Happy Testing! 🚀**

---

**Need Help?**  
Check the troubleshooting section or review the API documentation at http://localhost:8000/docs

**Document Version:** 1.0  
**Last Updated:** October 27, 2025
