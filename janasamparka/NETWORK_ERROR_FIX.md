# Network Error Fix - Mobile App Cannot Reach Backend

## Problem Identified
Your phone shows: **"Network Error"** when trying to request OTP.

This means your Android phone **cannot connect** to the backend server at `http://192.168.29.35:8000`

## Root Causes & Solutions

### Issue 1: Docker Keeps Stopping ⚠️
**Problem**: Docker Desktop keeps shutting down automatically
**Impact**: Backend API becomes unavailable

**Solution**: Keep Docker Desktop running
1. Open **Docker Desktop** application
2. In Docker Desktop preferences:
   - Go to **Settings** → **General**
   - Enable **"Start Docker Desktop when you log in"**
   - Disable **"Automatically check for updates"** (prevents restarts)
3. Keep the Docker Desktop window open while testing

### Issue 2: macOS Firewall Blocking Port 8000
**Problem**: macOS firewall may be blocking incoming connections on port 8000

**Solution**: Allow incoming connections
```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# If enabled, add exception for Docker
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Docker.app/Contents/MacOS/Docker
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /Applications/Docker.app/Contents/MacOS/Docker
```

Or manually:
1. Open **System Settings** → **Network** → **Firewall**
2. Click **Options**
3. Find **Docker** and set to **Allow incoming connections**
4. Or temporarily **turn off firewall** to test

### Issue 3: WiFi Network Isolation
**Problem**: Some WiFi routers have "AP Isolation" or "Client Isolation" enabled

**Solution**: Check router settings
1. Your phone and computer must be on **same WiFi network**
2. Check if your router has "AP Isolation" or "Guest Network" mode enabled
3. Try connecting both devices to a **different WiFi network** or **mobile hotspot**

### Issue 4: Backend Not Listening on Network Interface
**Problem**: Backend only listening on localhost, not on network IP

**Solution**: Verify backend is accessible from network
```bash
# Test from your computer (should work)
curl http://localhost:8000/

# Test from network IP (this is what your phone uses)
curl http://192.168.29.35:8000/
```

If the second command fails, the backend isn't listening on the network interface.

## Quick Fix Steps

### Step 1: Ensure Docker is Running
```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
./keep-backend-running.sh
```

Keep this terminal open!

### Step 2: Test Backend from Computer
```bash
# Should return: {"app":"Janasamparka API",...}
curl http://192.168.29.35:8000/

# Should return OTP response
curl -X POST http://192.168.29.35:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

### Step 3: Test from Your Phone's Browser
On your Android phone:
1. Open **Chrome** or any browser
2. Go to: `http://192.168.29.35:8000/`
3. You should see: `{"app":"Janasamparka API",...}`

**If this works**: The issue is in the mobile app code
**If this fails**: Network/firewall issue

### Step 4: Temporary Firewall Bypass (Testing Only)
```bash
# Disable firewall temporarily
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Test the app

# Re-enable firewall after testing
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

## Alternative: Use Tunnel Mode

If network issues persist, use Expo's tunnel mode:

### In mobile-app directory:
```bash
# Stop current server
# Press Ctrl+C

# Start with tunnel
npx expo start --tunnel
```

This creates a public URL that works even with network restrictions.

Then update `api.js`:
```javascript
// Change from:
const API_URL = 'http://192.168.29.35:8000/api';

// To the tunnel URL (shown in terminal):
const API_URL = 'https://your-tunnel-url.ngrok.io/api';
```

## Verify Everything is Working

Run this complete test:
```bash
# 1. Check Docker
docker ps | grep janasamparka

# 2. Check backend on localhost
curl http://localhost:8000/

# 3. Check backend on network IP
curl http://192.168.29.35:8000/

# 4. Test OTP endpoint
curl -X POST http://192.168.29.35:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

All four should succeed!

## Next Steps

1. **Keep Docker Desktop running** - Don't close it
2. **Test backend from phone's browser** - Visit `http://192.168.29.35:8000/`
3. **If browser works but app doesn't** - It's an app issue (unlikely)
4. **If browser doesn't work** - It's a network/firewall issue

Let me know which test fails and I'll provide the specific fix!
