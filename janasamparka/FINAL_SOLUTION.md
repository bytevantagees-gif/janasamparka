# 🔴 Expo Go HTTP Limitation - Final Solution

## Problem Summary
- ✅ Backend is running and accessible
- ✅ Chrome browser on Android can access `http://192.168.29.35:8000`
- ❌ Expo Go app shows "Network request failed"
- ❌ Both axios and fetch fail with the same error

## Root Cause
**Expo Go has strict network security policies that block HTTP requests on Android**, even when the device browser allows them. This is a known limitation of Expo Go, not your code or network.

### Why Chrome Works But Expo Go Doesn't:
- **Chrome**: System app with special permissions
- **Expo Go**: Sandboxed app with restricted network access
- **HTTP blocking**: Expo Go enforces stricter security than the browser

## Solutions (Choose One)

### ✅ Solution 1: Create Development Build (RECOMMENDED)

This creates a standalone APK with your app that has full network permissions.

```bash
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/mobile-app

# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure the project
eas build:configure

# Build for Android (development)
eas build --profile development --platform android
```

**Advantages:**
- Full network access (HTTP works)
- All native modules work
- Better for testing
- Closer to production

**Time**: ~15-20 minutes for first build

### ✅ Solution 2: Use HTTPS Backend (QUICK FIX)

Use ngrok to create an HTTPS tunnel to your backend:

```bash
# Install ngrok
brew install ngrok

# Create tunnel
ngrok http 8000
```

You'll get an HTTPS URL like: `https://abc123.ngrok.io`

Then update `/mobile-app/services/api-fetch.js`:
```javascript
const API_URL = 'https://abc123.ngrok.io/api';  // ← Change this
```

**Advantages:**
- Works immediately with Expo Go
- No build required
- HTTPS is secure

**Disadvantages:**
- URL changes each time
- Requires ngrok running
- Free tier has limitations

### ✅ Solution 3: Test on iOS (If Available)

iOS Expo Go has less strict HTTP restrictions:

```bash
npx expo start
# Scan QR code with iPhone
```

### ✅ Solution 4: Use Android Emulator

Android Emulator has different network stack:

```bash
# Start Android emulator
npx expo start --android
```

Emulator can access `http://10.0.2.2:8000` (your computer's localhost)

## Recommended Approach

### For Immediate Testing: Use ngrok (Solution 2)

**Step 1**: Install and run ngrok
```bash
brew install ngrok
ngrok http 8000
```

**Step 2**: Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

**Step 3**: Update API URL
```bash
# Edit this file:
nano /Users/srbhandary/Documents/Projects/MLA/janasamparka/mobile-app/services/api-fetch.js

# Change line 4 to:
const API_URL = 'https://YOUR-NGROK-URL.ngrok.io/api';
```

**Step 4**: Reload the app
- Shake phone → Reload
- Try requesting OTP

### For Long-term Development: Create Development Build (Solution 1)

This is the proper way to develop and test React Native apps.

## Why This Happened

### Expo Go Limitations:
1. **Pre-built binary**: Expo Go is a pre-built app, not your custom app
2. **Security restrictions**: Has strict network policies
3. **HTTP blocking**: Android 9+ blocks cleartext traffic
4. **No custom config**: Can't modify AndroidManifest.xml

### Development Build Benefits:
1. **Your custom app**: Built specifically for your project
2. **Full permissions**: Can configure network access
3. **All features**: Native modules, custom config
4. **Production-like**: Closer to final APK

## Quick Start with ngrok

```bash
# Terminal 1: Start backend
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka
docker-compose up

# Terminal 2: Start ngrok
ngrok http 8000
# Copy the https URL

# Terminal 3: Update and start Expo
cd mobile-app
# Edit services/api-fetch.js with ngrok URL
npx expo start

# Phone: Scan QR code and test
```

## Summary

| Solution | Time | Difficulty | Works with Expo Go | Recommended |
|----------|------|------------|-------------------|-------------|
| Development Build | 20 min | Medium | No (own app) | ✅ Yes (best) |
| ngrok HTTPS | 5 min | Easy | ✅ Yes | ✅ Yes (quick) |
| iOS Testing | 0 min | Easy | ✅ Yes | If available |
| Android Emulator | 5 min | Easy | ✅ Yes | Alternative |

## Next Steps

**Choose your solution:**

1. **Quick test now**: Use ngrok (5 minutes)
2. **Proper development**: Create development build (20 minutes)
3. **Alternative**: Test on iOS or Android emulator

Let me know which solution you'd like to proceed with, and I'll guide you through it!
