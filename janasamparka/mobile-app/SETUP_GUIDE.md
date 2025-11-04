# 🚀 Janasamparka Mobile App - Complete Setup Guide

## 📱 Step-by-Step Setup Instructions

### Step 1: Install Expo Go on Your Phone

**Download from:**
- **Android**: https://play.google.com/store/apps/details?id=host.exp.exponent
- **iOS**: https://apps.apple.com/app/expo-go/id982107779

### Step 2: Configure Backend Connection

**IMPORTANT:** You must use your computer's IP address, NOT `localhost`!

#### Find Your IP Address:

**On Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Look for: inet 192.168.x.x
```

**On Windows:**
```bash
ipconfig
# Look for: IPv4 Address: 192.168.x.x
```

**On Linux:**
```bash
ip addr show
# Look for: inet 192.168.x.x
```

#### Update API URL:

Edit `mobile-app/services/api.js`:
```javascript
// Line 9: Replace with YOUR IP address
const API_URL = 'http://192.168.1.100:8000/api';
//                      ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
//                    YOUR IP HERE!
```

### Step 3: Start Backend (if not running)

```bash
# Navigate to project root
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka

# Start backend with Docker
docker-compose up
```

**Verify backend is running:**
- Open browser: `http://localhost:8000/docs`
- You should see FastAPI Swagger UI

### Step 4: Start Mobile App

```bash
# Navigate to mobile-app directory
cd /Users/srbhandary/Documents/Projects/MLA/janasamparka/mobile-app

# Start Expo dev server
npm start
```

**You should see:**
```
› Metro waiting on exp://192.168.x.x:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

### Step 5: Run on Your Phone

#### Android:
1. Open **Expo Go** app
2. Tap **"Scan QR Code"**
3. Scan the QR code from terminal
4. App will load!

#### iOS:
1. Open **Camera** app
2. Point at QR code from terminal
3. Tap notification to open in Expo Go
4. App will load!

---

## ✅ Testing Checklist

### 1. Login Screen Test
- [ ] App loads successfully
- [ ] Can toggle language (English ↔ ಕನ್ನಡ)
- [ ] Can enter phone number
- [ ] Can request OTP
- [ ] Receives OTP (check backend console)
- [ ] Can verify OTP and login

**Test Credentials:**
- Phone: `9876543210` (without +91)
- OTP: Check backend logs

### 2. Home Screen Test
- [ ] Shows welcome message
- [ ] Shows recent complaints
- [ ] Quick actions work
- [ ] Can navigate to other screens

### 3. Submit Complaint Test
- [ ] Can enter title
- [ ] Can enter description
- [ ] Can select category
- [ ] Can capture location (grant permission)
- [ ] Can take photo (grant permission)
- [ ] Can choose from gallery
- [ ] Can submit complaint
- [ ] Shows success message

### 4. Complaints List Test
- [ ] Shows all complaints
- [ ] Can filter by status
- [ ] Can click to view details
- [ ] Pull to refresh works

### 5. Map View Test
- [ ] Map loads
- [ ] Shows complaint markers
- [ ] Can click markers
- [ ] Shows complaint details

### 6. Profile Test
- [ ] Shows user info
- [ ] Can toggle language
- [ ] Can logout
- [ ] Language persists after restart

### 7. Complaint Detail Test
- [ ] Shows full details
- [ ] Shows images
- [ ] Shows timeline
- [ ] Shows location info

---

## 🔧 Common Issues & Solutions

### Issue: "Unable to connect to server"

**Solution:**
1. Check backend is running: `docker-compose up`
2. Verify API_URL uses your IP, not localhost
3. Phone and computer on same WiFi
4. Test in browser: `http://YOUR_IP:8000/docs`

### Issue: "Network request failed"

**Solution:**
1. Check firewall settings
2. Ensure port 8000 is open
3. Restart backend and mobile app
4. Try different WiFi network

### Issue: Camera permission denied

**Solution:**
1. Go to phone Settings → Apps → Expo Go
2. Enable Camera permission
3. Restart app

### Issue: Location permission denied

**Solution:**
1. Go to phone Settings → Apps → Expo Go
2. Enable Location permission
3. Enable "Location Services" on phone
4. Restart app

### Issue: QR code won't scan

