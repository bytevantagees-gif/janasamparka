# Mobile App Backend Setup Guide

## Issue
The mobile app shows "Failed to send OTP" because the backend API server is not running.

## Solution

### Step 1: Start Docker Desktop
1. Open **Docker Desktop** application on your Mac
2. Wait for Docker to fully start (the whale icon in the menu bar should be steady)

### Step 2: Start the Backend Services
Open a terminal and run:

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5433)
- FastAPI backend (port 8000)
- React frontend (port 3000)

### Step 3: Verify Backend is Running
```bash
curl http://192.168.29.35:8000/api/health
```

You should see a response like: `{"status":"ok"}`

### Step 4: Check Backend Logs
```bash
docker logs janasamparka_backend -f
```

Press `Ctrl+C` to stop viewing logs.

### Step 5: Test OTP Endpoint
```bash
curl -X POST http://192.168.29.35:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

## Quick Commands

### Start Backend
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up -d backend db
```

### Stop Backend
```bash
docker-compose down
```

### Restart Backend
```bash
docker-compose restart backend
```

### View Backend Logs
```bash
docker logs janasamparka_backend -f
```

## Mobile App Configuration

The mobile app is configured to connect to:
- **API URL**: `http://192.168.29.35:8000/api`
- **File**: `/mobile-app/services/api.js`

Make sure:
1. Your phone and computer are on the **same WiFi network**
2. The IP address `192.168.29.35` is your computer's current IP
3. No firewall is blocking port 8000

## Troubleshooting

### Check if backend is accessible
```bash
# From your computer
curl http://localhost:8000/api/health

# From your network (use your IP)
curl http://192.168.29.35:8000/api/health
```

### Check Docker containers
```bash
docker ps
```

You should see:
- `janasamparka_backend` (port 8000)
- `janasamparka_db` (port 5433)

### Restart everything
```bash
docker-compose down
docker-compose up -d
```

## Test Users

Once the backend is running, you can test with these phone numbers:
- `+919876543210` (Admin)
- `+919876543211` (Puttur MLA)
- `+919876543213` (Mangalore Moderator)

The OTP for testing is usually `123456` (check backend logs for the actual OTP).
