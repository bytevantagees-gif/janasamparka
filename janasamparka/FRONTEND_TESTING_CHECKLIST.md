# ✅ FRONTEND TESTING CHECKLIST

## 📋 **MANUAL TESTING GUIDE FOR UI**

**Prerequisites:**
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ Logged in with: +918242226666 / OTP: 123456

---

## 🎯 **PHASE 1: BASIC FUNCTIONALITY**

### **1. Dashboard Page** (/dashboard)
- [ ] Page loads without errors
- [ ] Statistics cards display correctly
- [ ] Total complaints count visible
- [ ] Status breakdown chart renders
- [ ] Recent complaints list shows data
- [ ] All cards clickable (if applicable)

**Expected:** Dashboard shows overview of all complaints

---

### **2. Constituencies Page** (/constituencies)
- [ ] List of constituencies displays
- [ ] Search functionality works
- [ ] Can click on constituency
- [ ] Constituency detail page loads
- [ ] Statistics show correctly
- [ ] Create constituency button visible (if admin)

**Expected:** Can view and navigate constituencies

---

### **3. Complaints List Page** (/complaints)
- [ ] All complaints list displays
- [ ] Status filters work (Submitted, Assigned, etc.)
- [ ] Category filters work (Road, Water, etc.)
- [ ] Search by title works
- [ ] Date range filter works
- [ ] Pagination works (if >10 complaints)
- [ ] Can click on complaint to view details
- [ ] "Create Complaint" button visible

**Expected:** Can filter and view all complaints

---

### **4. Complaint Detail Page** (/complaints/:id)
- [ ] Complaint details display correctly
- [ ] Title, description, status visible
- [ ] User information shows
- [ ] Location information displays
- [ ] Created/updated timestamps show
- [ ] Status badge shows correct color
- [ ] "Update Status" button works
- [ ] "Assign Department" button works
- [ ] "Upload Photos" button works
- [ ] Status history timeline displays
- [ ] Can navigate back to list

**Expected:** Full complaint details with actions

---

### **5. Create Complaint Page** (/complaints/new)
- [ ] Form loads correctly
- [ ] Title field validates (required)
- [ ] Description field validates (required)
- [ ] Category dropdown works
- [ ] Ward dropdown populated
- [ ] Location fields work
- [ ] GPS "Use My Location" button works
- [ ] Photo upload works
- [ ] "Submit" creates complaint
- [ ] Redirects to complaint detail after submit
- [ ] Validation errors show properly

**Expected:** Can create new complaint successfully

---

### **6. Update Status Modal**
- [ ] Modal opens when button clicked
- [ ] Current status shows
- [ ] New status dropdown works
- [ ] Note/comment field works
- [ ] "Update Status" submits
- [ ] Modal closes after submit
- [ ] Complaint status updates
- [ ] Success message displays
- [ ] Status log entry created

**Expected:** Can update complaint status

---

### **7. Assign Department Modal**
- [ ] Modal opens when button clicked
- [ ] Department dropdown populated
- [ ] Priority dropdown works
- [ ] Note field works
- [ ] "Assign" button submits
- [ ] Modal closes after assign
- [ ] Department shows in complaint detail
- [ ] Success message displays

**Expected:** Can assign complaint to department

---

### **8. Upload Photos Modal**
- [ ] Modal opens when button clicked
- [ ] Photo type dropdown works (Before/After/During/Evidence)
- [ ] File picker opens on click
- [ ] Can select multiple files
- [ ] Preview thumbnails show
- [ ] Can remove selected files
- [ ] Caption field works
- [ ] "Upload Photos" button submits
- [ ] Progress indicator shows
- [ ] Photos appear in complaint detail
- [ ] Success message displays

**Expected:** Can upload multiple photos

---

### **9. Departments Page** (/departments)
- [ ] List of departments displays
- [ ] Search works
- [ ] Filter by active status works
- [ ] Department cards show info
- [ ] "Add Department" button visible
- [ ] Can click to view details (if applicable)

**Expected:** Can view all departments

---

### **10. Department Create Modal**
- [ ] Modal opens from "Add Department" button
- [ ] Name field validates
- [ ] Code field validates
- [ ] Contact phone validates
- [ ] Contact email validates
- [ ] Head name field works
- [ ] Active checkbox works
- [ ] "Create" button submits
- [ ] Modal closes after create
- [ ] New department appears in list
- [ ] Success message displays

**Expected:** Can create new department

---

### **11. Wards Page** (/wards)
- [ ] List of wards displays
- [ ] Search works
- [ ] Filter by constituency works
- [ ] Ward cards show info
- [ ] "Add Ward" button visible
- [ ] Population data displays
- [ ] Area displays

