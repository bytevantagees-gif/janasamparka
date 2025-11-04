# 📱 Janasamparka Mobile App

A React Native mobile application for citizens to submit and track civic complaints in Karnataka constituencies.

## 🎯 Features

### Core Features
- ✅ **OTP-based Login** - Secure phone number authentication
- ✅ **Submit Complaints** - With camera, GPS location, and multiple images
- ✅ **Track Complaints** - Real-time status updates and timeline
- ✅ **Map View** - Visual representation of all complaints
- ✅ **Bilingual Support** - English and Kannada (ಕನ್ನಡ)
- ✅ **Profile Management** - User details and preferences

### Technical Features
- React Native with Expo
- Expo Router for navigation
- React Query for data management
- AsyncStorage for local persistence
- Real-time location tracking
- Camera integration
- Maps integration

## 📋 Prerequisites

Before you begin, ensure you have installed:
- **Node.js** (v16 or higher)
- **npm** or **yarn**
- **Expo Go** app on your phone:
  - [Android - Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
  - [iOS - App Store](https://apps.apple.com/app/expo-go/id982107779)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd mobile-app
npm install
```

### 2. Configure Backend URL

Edit `services/api.js` and update the API_URL:

```javascript
// Replace with your computer's IP address (not localhost!)
const API_URL = 'http://192.168.1.100:8000/api';
```

**How to find your IP:**
- **Mac**: `ifconfig | grep "inet " | grep -v 127.0.0.1`
- **Windows**: `ipconfig` (look for IPv4 Address)
- **Linux**: `ip addr show`

### 3. Start the Development Server

```bash
npm start
```

or

```bash
npx expo start
```

### 4. Run on Your Phone

1. **Open Expo Go** app on your phone
2. **Scan the QR code** displayed in terminal
   - **Android**: Use Expo Go app camera
   - **iOS**: Use Camera app (it will open Expo Go)
3. **App will load** on your phone!

## 📱 Testing the App

### Test Users (from backend)

**All users use OTP: `123456`**

See **[../TEST_LOGIN_CREDENTIALS.md](../TEST_LOGIN_CREDENTIALS.md)** for complete list of 29 test users.

**Quick Test Logins:**
- **Admin**: `+919999999999` (all constituencies)
- **Puttur MLA**: `+918242226666` (Ashok Kumar Rai)
- **Mangalore MLA**: `+918242227777` (B.A. Mohiuddin Bava)
- **Udupi MLA**: `+918252255555` (Yashpal A. Suvarna)
- **Puttur Citizen**: `+918242226301` (for testing citizen features)
- **Mangalore Citizen**: `+918242227301` (for testing citizen features)
- **Udupi Citizen**: `+918252255301` (for testing citizen features)

### Test Flow
1. **Login** with phone number
2. **Request OTP** (check backend logs for OTP)
3. **Submit a complaint**:
   - Fill in title and description
   - Select category
   - Capture location (allow permission)
   - Take photos (allow permission)
   - Submit
4. **Track complaints** in "My Complaints" tab
5. **View on map** in "Map" tab
6. **Toggle language** in Profile tab

## 📁 Project Structure

```
mobile-app/
├── app/                    # Expo Router screens
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── home.js        # Home screen
│   │   ├── complaints.js  # Complaints list
│   │   ├── submit.js      # Submit complaint
│   │   ├── map.js         # Map view
│   │   └── profile.js     # User profile
│   ├── complaint/         # Complaint detail
│   │   └── [id].js        # Dynamic route for complaint ID
│   ├── index.js           # Login screen
│   └── _layout.js         # Root layout
├── contexts/              # React contexts
│   ├── AuthContext.js     # Authentication state
│   └── LanguageContext.js # Language state
├── services/              # API services
│   └── api.js             # API client
├── locales/               # Translations
│   └── translations.js    # English & Kannada
└── app.json               # Expo configuration
```

## 🌐 API Configuration

The app connects to your backend API. Make sure:

1. **Backend is running**: `docker-compose up`
2. **Port 8000 is accessible** from your phone
3. **Firewall allows connections** on port 8000
4. **Same WiFi network** - Phone and computer must be on same network

### Test Backend Connection

```bash
# From your phone's browser, visit:
http://YOUR_IP:8000/docs

# If this works, the app will work!
```

## 🎨 Screens

### 1. Login Screen
- Phone number input
- OTP verification
- Language toggle

### 2. Home Screen
- Welcome message
- Quick actions (Submit, Track, Map)
- Recent complaints

### 3. Submit Complaint Screen
- Title and description
- Category selection
- GPS location capture
- Camera integration
- Image gallery picker

### 4. Complaints List Screen
- Filter by status
- View all user's complaints
- Click to see details

### 5. Map Screen
- Visual map of all complaints
- Color-coded by status
- Click markers for details

### 6. Profile Screen
- User information
- Language preference
- Logout

### 7. Complaint Detail Screen
- Full complaint details
- Status timeline
- Images
- Location
- Department assignment

## 🌍 Bilingual Support

The app fully supports:
- **English** - Default
- **ಕನ್ನಡ (Kannada)** - Toggle in Profile

All UI elements are translated:
- Navigation labels
- Form fields
- Buttons
- Messages
- Error messages
- Status labels

## 📷 Permissions

The app requires these permissions:

### Android
- Camera
- Location (Fine & Coarse)
- Storage (Read & Write)

### iOS
- Camera
- Photo Library
- Location (When In Use)

Permissions are requested when needed with proper explanations.

## 🔧 Troubleshooting

### App won't load on phone
- ✅ Check same WiFi network
- ✅ Restart Expo dev server: `npm start`
- ✅ Clear Expo cache: `npx expo start -c`

### Can't connect to backend
- ✅ Check API_URL in `services/api.js`
- ✅ Use IP address, not localhost
- ✅ Backend must be running
- ✅ Check firewall settings

### Camera not working
- ✅ Grant camera permission
- ✅ Restart app after granting permission
- ✅ Check app.json permissions config

### Location not working
- ✅ Grant location permission
- ✅ Enable location services on phone
- ✅ Restart app

### OTP not received
- ✅ Check backend logs for OTP
- ✅ Backend may not send actual SMS (check console)

## 🏗️ Building for Production

### Android APK

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure build
eas build:configure

# Build APK
eas build --platform android --profile preview
```

### iOS IPA (requires Mac)

```bash
# Build for iOS
eas build --platform ios --profile preview
```

### Alternative: Create standalone builds

```bash
# For local Android build (needs Android Studio)
npx expo run:android

# For local iOS build (needs Mac + Xcode)
npx expo run:ios
```

## 📦 Dependencies

### Core
- `expo` - Expo framework
- `expo-router` - File-based routing
- `react-native` - React Native framework

### Navigation & State
- `@react-navigation/native` - Navigation (via Expo Router)
- `@tanstack/react-query` - Data fetching & caching

### Device Features
- `expo-location` - GPS location
- `expo-image-picker` - Camera & Gallery
- `react-native-maps` - Map view

### Storage & Network
- `@react-native-async-storage/async-storage` - Local storage
- `axios` - HTTP client

### UI Components
- `@expo/vector-icons` - Icons
- `@react-native-picker/picker` - Dropdown picker

## 🎯 Next Steps

1. **Test on real device** - Use Expo Go
2. **Update API URL** - Point to your backend
3. **Test all features** - Login, submit, track
4. **Customize branding** - Update colors, logo
5. **Build for production** - Create APK/IPA

## 📝 Environment Variables

Create `.env` file for configuration:

```env
API_URL=http://192.168.1.100:8000/api
GOOGLE_MAPS_API_KEY=your_api_key_here
```

## 🆘 Support

For issues or questions:
1. Check troubleshooting section
2. Review backend logs
3. Check Expo documentation: https://docs.expo.dev
4. Check React Native docs: https://reactnative.dev

## 📄 License

© 2025 Janasamparka. All rights reserved.

---

**Ready to test!** 🚀

Start the app: `npm start`
Scan QR code with Expo Go
Login and start submitting complaints!
