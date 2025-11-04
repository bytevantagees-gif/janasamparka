# Mobile App Connection Test

## Current Setup Status

### ✅ Backend Running
- **URL**: http://192.168.29.35:8000
- **Status**: Running in Docker
- **Test**: `curl http://192.168.29.35:8000/` returns success

### ✅ Expo Server Running  
- **URL**: exp://192.168.29.35:8081
- **Status**: Running with Metro bundler

### ✅ Code Updated
- Added detailed error logging to login screen
- Errors will now show actual API response

## What to Do Now

### Step 1: Reload the App
1. **Shake your phone** or press the menu button in Expo Go
2. Select **"Reload"**
3. Or **scan the QR code again** for a fresh start

### Step 2: Try to Request OTP
1. Enter a 10-digit phone number (e.g., `9876543210`)
2. Tap "Request OTP"
3. **Look at the error message** - it will now show the actual error

### Step 3: Check Console Logs
The Metro bundler terminal will now show:
- `Requesting OTP for: +919876543210`
- Any error details from the API

## Common Issues & Solutions

### Issue 1: Network Error / Connection Refused
**Cause**: Phone can't reach the backend server

**Solutions**:
1. Verify both devices are on the **same WiFi network**
2. Check your computer's IP hasn't changed:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
3. If IP changed, update `/mobile-app/services/api.js`

### Issue 2: CORS Error
**Cause**: Backend not allowing requests from mobile app

**Solution**: Backend should already have CORS enabled for all origins in development

### Issue 3: Timeout
**Cause**: Firewall blocking port 8000

**Solution**: 
- Check macOS Firewall settings
- Temporarily disable to test

## Manual Test from Your Computer

Test if the backend is accessible from your network:

```bash
# Test from your computer
curl http://192.168.29.35:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

Expected response:
```json
{
  "message": "OTP sent successfully",
  "phone": "+919876543210", 
  "otp": "123456",
  "expires_in_minutes": 5
}
```

## View Backend Logs

To see OTP codes and any errors:

```bash
docker logs janasamparka_backend -f
```

## Next Steps

After you try requesting OTP again:
1. **Tell me the exact error message** you see
2. **Check if there are console logs** in the Metro bundler terminal
3. I can then fix the specific issue
