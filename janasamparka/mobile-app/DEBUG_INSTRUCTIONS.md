# How to See App Errors in Terminal

## Method 1: Use Expo's Remote Debugging

### On Your Android Phone:
1. **Shake the phone** to open Expo menu
2. Select **"Debug Remote JS"**
3. A Chrome browser tab will open
4. Press **F12** (or Cmd+Option+I on Mac) to open Chrome DevTools
5. Go to the **Console** tab
6. All errors will now appear in the browser console

## Method 2: Use React Native Debugger (Better)

### Install React Native Debugger:
```bash
brew install --cask react-native-debugger
```

### Use it:
1. Open React Native Debugger app
2. In Expo Go on phone: Shake → "Debug Remote JS"
3. All logs and errors will appear in React Native Debugger

## Method 3: Use adb logcat (Android Logs)

### If you have Android SDK installed:
```bash
# View all Android logs
adb logcat

# Filter for React Native errors
adb logcat | grep -i "ReactNativeJS"

# Filter for your app
adb logcat | grep -i "expo"
```

## Method 4: Take a Screenshot

### On Your Phone:
1. When you see the error
2. Take a screenshot
3. Send it to me

## What Errors Are You Seeing?

Please tell me:
1. **What is the exact error message** on your phone?
2. **When does it happen?** (On app load? When clicking Request OTP?)
3. **What color is the error?** (Red screen? Yellow warning?)

## Quick Test

Let me add a simple test to see if the app can reach the backend:

### On Your Phone:
1. Open the app
2. Before clicking anything, shake the phone
3. Look for any red error screens
4. Tell me what you see

---

**Please describe the error you're seeing on your phone, or take a screenshot!**
