# Docker Keeps Stopping - Solution

## Problem
Docker Desktop keeps stopping automatically, causing the backend to become unavailable.

## Why This Happens
- Docker Desktop may be set to stop when idle
- System resources may be low
- Docker Desktop settings may need adjustment

## Permanent Solutions

### Solution 1: Keep Docker Desktop Running
1. **Open Docker Desktop** application
2. Go to **Settings** (gear icon)
3. Under **General**:
   - ✅ Enable "Start Docker Desktop when you log in"
   - ✅ Disable "Automatically check for updates"
4. Under **Resources**:
   - Increase Memory to at least 4GB
   - Increase CPUs to at least 2
5. Click **Apply & Restart**

### Solution 2: Run Backend Without Docker (Alternative)

If Docker keeps stopping, run the backend directly:

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://janasamparka:janasamparka123@localhost:5432/janasamparka_db"
export DEBUG=True

# Run the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then ngrok will connect to this instead.

### Solution 3: Use Keep-Alive Script

Create a script that monitors and restarts Docker:

```bash
#!/bin/bash
# save as: keep-docker-alive.sh

while true; do
    if ! docker info > /dev/null 2>&1; then
        echo "Docker stopped! Restarting..."
        open -a Docker
        sleep 30
    fi
    
    if ! docker ps | grep -q janasamparka_backend; then
        echo "Backend stopped! Restarting..."
        cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
        docker-compose up -d
    fi
    
    sleep 60  # Check every minute
done
```

Run it:
```bash
chmod +x keep-docker-alive.sh
./keep-docker-alive.sh &
```

## Immediate Fix

For now, manually restart Docker and backend:

```bash
# 1. Start Docker Desktop
open -a Docker
sleep 20

# 2. Start backend
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up -d

# 3. Verify it's running
docker ps | grep janasamparka
curl http://localhost:8000/

# 4. Test through ngrok
curl -H "ngrok-skip-browser-warning: true" \
  https://palindromic-amusively-karly.ngrok-free.dev/ | head -c 100
```

## Check Docker Status

```bash
# Is Docker running?
docker info

# Are containers running?
docker ps

# View backend logs
docker logs janasamparka_backend -f

# Restart backend if needed
docker-compose restart backend
```

## Why Docker Stops

Common reasons:
1. **Resource limits** - Docker runs out of memory
2. **Auto-sleep** - macOS puts Docker to sleep
3. **Updates** - Docker Desktop auto-updates
4. **Crashes** - Backend errors cause Docker to stop

## Recommended Action

**Right now:**
1. Keep Docker Desktop application **open and visible**
2. Don't minimize it
3. Monitor it while testing

**Long term:**
1. Adjust Docker Desktop settings (Solution 1)
2. Or run backend without Docker (Solution 2)
3. Or use keep-alive script (Solution 3)

---

**For immediate testing, let me restart Docker for you now...**