**Expected:** Can view all wards

---

### **12. Ward Create Modal**
- [ ] Modal opens from "Add Ward" button
- [ ] Name field validates
- [ ] Ward number validates
- [ ] Taluk field works
- [ ] Constituency dropdown populated
- [ ] Population fields work (optional)
- [ ] Area field works (optional)
- [ ] "Create" button submits
- [ ] New ward appears in list
- [ ] Success message displays

**Expected:** Can create new ward

---

### **13. Polls Page** (/polls)
- [ ] List of polls displays
- [ ] Active/ended filters work
- [ ] Poll cards show question
- [ ] Vote distribution chart shows
- [ ] Leading option highlighted
- [ ] Total votes count shows
- [ ] "Create Poll" button visible
- [ ] Can click to view details

**Expected:** Can view all polls with results

---

### **14. Poll Create Modal**
- [ ] Modal opens from "Create Poll" button
- [ ] Title field validates
- [ ] Description field works
- [ ] Ward dropdown works (optional)
- [ ] Start date picker works
- [ ] End date picker works
- [ ] Can add poll options (2-6)
- [ ] Can remove poll options
- [ ] "Create Poll" button submits
- [ ] New poll appears in list
- [ ] Success message displays

**Expected:** Can create new poll with multiple options

---

### **15. Users Page** (/users)
- [ ] List of users displays
- [ ] Search works
- [ ] Filter by role works
- [ ] User cards show info
- [ ] "Add User" button visible
- [ ] Can see user status (active/inactive)

**Expected:** Can view all users

---

### **16. User Create Modal**
- [ ] Modal opens from "Add User" button
- [ ] Name field validates
- [ ] Phone field validates (+format)
- [ ] Role dropdown works
- [ ] Constituency dropdown works
- [ ] Ward dropdown works (optional)
- [ ] Locale preference dropdown works
- [ ] "Create" button submits
- [ ] New user appears in list
- [ ] Success message displays

**Expected:** Can create new user

---

### **17. Settings Page** (/settings)
- [ ] Page loads
- [ ] User profile info displays
- [ ] Can edit profile (if implemented)
- [ ] Settings options show
- [ ] Logout button works

**Expected:** Settings page accessible

---

### **18. Navigation & Layout**
- [ ] Sidebar navigation works
- [ ] All menu items clickable
- [ ] Active page highlighted
- [ ] Logo/branding displays
- [ ] User info in sidebar
- [ ] Logout button works
- [ ] Mobile menu works (if responsive)

**Expected:** Can navigate entire app

---

## 🚀 **PHASE 2: ADVANCED FEATURES**

### **19. Map View Page** (/map)
- [ ] Page loads without errors
- [ ] Map renders with tiles
- [ ] Complaint markers appear
- [ ] Markers color-coded by status
- [ ] Click marker shows popup
- [ ] Popup shows complaint info
- [ ] "View Details" in popup works
- [ ] Map auto-fits to show all markers
- [ ] Legend displays correctly
- [ ] Statistics overlay shows count

**Expected:** Interactive map with all complaints

---

### **20. Map Filters**
- [ ] "Filters" button opens panel
- [ ] Status filter works
- [ ] Category filter works
- [ ] Date from/to filters work
- [ ] "Apply Filters" updates map
- [ ] "Clear All" removes filters
- [ ] Filter count badge shows
- [ ] Map updates when filters applied

**Expected:** Can filter complaints on map

---

### **21. Map View Modes**
- [ ] View mode toggle buttons visible
- [ ] Markers view (📍) - Default
- [ ] Click heatmap icon (🔥)
- [ ] Heatmap layer appears
- [ ] Markers disappear in heatmap mode
- [ ] Red/yellow/blue gradient shows
- [ ] Click clusters icon (●●●)
- [ ] Markers group into clusters
- [ ] Cluster numbers show
- [ ] Click cluster zooms in
- [ ] Toggle back to markers works

**Expected:** All 3 view modes work smoothly

---

### **22. Before/After Photo Comparison**
- [ ] Visible in complaint detail (if photos exist)
- [ ] Before photo shows with red badge
- [ ] After photo shows with green badge
- [ ] Slider appears between photos
- [ ] Can drag slider left/right
- [ ] Smooth animation/transition
- [ ] Photos compare side-by-side
- [ ] Fullscreen button works
- [ ] Fullscreen mode works properly
- [ ] ESC or X closes fullscreen
- [ ] Photo metadata displays (date, caption)

**Expected:** Interactive photo comparison slider

---

