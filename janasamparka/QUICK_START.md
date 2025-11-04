# ⚡ QUICK START - Complete Docker Setup

## 🚀 Run Everything (1 Command)

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up --build
```

**Wait 30-60 seconds**, then open:
- 🌐 **App:** http://localhost:3000
- 📡 **API:** http://localhost:8000/docs
- 🗄️ **DB:** localhost:5433

---

## 🔒 Login Credentials

**Phone:** `+918242226666`  
**OTP:** `123456`

---

## 🛑 Stop Everything

```bash
# Press Ctrl+C in the terminal
# OR
docker-compose down
```

---

## 📊 What's Running

| Service | Port | Status |
|---------|------|--------|
| **Frontend** (React) | 3000 | ✅ Docker |
| **Backend** (FastAPI) | 8000 | ✅ Docker |
| **Database** (PostgreSQL) | 5433 | ✅ Docker |

---

## 🔥 Hot Reload

**Edit code and save** - changes appear automatically!

- Frontend: Edit `admin-dashboard/src/*`
- Backend: Edit `backend/app/*`

---

## 📝 View Logs

```bash
docker-compose logs -f
```

---

## 🐛 Troubleshooting

### Port Already in Use?
```bash
# Stop conflicting services
docker-compose down

# Or kill specific port
lsof -i :3000  # Find process
kill -9 <PID>  # Kill it
```

### Service Not Starting?
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Fresh Start?
```bash
# ⚠️ Deletes all data!
docker-compose down -v
docker-compose up --build
```

---

## ✅ Health Check

```bash
# Check all services
docker-compose ps

# Test frontend
curl http://localhost:3000

# Test backend
curl http://localhost:8000/health

# Test database
docker exec janasamparka_db psql -U janasamparka -d janasamparka_db -c "SELECT 1;"
```

---

## 🧪 Run Tests

While containers are running (in another terminal):

```bash
# Backend API tests
./test_all_phases.sh

# Or detailed tests
python3 test_backend_comprehensive.py

# Frontend tests
# Follow: FRONTEND_TESTING_CHECKLIST.md
```

---

## 📚 Documentation

- **Full Docker Guide:** `DOCKER_SETUP.md`
- **Testing Guide:** `RUN_ALL_TESTS.md`
- **API Endpoints:** http://localhost:8000/docs

---

## 🎯 Complete Workflow

```bash
# 1. Start everything
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs (optional)
docker-compose logs -f

# 4. Work on code (auto-reloads)
# Edit files in admin-dashboard/ or backend/

# 5. Run tests (in another terminal)
./test_all_phases.sh

# 6. Stop when done
docker-compose down
```

---

## 🔄 Daily Usage

### **Morning:**
```bash
docker-compose up -d
```

### **During Development:**
- Edit code (auto-reloads)
- Check logs: `docker-compose logs -f`
- Restart if needed: `docker-compose restart frontend`

### **Evening:**
```bash
docker-compose down
```

---

## 📦 What Changed

### **Before (Old Setup):**
```bash
# Terminal 1: Database
psql ...

# Terminal 2: Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd admin-dashboard
npm run dev
```

### **After (New Docker Setup):**
```bash
# Single terminal:
docker-compose up
```

**That's it!** 🎉

---

## 🎊 Benefits

- ✅ **One command** to start everything
- ✅ **No local installations** needed
- ✅ **Consistent environment** across team
- ✅ **Hot-reload** works perfectly
- ✅ **Easy onboarding** for new devs
- ✅ **Production-ready** setup

---

## 🚀 First Time Setup

```bash
# 1. Navigate to project
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka

# 2. Start everything (builds containers first time)
docker-compose up --build

# 3. Wait for services to start (~30-60 seconds)
# Look for:
# ✓ Database ready
# ✓ Backend started
# ✓ Frontend ready

# 4. Open browser
open http://localhost:3000

# 5. Login
# Phone: +918242226666
# OTP: 123456

# 6. Test features!
```

---

## 🎯 Success Checklist

After running `docker-compose up`, verify:

- [ ] See "VITE ready" message for frontend
- [ ] See "Uvicorn running" message for backend
- [ ] See "database system is ready" message for DB
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/docs
- [ ] Can login to application
- [ ] Can view dashboard
- [ ] Can view map

---

## 💡 Pro Tips

1. **Run in background:** `docker-compose up -d`
2. **Follow logs:** `docker-compose logs -f frontend`
3. **Restart one service:** `docker-compose restart backend`
4. **Rebuild after changes:** `docker-compose build frontend`
5. **Check resource usage:** `docker stats`

---

## 🆘 Need Help?

1. **Read full guide:** `cat DOCKER_SETUP.md`
2. **Check logs:** `docker-compose logs`
3. **Test services:** `docker-compose ps`
4. **Fresh start:** `docker-compose down && docker-compose up --build`

---

**🐳 Enjoy your Dockerized development environment!**

**Ready to code!** 🚀
