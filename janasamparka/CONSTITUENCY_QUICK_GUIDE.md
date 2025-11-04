# 🎯 Quick Guide: Constituency Selection for Citizens

## ✨ What's New?

Citizens can now **select their constituency** once during login, and it's **saved permanently**! They can also change it later in Settings.

---

## 🚀 Quick Test (2 Minutes)

### Step 1: Login as New Citizen

```bash
1. Go to http://localhost:5173/login
2. Phone: +919988770001
3. OTP: 123456
4. Click "Verify & Login"
```

### Step 2: Select Constituency

You'll see a beautiful page with:
- 🏛️ List of constituencies (Puttur, Mangalore, Bantwal)
- 📊 Details: Wards, Population
- ✨ Click any constituency card

### Step 3: Saved!

- ⚡ Automatic save
- 🚀 Redirect to your personalized dashboard
- ✅ Constituency remembered forever

---

## 🎨 Visual Flow

### First Login:
```
┌─────────────────────────────┐
│   📱 Enter Phone             │
│   +919988770001             │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   🔐 Enter OTP               │
│   123456                    │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   🏛️ Select Constituency     │
│                             │
│   [ Puttur    ]  ←Select   │
│   [ Mangalore ]             │
│   [ Bantwal   ]             │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   ✅ Citizen Dashboard        │
│   Showing Puttur data       │
└─────────────────────────────┘
```

### Next Login:
```
┌─────────────────────────────┐
│   📱 Enter Phone             │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   🔐 Enter OTP               │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   ✅ Dashboard (Direct!)      │
│   No selection needed       │
└─────────────────────────────┘
```

---

## 🛠️ Change Constituency Anytime

### In Settings:

1. **Go to Settings** (top right menu)
2. **Scroll to Profile section**
3. **See "Constituency" dropdown**
4. **Select new constituency**
5. **Click "Update Constituency"**
6. **Done!** ✅

---

## 🎯 Features

### Constituency Selector:
- ✅ Beautiful card-based UI
- ✅ Shows ward count & population
- ✅ Hover effects
- ✅ Loading spinner during save
- ✅ Error handling

### Settings Page:
- ✅ Dropdown for citizens only
- ✅ Shows current constituency
- ✅ Change anytime
- ✅ Instant save

---

## 🧪 Test Scenarios

### Scenario 1: First-Time Citizen ⭐
```
Phone: +919988770001
OTP: 123456
Result: See constituency selector → Select → Dashboard
```

### Scenario 2: Returning Citizen ⭐
```
Phone: +919988770001 (same as above)
OTP: 123456
Result: Skip selector → Direct to dashboard
```

### Scenario 3: Change Constituency ⭐
```
Login → Settings → Profile → Constituency dropdown
Select "Mangalore" → Update → Success!
```

### Scenario 4: Non-Citizen (Officer/MLA) ⭐
```
Login as Officer/MLA/Admin
Result: No constituency selector at login
Result: No constituency field in settings
```

---

## 💾 Data Persistence

### Where It's Saved:
```
Database: users.constituency_id (UUID)
LocalStorage: user.constituency_id
Context: AuthContext.user.constituency_id
```

### When It's Used:
- ✅ Filtering complaints on dashboard
- ✅ Showing relevant analytics
- ✅ Personalizing citizen experience
- ✅ Ward-level data display

---

## 📊 UI Components

### ConstituencySelector.jsx:
```jsx
Location: /components/ConstituencySelector.jsx
Features:
  - Full-page selector
  - Constituency cards
  - Auto-save on click
  - Error handling
  - Loading states
```

### Settings.jsx (Updated):
```jsx
Location: /pages/Settings.jsx
Added:
  - Constituency dropdown (citizens only)
  - Update button
  - Loading states
  - Success/error alerts
```

### Login.jsx (Updated):
```jsx
Location: /pages/Login.jsx
Added:
  - 'constituency' step
  - Conditional selector display
  - Auto-redirect after selection
```

---

## 🔍 How It Works

### Backend:
```python
PATCH /api/users/{user_id}
Body: { "constituency_id": "uuid-here" }
Response: { ...user, constituency_id: "uuid" }
```

### Frontend:
```javascript
// At login
if (user.role === 'citizen' && !user.constituency_id) {
  showConstituencySelector();
}

// In settings
await usersAPI.updateUser(user.id, {
  constituency_id: selectedConstituency
});
```

---

## ✅ Checklist

Before testing:
- [ ] Backend is running (`docker-compose up -d`)
- [ ] Frontend is running (`npm run dev`)
- [ ] Database has constituencies (Puttur, Mangalore, Bantwal)

Test:
- [ ] First-time citizen login → See selector
- [ ] Select constituency → Saved & redirected
- [ ] Second login → Skip selector
- [ ] Settings → Change constituency → Updated
- [ ] Non-citizen login → No selector

---

## 🎉 Benefits

### For Citizens:
✅ Only see relevant local complaints  
✅ Personalized dashboard  
✅ Set once, use forever  
✅ Easy to change if moving  

### For System:
✅ Better data organization  
✅ Accurate filtering  
✅ Constituency-level analytics  
✅ Improved user experience  

---

## 📞 Support

**Issue:** Selector not showing for citizens  
**Fix:** Check if user.constituency_id is null in database

**Issue:** Can't save constituency  
**Fix:** Verify backend API at `/api/users/{id}`

**Issue:** Dropdown empty in Settings  
**Fix:** Check constituencies API `/api/constituencies/`

---

**Status:** ✅ Ready to Test  
**Time to Test:** 2-3 minutes  
**Complexity:** Simple & Intuitive  
**Date:** October 30, 2025