**Solution:**
1. Make sure Expo Go is updated
2. Try manual connection:
   - In Expo Go, tap "Enter URL manually"
   - Enter: `exp://YOUR_IP:8081`
3. Restart dev server: `npm start -c` (clears cache)

### Issue: App crashes on startup

**Solution:**
1. Clear Expo cache: `npx expo start -c`
2. Clear phone's Expo Go cache
3. Reinstall Expo Go
4. Check for errors in terminal

---

## 🎯 Production Build Steps

### For Android APK

```bash
# 1. Install EAS CLI globally
npm install -g eas-cli

# 2. Login to Expo account (create free account if needed)
eas login

# 3. Configure project
eas build:configure

# 4. Build APK (can install directly on Android)
eas build --platform android --profile preview

# Download APK and install on Android phone
```

### For iOS IPA (requires Apple Developer account)

```bash
# Build for iOS
eas build --platform ios --profile preview

# Note: iOS builds require Apple Developer account ($99/year)
```

---

## 📊 App Architecture

```
┌─────────────────────────────────────────┐
│         React Native (Expo)              │
├─────────────────────────────────────────┤
│  Expo Router (File-based Navigation)    │
├─────────────────────────────────────────┤
│  React Query (Data Management)          │
├─────────────────────────────────────────┤
│  Axios (HTTP Client)                    │
├─────────────────────────────────────────┤
│  AsyncStorage (Local Persistence)       │
└─────────────────────────────────────────┘
            ↓ HTTP API ↓
┌─────────────────────────────────────────┐
│     FastAPI Backend (Port 8000)         │
└─────────────────────────────────────────┘
            ↓ Database ↓
┌─────────────────────────────────────────┐
│     PostgreSQL + PostGIS                │
└─────────────────────────────────────────┘
```

---

## 📝 Feature Checklist

### Implemented ✅
- [x] OTP-based authentication
- [x] Submit complaints with photos
- [x] GPS location capture
- [x] View complaints list
- [x] Filter complaints by status
- [x] View complaint details
- [x] Map view with markers
- [x] Bilingual (English/Kannada)
- [x] User profile
- [x] Logout functionality
- [x] Pull to refresh
- [x] Status timeline
- [x] Category filtering

### Future Enhancements 🚀
- [ ] Push notifications
- [ ] Offline mode
- [ ] Voice input for complaints
- [ ] Share complaint to social media
- [ ] Dark mode
- [ ] Complaint search
- [ ] Rate resolved complaints
- [ ] File attachments (PDF, docs)
- [ ] Video recording
- [ ] Nearby complaints
- [ ] Analytics dashboard

---

## 🎨 Customization

### Change App Colors

Edit color values in screen files:

```javascript
// Primary Blue: #3B82F6
// Success Green: #10B981
// Warning Orange: #F59E0B
// Danger Red: #EF4444
// Purple: #8B5CF6
```

### Change App Name

Edit `app.json`:
```json
{
  "expo": {
    "name": "Your App Name",
    "slug": "your-app-slug"
  }
}
```

### Add App Icon

1. Create 1024x1024 PNG icon
2. Save as `assets/icon.png`
3. Rebuild app

### Add Splash Screen

1. Create 1242x2436 PNG
2. Save as `assets/splash-icon.png`
3. Update `app.json` splash config

---

## 📞 Support & Debugging

### View Logs

**In Terminal:**
- Shows network requests
- Shows errors
- Shows console.log output

**On Phone:**
- Shake device to open dev menu
- Tap "Debug Remote JS"
- Open Chrome DevTools

### Reset Everything

```bash
# Clear all caches
npx expo start -c

# Reset node modules
rm -rf node_modules package-lock.json
npm install

# Reset Expo Go cache on phone
# Open Expo Go → Settings → Clear Cache
```

---

## 🎓 Learning Resources

- **Expo Docs**: https://docs.expo.dev
- **React Native**: https://reactnative.dev
- **React Query**: https://tanstack.com/query
- **Expo Router**: https://docs.expo.dev/router/introduction

---

## ✨ You're Ready!

1. ✅ Backend running on port 8000
2. ✅ Mobile app configured with your IP
3. ✅ Expo Go installed on phone
4. ✅ Same WiFi network

**Run:** `npm start` → Scan QR → Test!

---

**Need help?** Check troubleshooting section above or review README.md
