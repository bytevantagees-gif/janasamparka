# 🔐 Authentication System Guide

## ✅ What's Been Implemented

### **1. Auth Context (`AuthContext.jsx`)**
- Global authentication state management
- Token storage in localStorage
- User session persistence
- OTP request & verification functions
- Logout functionality

### **2. Login Page (`Login.jsx`)**
- Two-step OTP login flow:
  1. Enter phone number
  2. Verify OTP
- Development mode: OTP auto-displayed
- Quick test login buttons
- Beautiful UI with loading states
- Error handling

### **3. Protected Routes (`ProtectedRoute.jsx`)**
- Redirects unauthenticated users to `/login`
- Shows loading state while checking auth
- Wraps all authenticated pages

### **4. Updated Layout**
- Displays logged-in user info
- Shows user role (MLA, Admin, etc.)
- Logout button
- User avatar with initials

### **5. Updated App.jsx**
- AuthProvider wraps entire app
- Login route (public)
- All dashboard routes protected
- Automatic redirect to dashboard after login

---

## 🧪 Testing Authentication

### **Access the Login Page**
Open: http://localhost:3000/login

### **Test Users**

| User | Phone | Role | Constituency |
|------|-------|------|--------------|
| Ashok Kumar Rai | +918242226666 | MLA | Puttur |
| B.A. Mohiuddin Bava | +918242227777 | MLA | Mangalore North |
| Yashpal A. Suvarna | +918252255555 | MLA | Udupi |
| System Administrator | +919999999999 | Admin | All |
| Test Citizen | +919876543210 | Citizen | Puttur |

### **Login Flow**

**Step 1: Enter Phone Number**
1. Visit http://localhost:3000
2. You'll be redirected to `/login`
3. Enter phone number (e.g., +918242226666)
4. Click "Request OTP"

**Step 2: Verify OTP**
1. OTP will be displayed on screen (development mode)
2. It's auto-filled for you
3. Click "Verify & Login"
4. You'll be redirected to `/dashboard`

**Step 3: Explore Dashboard**
1. See your name and role in sidebar
2. Navigate between pages
3. All routes are protected

**Step 4: Logout**
1. Click "Logout" button in sidebar
2. You'll be redirected to `/login`
3. Session cleared from localStorage

---

## 🔑 How It Works

### **Authentication Flow**

```
┌─────────────┐
│ User visits │
│   /login    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Enter Phone Number  │
│ (+918242226666)     │
└──────┬──────────────┘
       │
       ▼
┌────────────────────────────┐
│ POST /api/auth/request-otp │
│ Returns OTP (dev mode)     │
└──────┬─────────────────────┘
       │
       ▼
┌─────────────────────┐
│   Enter OTP Code    │
│   (auto-filled)     │
└──────┬──────────────┘
       │
       ▼
┌────────────────────────────┐
│ POST /api/auth/verify-otp  │
│ Returns JWT + User Data    │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Store in localStorage:     │
│ - access_token             │
│ - refresh_token            │
│ - user data                │
└──────┬─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ Redirect to         │
│   /dashboard        │
└─────────────────────┘
```

### **Protected Route Flow**

```
User navigates to /dashboard
       │
       ▼
┌──────────────────┐
│ ProtectedRoute   │
│ checks auth      │
└────┬─────────────┘
     │
     ├─ Authenticated? ──YES──▶ Show Dashboard
     │
     └─ No? ──▶ Redirect to /login
```

### **Session Persistence**

```
Page Refresh
     │
     ▼
┌─────────────────────────┐
│ AuthContext loads       │
│ from localStorage:      │
│ - access_token          │
│ - user data             │
└─────┬───────────────────┘
      │
      ├─ Has token? ──YES──▶ User stays logged in
      │
      └─ No token? ──▶ User sees login page
```

---

## 📂 File Structure

```
admin-dashboard/src/
├── contexts/
│   └── AuthContext.jsx          # ✨ Auth state management
├── components/
│   ├── Layout.jsx               # ✅ Updated with user info
│   └── ProtectedRoute.jsx       # ✨ Route guard
├── pages/
│   ├── Login.jsx                # ✨ OTP login page
│   ├── Dashboard.jsx
│   ├── Constituencies.jsx
│   └── ...
├── services/
│   └── api.js                   # API client (already has authAPI)
└── App.jsx                      # ✅ Updated with auth routes
```

---

## 🔧 API Integration

The auth system uses these backend endpoints:

### **Request OTP**
```javascript
POST /api/auth/request-otp
Body: { "phone": "+918242226666" }
Response: {
  "message": "OTP sent successfully",
  "phone": "+918242226666",
  "otp": "123456",  // Only in development
  "expires_in_minutes": 5
}
```

### **Verify OTP**
```javascript
POST /api/auth/verify-otp
Body: { 
  "phone": "+918242226666",
  "otp": "123456"
}
Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "name": "Ashok Kumar Rai",
    "phone": "+918242226666",
    "role": "mla",
    "constituency_id": "..."
  }
}
```

---

## 🎨 UI Features

### **Login Page**
- ✅ Beautiful gradient background
- ✅ Kannada branding (ಜನಸಂಪರ್ಕ)
- ✅ Two-step OTP flow
- ✅ Loading states
- ✅ Error messages
- ✅ Quick test login buttons
- ✅ OTP auto-display in dev mode
- ✅ Resend OTP option

### **Protected Pages**
- ✅ User info in sidebar
- ✅ User avatar with initials
- ✅ Role display
- ✅ Logout button
- ✅ Auto-redirect if not authenticated

---

## 🔐 Security Features

### **Token Management**
- ✅ JWT access tokens
- ✅ Refresh tokens for session renewal
- ✅ Tokens stored in localStorage
- ✅ Tokens sent in Authorization header

### **Session Handling**
- ✅ Persistent sessions (survives page refresh)
- ✅ Clean logout (clears all tokens)
- ✅ Auto-redirect to login if not authenticated

### **Protected Routes**
- ✅ All dashboard routes require authentication
- ✅ Login page is public
- ✅ Automatic redirection

---

## 🎯 Next Steps

With authentication complete, you can now:

1. ✅ **Users can log in securely**
2. ✅ **Sessions persist across page refreshes**
3. ✅ **All routes are protected**
4. ✅ **User info displayed in UI**
5. ✅ **Logout functionality works**

### **Future Enhancements**
- [ ] Token refresh logic
- [ ] Remember me functionality
- [ ] Multi-factor authentication
- [ ] Session timeout warnings
- [ ] Password-based login option
- [ ] Role-based UI customization

---

## 🐛 Troubleshooting

### **Issue: Redirected to login immediately after logging in**
- Check browser console for errors
- Verify localStorage has `access_token`
- Check if token is valid

### **Issue: OTP not working**
- Ensure backend is running on port 8000
- Check network tab for API errors
- Verify phone number format (+91...)

### **Issue: User info not showing**
- Check if user data is in localStorage
- Verify AuthContext is wrapping App
- Check browser console for errors

---

## ✅ Summary

**Authentication is now fully functional!**

- 🔐 Secure OTP-based login
- 🛡️ Protected routes
- 👤 User session management
- 🚪 Logout functionality
- 💾 Session persistence

**Test it now:** http://localhost:3000

---

**Created:** October 27, 2025  
**Status:** ✅ Complete and Ready
