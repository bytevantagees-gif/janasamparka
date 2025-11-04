# Demo Deployment Guide

## Overview
This guide explains how to maintain a stable demo environment separate from production development.

## Git Strategy: Tags + Branches

### Current Setup
- **`demo-stable`** branch - Frozen demo state, never modified
- **`main`** branch - Active production development
- **`v1.0.0-demo`** tag - Specific demo snapshot

## Creating the Demo State

### 1. Commit All Current Changes
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka

# Add all seeding and demo files
git add backend/seed_database.py
git add backend/create_department_users.py
git add backend/create_moderator.py
git add backend/delete_dept_officers.py
git add SEEDING_GUIDE.md
git add GIT_COMMIT_CHECKLIST.md
git add DEMO_DEPLOYMENT_GUIDE.md
git add admin-dashboard/src/pages/Login.jsx

# Commit the demo state
git commit -m "feat: Complete demo environment setup

- Database seeding with test users (3 moderators, 15 dept officers, 3 auditors)
- All phone numbers in correct Indian format (+91 + 10 digits)
- 16 sample complaints in Puttur on real roads
- Login page with quick test buttons
- Complete restoration documentation

This commit represents a stable demo state that can be deployed anywhere."
```

### 2. Create Demo Branch (Frozen State)
```bash
# Create and switch to demo branch
git checkout -b demo-stable

# Push demo branch to remote
git push origin demo-stable

# Tag this specific commit
git tag -a v1.0.0-demo -m "Stable demo environment with test data
- 3 Moderators
- 15 Department Officers  
- 3 Auditors
- 16 Puttur sample complaints
- All features working
- Ready for demo deployment"

# Push the tag
git push origin v1.0.0-demo

# Switch back to main for production work
git checkout main
```

### 3. Continue Production Development on Main
```bash
# Now on main branch - continue development
git checkout main

# Make production changes
git add .
git commit -m "production changes..."
git push origin main
```

## Deploying Demo Environment

### Fresh Demo Deployment (Anytime, Anywhere)

#### Option 1: Using Demo Branch
```bash
# Clone the repository
git clone https://github.com/your-username/janasamparka.git
cd janasamparka

# Checkout demo branch
git checkout demo-stable

# Deploy
cd janasamparka
docker compose up -d

# Wait for services
sleep 60

# Seed demo data
docker compose exec backend python seed_database.py

# Access demo
# http://your-server:3000
```

#### Option 2: Using Demo Tag (Specific Version)
```bash
# Clone and checkout specific demo tag
git clone https://github.com/your-username/janasamparka.git
cd janasamparka
git checkout tags/v1.0.0-demo

# Deploy same as above
cd janasamparka
docker compose up -d
sleep 60
docker compose exec backend python seed_database.py
```

## Demo vs Production Comparison

| Aspect | Demo (`demo-stable`) | Production (`main`) |
|--------|---------------------|-------------------|
| **Purpose** | Stable demos, client presentations | Active development |
| **Changes** | **FROZEN** - Never modified | Continuous updates |
| **Data** | Test users + 16 sample complaints | Real user data |
| **Users** | 21 test users with known passwords | Real users |
| **Updates** | Only for critical bugs | Regular features |
| **Database** | Can reset anytime | Persistent data |

## Environment Files

### Demo Environment (.env.demo)
```bash
# Copy to your demo server
cp .env.example .env.demo

# Edit demo-specific settings
nano .env.demo
```

```env
# Demo Environment Variables
NODE_ENV=demo
DATABASE_URL=postgresql://janasamparka:demo_password@db:5432/janasamparka
SECRET_KEY=demo_secret_key_change_in_production
FRONTEND_URL=http://demo.yourcompany.com:3000
BACKEND_URL=http://demo.yourcompany.com:8000

# Demo mode flag
DEMO_MODE=true
ALLOW_SEED_DATA=true
```

### Production Environment (.env.production)
```env
# Production Environment Variables
NODE_ENV=production
DATABASE_URL=postgresql://janasamparka:strong_password@db:5432/janasamparka_prod
SECRET_KEY=very_strong_secret_key_for_production
FRONTEND_URL=https://app.yourcompany.com
BACKEND_URL=https://api.yourcompany.com

# Production security
DEMO_MODE=false
ALLOW_SEED_DATA=false
```

## Docker Compose for Different Environments

### Demo (docker-compose.demo.yml)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: janasamparka_demo_backend
    environment:
      - NODE_ENV=demo
    ports:
      - "8000:8000"
    
  frontend:
    build: ./admin-dashboard
    container_name: janasamparka_demo_frontend
    environment:
      - VITE_API_URL=http://demo.yourserver.com:8000
    ports:
      - "3000:3000"
    
  db:
    image: postgis/postgis:15-3.3
    container_name: janasamparka_demo_db
    environment:
      - POSTGRES_DB=janasamparka_demo
```

### Production (docker-compose.production.yml)
Already exists in your repo - keep separate from demo.

## Complete Demo Deployment Workflow

