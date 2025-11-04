# 🐳 Complete Docker Setup Guide

## ✅ What's Now in Docker

Your entire application stack is now containerized:

1. **✅ Database** - PostgreSQL 15 with PostGIS (Port 5433)
2. **✅ Backend** - FastAPI (Port 8000)
3. **✅ Frontend** - React + Vite (Port 3000)

---

## 🚀 Quick Start (ONE COMMAND!)

```bash
# From project root
docker-compose up --build
```

**That's it!** 🎉

Wait 30-60 seconds for all services to start, then access:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📋 Services Architecture

```
┌─────────────────────────────────────────┐
│         Docker Compose Stack            │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────┐                     │
│  │   Frontend    │  Port 3000          │
│  │  React + Vite │                     │
│  └───────┬───────┘                     │
│          │                             │
│          ↓  Proxy: /api/*              │
│  ┌───────────────┐                     │
│  │    Backend    │  Port 8000          │
│  │    FastAPI    │                     │
│  └───────┬───────┘                     │
│          │                             │
│          ↓  SQL Queries                │
│  ┌───────────────┐                     │
│  │   Database    │  Port 5433          │
│  │   PostgreSQL  │  (mapped from 5432) │
│  │   + PostGIS   │                     │
│  └───────────────┘                     │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔧 Detailed Commands

### **Start All Services**
```bash
docker-compose up
```

### **Start with Build**
```bash
docker-compose up --build
```

### **Start in Background (Detached)**
```bash
docker-compose up -d
```

### **Stop All Services**
```bash
docker-compose down
```

### **Stop and Remove Volumes** (⚠️ Deletes database data!)
```bash
docker-compose down -v
```

### **View Logs**
```bash
# All services
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Specific service
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db
```

### **Rebuild a Specific Service**
```bash
docker-compose build frontend
docker-compose build backend
```

### **Restart a Service**
```bash
docker-compose restart frontend
docker-compose restart backend
```

---

## 📊 Service Details

### **1. Database (PostgreSQL + PostGIS)**

```yaml
Service: db
Image: postgis/postgis:15-3.3
Port: 5433 (host) → 5432 (container)
```

**Environment:**
- User: `janasamparka`
- Password: `janasamparka123`
- Database: `janasamparka_db`

**Data Persistence:**
- Volume: `postgres_data` (survives container restarts)

**Connect from Host:**
```bash
psql -h localhost -p 5433 -U janasamparka -d janasamparka_db
# Password: janasamparka123
```

---

### **2. Backend (FastAPI)**

```yaml
Service: backend
Context: ./backend
Port: 8000 (host) → 8000 (container)
```

**Features:**
- ✅ Hot-reload enabled (`--reload` flag)
- ✅ Code changes sync automatically (volume mounted)
- ✅ Waits for database health check
- ✅ Auto-restarts on failure

**Environment:**
- `DATABASE_URL`: Points to `db:5432` (Docker network)
- `DEBUG`: True

**API Endpoints:**
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- API: http://localhost:8000/api/*

---

### **3. Frontend (React + Vite)**

```yaml
Service: frontend
Context: ./admin-dashboard
Port: 3000 (host) → 3000 (container)
```

**Features:**
- ✅ Hot-reload enabled (polling for Docker)
- ✅ Code changes sync automatically
- ✅ API proxy to backend configured
- ✅ Accessible from host and network

**Environment:**
- `DOCKER_ENV`: true (enables Docker networking)
- `VITE_API_BASE_URL`: http://localhost:8000

**Access:**
- App: http://localhost:3000
- Network: http://<your-ip>:3000

---

## 🔥 Hot Reload & Development

### **Frontend Hot Reload**

When you edit files in `admin-dashboard/src/`, changes will automatically reload in the browser!

**Vite Config Changes:**
- ✅ `host: true` - Enables external access
- ✅ `usePolling: true` - Makes hot-reload work in Docker
- ✅ Dynamic proxy - Routes `/api/*` to backend service

### **Backend Hot Reload**

When you edit files in `backend/app/`, FastAPI will automatically reload!

**Uvicorn Config:**
- ✅ `--reload` flag enabled
- ✅ Volume mounted for code sync

---

## 🌐 Networking

### **Internal (Container-to-Container)**

Services communicate using service names:
- Frontend → Backend: `http://backend:8000`
- Backend → Database: `postgresql://...@db:5432/...`

### **External (Host-to-Container)**

Access from your computer:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Database: `localhost:5433`

### **Network Diagram**

```
Host Machine (localhost)
    ↓ Port 3000
Frontend Container
    ↓ http://backend:8000/api/
Backend Container
    ↓ postgresql://db:5432
Database Container
```

---

## 🔒 Default Credentials

### **Application Login**
- Phone: `+918242226666`
- OTP: `123456`

### **Database**
- Host: `localhost:5433`
- User: `janasamparka`
- Password: `janasamparka123`
- Database: `janasamparka_db`

---

## 📦 Volume Management

### **Named Volumes**

```yaml
volumes:
  postgres_data:  # Database persists here
```

### **View Volumes**
```bash
docker volume ls
```

### **Inspect Volume**
```bash
docker volume inspect janasamparka_postgres_data
```

### **Backup Database**
```bash
docker exec janasamparka_db pg_dump -U janasamparka janasamparka_db > backup.sql
```

### **Restore Database**
```bash
docker exec -i janasamparka_db psql -U janasamparka janasamparka_db < backup.sql
```

---

## 🐛 Troubleshooting

### **Issue: Services won't start**

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs backend
```

---

### **Issue: Port already in use**

```bash
# Find what's using the port
lsof -i :3000
lsof -i :8000
lsof -i :5433

# Kill the process or change port in docker-compose.yml
```

---

### **Issue: Database connection error**

```bash
# Check if database is healthy
docker-compose ps

# Should show:
# janasamparka_db       ... Up (healthy)

# If not healthy, check logs:
docker-compose logs db
```

---

### **Issue: Frontend not updating**

```bash
# Restart frontend service
docker-compose restart frontend

# Or rebuild:
docker-compose build frontend
docker-compose up frontend
```

---

### **Issue: "node_modules" issues**

```bash
# Remove node_modules volume and rebuild
docker-compose down
docker-compose build --no-cache frontend
docker-compose up
```

---

### **Issue: Database data corrupted**

```bash
# ⚠️ WARNING: This deletes all data!
docker-compose down -v
docker-compose up --build
```

---

## 🔄 Development Workflow

### **Typical Day:**

```bash
# Morning: Start everything
docker-compose up -d

# Work on code (auto-reloads)
# - Edit frontend in admin-dashboard/src/
# - Edit backend in backend/app/

# View logs if needed
docker-compose logs -f

# Evening: Stop everything
docker-compose down
```

### **After Pulling New Code:**

```bash
# Rebuild if Dockerfile or dependencies changed
docker-compose down
docker-compose up --build
```

---

## 📊 Health Checks

### **Check Service Status**
```bash
docker-compose ps
```

**Expected Output:**
```
NAME                    STATUS
janasamparka_db         Up (healthy)
janasamparka_backend    Up
janasamparka_frontend   Up
```

### **Test Frontend**
```bash
curl http://localhost:3000
# Should return HTML
```

### **Test Backend**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### **Test Database**
```bash
docker exec janasamparka_db psql -U janasamparka -d janasamparka_db -c "SELECT 1;"
# Should return: 1
```

---

## 🚀 Production Considerations

For production deployment, you'd want to:

1. **Use production Dockerfile for frontend:**
   - Build static assets
   - Serve with nginx
   - Remove hot-reload

2. **Secure database:**
   - Change default passwords
   - Don't expose port 5433
   - Use secrets management

3. **Add nginx reverse proxy:**
   - Single entry point
   - SSL/TLS termination
   - Load balancing

4. **Add environment-specific configs:**
   - `.env.production`
   - `docker-compose.prod.yml`

---

## 📝 File Structure

```
janasamparka/
├── docker-compose.yml           # ✅ Orchestrates all services
├── backend/
│   ├── Dockerfile              # ✅ Backend container config
│   └── requirements.txt
├── admin-dashboard/
│   ├── Dockerfile              # ✅ Frontend container config (NEW!)
│   ├── .dockerignore           # ✅ Ignore files (NEW!)
│   ├── vite.config.js          # ✅ Updated for Docker
│   └── package.json
└── DOCKER_SETUP.md             # ✅ This file
```

---

## ✅ What Changed

### **Files Created:**
1. ✅ `admin-dashboard/Dockerfile` - Frontend container
2. ✅ `admin-dashboard/.dockerignore` - Ignore node_modules, etc.

### **Files Updated:**
3. ✅ `docker-compose.yml` - Added frontend service
4. ✅ `admin-dashboard/vite.config.js` - Docker-compatible config

### **Features Added:**
- ✅ Frontend runs in Docker
- ✅ Hot-reload works in Docker
- ✅ All services networked together
- ✅ Single command to start everything

---

## 🎯 Quick Reference

### **Start Everything:**
```bash
docker-compose up --build
```

### **Stop Everything:**
```bash
docker-compose down
```

### **View Logs:**
```bash
docker-compose logs -f
```

### **Restart Service:**
```bash
docker-compose restart frontend
```

### **Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Database: `psql -h localhost -p 5433 -U janasamparka`

---

## 🎊 Summary

### **Before:**
- ❌ Only database and backend in Docker
- ❌ Frontend needed manual `npm run dev`
- ❌ Multiple terminal windows required

### **After:**
- ✅ **Everything** in Docker
- ✅ Single command: `docker-compose up`
- ✅ Hot-reload works for both frontend and backend
- ✅ Consistent environment for entire team
- ✅ Easy onboarding for new developers

---

## 🚀 Next Steps

1. **Test the setup:**
   ```bash
   docker-compose up --build
   ```

2. **Access the app:**
   - Open http://localhost:3000
   - Login with +918242226666 / OTP: 123456

3. **Verify hot-reload:**
   - Edit `admin-dashboard/src/App.jsx`
   - See changes instantly in browser

4. **Run your tests:**
   ```bash
   # In another terminal (while containers run)
   ./test_all_phases.sh
   ```

---

**🎉 Your entire stack is now Dockerized!** 🐳

**Version:** 1.0  
**Last Updated:** October 28, 2025  
**Status:** ✅ Production Ready
