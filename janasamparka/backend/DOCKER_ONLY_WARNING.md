# ⚠️ CRITICAL: DOCKER-ONLY APPLICATION ⚠️

## THIS APPLICATION ONLY RUNS IN DOCKER

**DO NOT attempt to run the backend outside of Docker containers.**

## Why Docker Only?

1. **Database Isolation**: The PostgreSQL database (`janasamparka_db`) exists ONLY in the Docker container
2. **No External Dependencies**: No local PostgreSQL installation should be used
3. **Consistent Environment**: All dependencies, ports, and configurations are managed by Docker

## Correct Way to Run

### Start All Services
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
# Backend logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f db

# Frontend logs
docker-compose logs -f frontend
```

### Stop Services
```bash
docker-compose down
```

## What NOT To Do

❌ **NEVER run these commands:**
```bash
# DON'T DO THIS - Backend outside Docker
cd backend
python -m uvicorn app.main:app

# DON'T DO THIS - Direct database connection
psql -h localhost -p 5432 -U janasamparka

# DON'T DO THIS - Activate venv and run
source .venv/bin/activate
python app/main.py
```

## Database Connection Details

### Inside Docker Container (Backend)
- Host: `db` (Docker service name)
- Port: `5432` (internal container port)
- URL: `postgresql://janasamparka:janasamparka123@db:5432/janasamparka_db`

### From Host Machine (for debugging only)
- Host: `localhost`
- Port: `5433` (mapped from container's 5432)
- URL: `postgresql://janasamparka:janasamparka123@localhost:5433/janasamparka_db`

## External PostgreSQL Servers

If you have PostgreSQL installed locally (e.g., PostgreSQL 18 at `/Library/PostgreSQL/18/`):

### ⚠️ STOP IT PERMANENTLY ⚠️

```bash
# Stop PostgreSQL service
sudo launchctl unload /Library/LaunchDaemons/com.edb.launchd.postgresql-18.plist

# Or use pg_ctl
sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl stop -D /Library/PostgreSQL/18/data

# Prevent auto-start on boot
sudo launchctl disable system/com.edb.launchd.postgresql-18
```

## Configuration Files

### backend/app/core/config.py
- Default: `localhost:5433` (Docker mapped port)
- Used when running scripts outside Docker (seed scripts, etc.)

### backend/.env
- Default: `localhost:5433` (Docker mapped port)
- Loaded by config.py when outside Docker

### docker-compose.yml (backend service)
- Override: `DATABASE_URL=postgresql://janasamparka:janasamparka123@db:5432/janasamparka_db`
- Used when backend runs inside Docker container

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5433 (psql access from host)

## Troubleshooting

### "Connection refused" errors
1. Verify containers are running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Restart containers: `docker-compose restart backend db`

### "Database does not exist"
1. Check database exists: `docker-compose exec db psql -U janasamparka -l`
2. Create if needed: `docker-compose exec db psql -U janasamparka -c "CREATE DATABASE janasamparka_db;"`

### "Port already in use"
1. Check what's using the port: `lsof -i :8000` or `lsof -i :3000`
2. Kill the process or change Docker port mapping

## Security Notes

1. ✅ Database only accessible via Docker network
2. ✅ No external PostgreSQL can interfere
3. ✅ Port 5433 mapped for debugging only
4. ✅ All data persists in Docker volume `postgres_data`

## Data Persistence

- Database data: Docker volume `postgres_data`
- View volumes: `docker volume ls`
- Inspect volume: `docker volume inspect janasamparka_postgres_data`
- Backup volume: `docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data`

---

**Remember:** This application is designed to run entirely within Docker. Running it outside Docker will cause connection errors and inconsistent behavior.