### On Demo Server
```bash
# 1. Clone repository
git clone https://github.com/your-username/janasamparka.git demo-deployment
cd demo-deployment

# 2. Checkout demo branch
git checkout demo-stable

# 3. Setup environment
cp .env.example .env
# Edit .env with demo settings

# 4. Start containers
cd janasamparka
docker compose -f docker-compose.demo.yml up -d

# 5. Wait for database
sleep 60

# 6. Run migrations
docker compose exec backend alembic upgrade head

# 7. Seed demo data
docker compose exec backend python seed_database.py

# 8. Verify
curl http://localhost:3000
curl http://localhost:8000/health

# 9. Access demo
# Login: http://localhost:3000/login
# Use any test phone: +9199001000 / password: demo
```

## Updating Demo (When Needed)

### For Critical Bug Fixes Only
```bash
# On your development machine
git checkout demo-stable

# Make minimal fix
git add fixed-file.py
git commit -m "fix: Critical demo bug - description"
git push origin demo-stable

# Create new demo tag
git tag -a v1.0.1-demo -m "Bug fix release"
git push origin v1.0.1-demo

# Switch back to main
git checkout main
```

### On Demo Server (Pull Updates)
```bash
cd demo-deployment/janasamparka
git pull origin demo-stable
docker compose down
docker compose up -d --build
docker compose exec backend python seed_database.py
```

## Database Backup/Restore for Demo

### Backup Demo State
```bash
# Backup current demo database
docker compose exec db pg_dump -U janasamparka janasamparka_demo > demo_backup_$(date +%Y%m%d).sql
```

### Restore Demo State
```bash
# Restore from backup
docker compose exec -T db psql -U janasamparka janasamparka_demo < demo_backup_20241104.sql
```

### Quick Reset Demo
```bash
# Nuclear reset - back to fresh seeded state
docker compose down -v
docker compose up -d
sleep 60
docker compose exec backend python seed_database.py
```

## Separate Servers (Recommended for Production)

### Demo Server
- **URL**: `demo.yourcompany.com`
- **Branch**: `demo-stable`
- **Data**: Test users, sample complaints
- **Reset**: Can reset anytime
- **Purpose**: Client demos, testing, training

### Production Server
- **URL**: `app.yourcompany.com`
- **Branch**: `main`
- **Data**: Real users, real complaints
- **Reset**: NEVER reset
- **Purpose**: Live application for actual MLAs

## Monitoring Both Environments

### Check Demo Status
```bash
# SSH to demo server
ssh demo.yourcompany.com

# Check status
cd /path/to/demo-deployment/janasamparka
docker compose ps
docker compose logs --tail 50
```

### Check Production Status
```bash
# SSH to production server
ssh app.yourcompany.com

# Check status
cd /path/to/production/janasamparka
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs --tail 50
```

## Demo Credentials Reference

Store these in a safe place for demos:

```
===========================================
DEMO LOGIN CREDENTIALS
===========================================

Moderators:
  Puttur:           +919900000000 / demo
  Mangalore North:  +919900000001 / demo
  Udupi:            +919900000002 / demo

Department Officers (Sample):
  PWD Puttur:       +9199001000 / demo
  Water Puttur:     +9199002000 / demo
  PWD Mangalore:    +9199001100 / demo
  
Auditors:
  Puttur:           +9199006000 / demo
  Mangalore North:  +9199006001 / demo
  Udupi:            +9199006002 / demo

Sample Complaints:
  Location: Puttur (16 complaints)
  Roads: BC Road, Market Road, Kadambar Circle, etc.
  Status: Mix of new, in_progress, resolved

===========================================
```

## Summary Checklist

- [ ] Commit all demo state changes
- [ ] Create `demo-stable` branch
- [ ] Tag as `v1.0.0-demo`
- [ ] Push branch and tag to remote
- [ ] Continue production work on `main`
- [ ] Deploy demo using `demo-stable` branch
- [ ] Deploy production using `main` branch
- [ ] Keep demo and production on separate servers
- [ ] Document demo credentials
- [ ] Setup monitoring for both

## Quick Commands Reference

```bash
# Deploy Demo
git checkout demo-stable && docker compose up -d && docker compose exec backend python seed_database.py

# Deploy Production  
git checkout main && docker compose -f docker-compose.production.yml up -d

# Reset Demo to Fresh State
docker compose down -v && docker compose up -d && docker compose exec backend python seed_database.py

# Update Demo (bug fixes only)
git checkout demo-stable && git pull && docker compose up -d --build

# Update Production (regular)
git checkout main && git pull && docker compose -f docker-compose.production.yml up -d --build
```

## Success Criteria

✅ Demo branch never receives production features
✅ Production branch continues active development
✅ Demo can be deployed fresh anywhere in 5 minutes
✅ Demo can be reset to clean state anytime
✅ Production data is never lost
✅ Both environments can run simultaneously
✅ Demo always has working test credentials

---

**Next Steps:**
1. Run the git commands to create demo branch and tag
2. Push everything to remote
3. Test deploying demo on another machine/folder
4. Continue production development on main branch
