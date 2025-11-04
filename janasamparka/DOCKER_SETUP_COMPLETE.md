# Docker Setup - Complete Guide

## Overview
The entire Janasamparka MLA Connect application runs in Docker containers. All development, dependencies, and services are containerized.

**Date**: October 30, 2025  
**Status**: ✅ All services running in Docker  
**Containers**: 3 (Backend, Frontend, Database)

---

## Container Architecture

### 1. **Database Container** (PostgreSQL + PostGIS)
- **Image**: `postgis/postgis:15-3.3`
- **Port**: `5433:5432` (host:container)
- **Volume**: Database data persisted
- **Status**: ✅ Healthy

### 2. **Backend Container** (FastAPI + Python)
- **Image**: `janasamparka-backend` (custom)
- **Port**: `8000:8000` (host:container)
- **Working Dir**: `/app`
- **Status**: ✅ Running

### 3. **Frontend Container** (React + Vite)
- **Image**: `janasamparka-frontend` (custom)
- **Port**: `3000:3000` (host:container)
- **Working Dir**: `/app`
- **Status**: ✅ Running

---

## Quick Start

### Start All Containers
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up -d
```

### Check Container Status
```bash
docker-compose ps
# or
docker ps --filter "name=janasamparka"
```

### View Logs
```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

### Stop All Containers
```bash
docker-compose down
```

### Restart a Container
```bash
docker-compose restart frontend
docker-compose restart backend
```

---

## Frontend Container Details

### Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Installed Dependencies (Inside Container)
```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.12.2",
    "axios": "^1.6.2",
    "clsx": "^2.0.0",
    "leaflet": "^1.9.4",
    "leaflet.heat": "^0.2.0",
    "leaflet.markercluster": "^1.5.3",
    "lodash.debounce": "^4.0.8",
    "lucide-react": "^0.294.0",
    "prop-types": "^15.8.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-leaflet": "^4.2.1",
    "react-router-dom": "^6.20.0",
    "recharts": "^2.10.3",
    "tailwind-merge": "^2.1.0"
  }
}
```

### Installing New Dependencies
```bash
# Install package in running container
docker-compose exec frontend npm install <package-name>

# Then rebuild to persist
docker-compose down frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Accessing Container Shell
```bash
# Frontend
docker-compose exec frontend sh

# Backend
docker-compose exec backend bash

# Database
docker-compose exec db psql -U postgres -d janasamparka
```

---

## Backend Container Details

### Key Files
- **Dockerfile**: `/backend/Dockerfile`
- **Requirements**: `/backend/requirements.txt`
- **Entry Point**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Python Environment
- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + Alembic
- PostGIS + Shapely

### Installing Python Packages
```bash
# Add to requirements.txt first
echo "package-name==version" >> backend/requirements.txt

# Rebuild container
docker-compose down backend
docker-compose build backend
docker-compose up -d backend
```

### Running Migrations
```bash
# Access backend container
docker-compose exec backend bash

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

---

## Database Container Details

### Connection Details
- **Host**: `localhost` (from host machine)
- **Port**: `5433` (mapped from container's 5432)
- **Database**: `janasamparka`
- **User**: `postgres`
- **Password**: (set in docker-compose.yml)

### Accessing Database
```bash
# From host
psql -h localhost -p 5433 -U postgres -d janasamparka

# From Docker
docker-compose exec db psql -U postgres -d janasamparka
```

### Backup Database
```bash
docker-compose exec db pg_dump -U postgres janasamparka > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker-compose exec -T db psql -U postgres janasamparka
```

---

## Volume Management

### List Volumes
```bash
docker volume ls | grep janasamparka
```

### Inspect Volume
```bash
docker volume inspect janasamparka_db_data
```

### Remove All Data (CAUTION!)
```bash
docker-compose down -v
```

---

## Network Configuration

### Docker Network
All containers are on the same Docker network and can communicate using service names:
- Frontend → Backend: `http://backend:8000`
- Backend → Database: `postgresql://postgres@db:5432/janasamparka`

### Host Access
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Database: `localhost:5433`

---

## Common Tasks

### 1. Rebuild Everything
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 2. View Container Resources
```bash
docker stats
```

### 3. Clean Up Unused Images
```bash
docker image prune -a
```

### 4. Update Dependencies

**Frontend:**
```bash
# Update package.json locally
# Then rebuild
docker-compose down frontend
docker-compose build frontend
docker-compose up -d frontend
```

**Backend:**
```bash
# Update requirements.txt locally
# Then rebuild
docker-compose down backend
docker-compose build backend
docker-compose up -d backend
```

### 5. Check Container Health
```bash
docker inspect janasamparka_frontend --format='{{.State.Health.Status}}'
docker inspect janasamparka_backend --format='{{.State.Health.Status}}'
docker inspect janasamparka_db --format='{{.State.Health.Status}}'
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Check if port is in use
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5433  # Database

# Force recreate
docker-compose up -d --force-recreate <service-name>
```

### Package Not Found Error
```bash
# Verify package in container
docker-compose exec frontend npm list <package-name>

# Reinstall
docker-compose exec frontend npm install
```

### Permission Issues
```bash
# Frontend files owned by root
docker-compose exec frontend chown -R node:node /app

# Or rebuild with correct permissions
docker-compose build --no-cache frontend
```

### Database Connection Failed
```bash
# Check if DB is healthy
docker-compose ps

# Restart DB
docker-compose restart db

# Check DB logs
docker-compose logs db
```

---

## File Synchronization

### .dockerignore Files
Ensure these files exist to prevent unnecessary copying:

**Frontend** (`admin-dashboard/.dockerignore`):
```
node_modules
dist
.env
.env.local
.git
.gitignore
npm-debug.log*
.DS_Store
coverage
.vscode
```

**Backend** (`backend/.dockerignore`):
```
__pycache__
*.py[cod]
.env
.venv
venv/
.git
.gitignore
*.log
.pytest_cache
```

### Live Reload
Both frontend and backend support hot reload:
- **Frontend**: Vite watches for file changes
- **Backend**: Uvicorn `--reload` flag enabled

Changes to files are automatically reflected in the running containers.

---

## Local Development Without Docker

**NOT RECOMMENDED** - All development should be in Docker.

If you need to run locally:
```bash
# Frontend
cd admin-dashboard
npm install
npm run dev

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

But remember: **Everything should be in Docker!**

---

## Production Considerations

### Build for Production
```bash
# Frontend production build
docker-compose exec frontend npm run build

# Serve production build
docker-compose exec frontend npm run preview
```

### Environment Variables
Set in `docker-compose.yml`:
```yaml
environment:
  - NODE_ENV=production
  - VITE_API_URL=http://backend:8000
```

### Security
- [ ] Change default database passwords
- [ ] Use secrets management for sensitive data
- [ ] Configure proper CORS settings
- [ ] Enable SSL/TLS in production

---

## Summary

✅ **Frontend Container**: Running with all dependencies installed  
✅ **Backend Container**: Running with FastAPI and all Python packages  
✅ **Database Container**: Running with PostGIS extensions  
✅ **Networking**: All containers communicate properly  
✅ **Volumes**: Database data persisted  
✅ **Hot Reload**: Both frontend and backend support live reload  

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- Database: localhost:5433

**Container Status Check:**
```bash
docker ps --filter "name=janasamparka"
```

All services are running in Docker containers. No local installations needed! 🎉