### **23. Work Completion Approval**
- [ ] Section visible when after photos exist
- [ ] Shows "Pending Approval" status (yellow)
- [ ] "Approve Work" button visible
- [ ] Click "Approve Work"
- [ ] Modal/form opens
- [ ] Comments field validates (required)
- [ ] "Confirm Approval" button works
- [ ] Status changes to "Approved" (green)
- [ ] Approval comments display
- [ ] Approval timestamp shows
- [ ] Status log updated

**Expected:** MLA can approve completed work

---

### **24. Work Rejection**
- [ ] "Request Revision" button visible
- [ ] Click "Request Revision"
- [ ] Modal/form opens
- [ ] Reason field validates (required)
- [ ] "Request Revision" button works
- [ ] Status changes to "Rejected" (red)
- [ ] Complaint status reverts to "In Progress"
- [ ] Rejection reason displays
- [ ] Rejection timestamp shows
- [ ] Can re-approve after rejection

**Expected:** MLA can reject work and request redo

---

### **25. Map Refresh & Export**
- [ ] "Refresh" button works
- [ ] Loading spinner shows
- [ ] Map data updates
- [ ] "Export" button visible
- [ ] Export shows message (stub)

**Expected:** Map can be refreshed

---

## 🐛 **ERROR HANDLING**

### **26. Error Scenarios**
- [ ] Network error shows message
- [ ] Invalid form submission shows errors
- [ ] Required fields highlight red
- [ ] API errors show user-friendly messages
- [ ] 404 pages work
- [ ] Loading states show spinners
- [ ] Empty states show helpful messages
- [ ] Timeout errors handled

**Expected:** Graceful error handling

---

## 📱 **RESPONSIVE DESIGN**

### **27. Mobile Testing** (if applicable)
- [ ] App works on mobile (375px)
- [ ] App works on tablet (768px)
- [ ] Navigation collapses properly
- [ ] Forms are usable on mobile
- [ ] Maps work with touch
- [ ] Buttons properly sized
- [ ] Text readable on small screens

**Expected:** Responsive on all devices

---

## ⚡ **PERFORMANCE**

### **28. Performance Checks**
- [ ] Pages load in <3 seconds
- [ ] No console errors
- [ ] No console warnings (major)
- [ ] Images load properly
- [ ] Smooth animations
- [ ] No lag when typing
- [ ] Map renders smoothly
- [ ] Large lists paginate properly

**Expected:** Fast and smooth UX

---

## ✅ **COMPLETION CHECKLIST**

### **Phase 1 Basic Features:**
- [ ] Dashboard (1 test)
- [ ] Constituencies (1 test)
- [ ] Complaints List (1 test)
- [ ] Complaint Detail (1 test)
- [ ] Create Complaint (1 test)
- [ ] Update Status (1 test)
- [ ] Assign Department (1 test)
- [ ] Upload Photos (1 test)
- [ ] Departments (2 tests)
- [ ] Wards (2 tests)
- [ ] Polls (2 tests)
- [ ] Users (2 tests)
- [ ] Settings (1 test)
- [ ] Navigation (1 test)

**Phase 1 Total: 18 tests**

### **Phase 2 Advanced Features:**
- [ ] Map View (1 test)
- [ ] Map Filters (1 test)
- [ ] Map View Modes (1 test)
- [ ] Before/After Comparison (1 test)
- [ ] Work Approval (1 test)
- [ ] Work Rejection (1 test)
- [ ] Map Refresh (1 test)

**Phase 2 Total: 7 tests**

### **Additional Checks:**
- [ ] Error Handling (1 test)
- [ ] Responsive Design (1 test)
- [ ] Performance (1 test)

**Total Tests: 28**

---

## 📊 **TEST RESULTS TEMPLATE**

```
FRONTEND TESTING RESULTS
========================

Date: _______________
Tester: _______________
Environment: Development

Phase 1 Tests: __/18 passed
Phase 2 Tests: __/7 passed
Additional Tests: __/3 passed

Total: __/28 passed (__%)

Critical Issues Found:
1. _____________________
2. _____________________

Minor Issues Found:
1. _____________________
2. _____________________

Browser Tested:
[ ] Chrome
[ ] Firefox
[ ] Safari
[ ] Edge

Overall Status: [ PASS / FAIL ]

Notes:
_________________________________
_________________________________
```

---

## 🎯 **NEXT STEPS**

### **If All Tests Pass:**
✅ Frontend is production-ready  
✅ Can proceed to deployment  
✅ Start user training  

### **If Tests Fail:**
🐛 Document all failures  
🔧 Prioritize critical bugs  
🧪 Fix and retest  
📝 Update documentation  

---

**Testing Guide Version:** 1.0  
**Last Updated:** October 27, 2025  
**Status:** Ready for Manual Testing
