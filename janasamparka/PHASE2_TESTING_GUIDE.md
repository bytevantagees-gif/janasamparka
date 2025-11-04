# 🧪 PHASE 2 - COMPREHENSIVE TESTING GUIDE

## 📋 **TESTING CHECKLIST**

**Goal:** Test all Phase 2 features systematically  
**Duration:** ~2-3 hours  
**Prerequisites:** Backend and frontend running

---

## 🚀 **SETUP & PREPARATION**

### **Step 1: Install Dependencies**

#### **Frontend Dependencies:**
```bash
cd admin-dashboard

# Install new packages
npm install leaflet react-leaflet leaflet.heat leaflet.markercluster

# Verify installation
npm list | grep leaflet
```

**Expected Output:**
```
├── leaflet@1.9.4
├── leaflet.heat@0.2.0
├── leaflet.markercluster@1.5.3
└── react-leaflet@4.2.1
```

#### **Backend Dependencies:**
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install new packages
pip install shapely==2.0.2 geopy==2.4.1 faiss-cpu==1.7.4

# Verify installation
pip list | grep -E "shapely|geopy|faiss|sentence"
```

**Expected Output:**
```
faiss-cpu              1.7.4
geopy                  2.4.1
shapely                2.0.2
sentence-transformers  2.2.2
```

---

### **Step 2: Run Database Migrations**

```bash
cd backend

# Migration 1: Approval fields
psql -U your_user -d janasamparka -f migrations/add_approval_fields.sql

# Migration 2: PostGIS setup
psql -U your_user -d janasamparka -f migrations/setup_postgis.sql
```

**Expected Output:**
```
ALTER TABLE
ALTER TABLE
CREATE INDEX
CREATE FUNCTION
CREATE TRIGGER
...
```

**Verify Migration:**
```sql
-- Check approval fields
\d complaints

-- Check PostGIS
SELECT PostGIS_version();

-- Check functions
\df find_ward_from_coordinates
```

---

### **Step 3: Start Servers**

#### **Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Verify Backend:**
- Visit: http://localhost:8000/docs
- Should see 12 API router sections
- New sections: "Map", "AI & ML", "Bhoomi Land Records"

#### **Terminal 2 - Frontend:**
```bash
cd admin-dashboard
npm run dev
```

**Expected Output:**
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
```

**Verify Frontend:**
- Visit: http://localhost:3000
- Login with: +918242226666 / OTP: 123456
- See "Map View" in sidebar

---

## 🧪 **PHASE 2.1: BEFORE/AFTER PHOTO WORKFLOW**

### **Test 1: Upload Before Photos**

**Steps:**
1. Navigate to Complaints → Select any complaint
2. Click "Upload Photos" button
3. Select photo type: "Before"
4. Upload 1-2 images
5. Add caption: "Issue before repair"
6. Click "Upload Photos"

**Expected Result:**
✅ Success message appears  
✅ Photos visible in complaint detail  
✅ Photos tagged as "Before" with red badge

**Screenshot Location:** Before photos section

---

### **Test 2: Update Status to Resolved & Upload After Photos**

**Steps:**
1. Click "Update Status" button
2. Change status to "Resolved"
3. Add note: "Work completed"
4. Click "Update Status"
5. Click "Upload Photos" again
6. Select photo type: "After"
7. Upload 1-2 images
8. Add caption: "Issue after repair"
9. Click "Upload Photos"

**Expected Result:**
✅ Status changed to "Resolved"  
✅ After photos uploaded  
✅ Photos tagged as "After" with green badge

---

### **Test 3: Before/After Comparison Slider**

**Steps:**
1. Scroll to "Before/After Comparison" section
2. See side-by-side photos
3. Drag the slider left and right
4. Click fullscreen icon
5. Drag slider in fullscreen mode
6. Press ESC or click X to exit

**Expected Result:**
✅ Slider visible with before/after photos  
✅ Dragging smoothly compares photos  
✅ Fullscreen mode works  
✅ Slider position resets properly

**Visual Check:**
- Before photo: Red "Before" badge
- After photo: Green "After" badge
- Slider handle: White with arrows
- Smooth animation at 60 FPS

---

### **Test 4: MLA Work Approval**

**Steps:**
1. Scroll to "Work Completion Status" section
2. Should show "Pending Approval" in yellow
3. Click "Approve Work" button
4. Enter comments: "Excellent work. Quality approved."
5. Click "Confirm Approval"

**Expected Result:**
✅ Status changes to "Work Approved" (green)  
✅ Comments visible  
✅ Approval timestamp shown  
✅ Status log updated

**API Call Check:**
```bash
# In browser console
POST /api/complaints/{id}/approve
Status: 200 OK
```

---

### **Test 5: MLA Work Rejection**

**Steps:**
1. Navigate to another resolved complaint with after photos
2. Click "Request Revision" button
3. Enter reason: "Quality not satisfactory. Please redo."
4. Click "Request Revision"

**Expected Result:**
✅ Status changes to "Work Rejected" (red)  
✅ Complaint status reverts to "IN_PROGRESS"  
✅ Rejection reason visible  
✅ Department notified (in real app)

---

### **Test 6: Re-approval After Rejection**

**Steps:**
1. Upload new after photos
2. Click "Review Again & Approve"
3. Enter new comments
4. Click "Confirm Approval"

**Expected Result:**
✅ Can approve previously rejected work  
✅ New approval replaces old rejection  
✅ History maintained in status logs

---

## 🗺️ **PHASE 2.2: INTERACTIVE MAP**

### **Test 7: Navigate to Map Page**

**Steps:**
1. Click "Map View" in sidebar (🌍 icon)
2. Wait for map to load

**Expected Result:**
✅ Map page loads  
✅ All complaints appear as colored pins  
✅ Map auto-fits to show all complaints  
✅ Legend visible in bottom-left  
✅ Statistics overlay in top-right

**Visual Check:**
- Blue pins: Submitted complaints
- Yellow pins: Assigned complaints
- Purple pins: In Progress
- Green pins: Resolved
- Gray pins: Closed
- Red pins: Rejected

---

### **Test 8: Click Markers & View Popups**

**Steps:**
1. Click any complaint marker
2. Read popup content
3. Click "View Details" button

**Expected Result:**
✅ Popup appears with complaint info  
✅ Shows title, status, category, date  
✅ "View Details" navigates to complaint page  
✅ Popup closes when clicking map

---

### **Test 9: Apply Filters**

**Steps:**
1. Click "Filters" button
2. Select Status: "Resolved"
3. Select Category: "Road & Infrastructure"
4. Click "Apply Filters"

**Expected Result:**
✅ Map updates to show only filtered complaints  
✅ Pin count updates  
✅ "(filtered)" text appears  
✅ Badge shows active filter count

**Clear Filters:**
1. Click "Clear All"
2. Map shows all complaints again

---

### **Test 10: Refresh Map**

**Steps:**
1. Click "Refresh" button
2. Watch for loading spinner

**Expected Result:**
✅ Loading spinner appears  
✅ Map data refreshes  
✅ Pins update if data changed  
✅ Success feedback

---

### **Test 11: Date Range Filter**

**Steps:**
1. Open filters
2. Set "From Date": 7 days ago
3. Set "To Date": Today
4. Click "Apply Filters"

**Expected Result:**
✅ Shows only complaints from last 7 days  
✅ Older complaints hidden  
✅ Count reflects filter

---

## 🔥 **PHASE 2.4: HEATMAP & CLUSTERING**

### **Test 12: Toggle to Heatmap View**

**Steps:**
1. On map page, click heatmap icon (layers icon)
2. Wait for view to change

**Expected Result:**
✅ Individual markers disappear  
✅ Heatmap overlay appears  
✅ Red/yellow/blue gradient shows density  
✅ Hotspots clearly visible

**Visual Check:**
- Red areas: High complaint density
- Yellow areas: Medium density
- Blue areas: Low density
- Smooth gradient transitions

---

### **Test 13: Toggle to Cluster View**

**Steps:**
1. Click cluster icon (●●●)
2. Observe clustering

**Expected Result:**
✅ Nearby complaints group into clusters  
✅ Cluster circles show count  
✅ Clicking cluster zooms in  
✅ Zooming in breaks clusters apart

**Cluster Colors:**
- Small clusters (<10): Light color
- Medium clusters (10-50): Medium color
- Large clusters (>50): Dark color

---

### **Test 14: Toggle Back to Markers**

**Steps:**
1. Click marker icon (📍)
2. Return to normal view

**Expected Result:**
✅ Heatmap/clusters disappear  
✅ Individual markers return  
✅ Smooth transition  
✅ All data intact

---

### **Test 15: Test All View Modes with Filters**

**Steps:**
1. Apply status filter: "Resolved"
2. Toggle between all 3 view modes
3. Verify each mode respects filter

**Expected Result:**
✅ Markers view: Only resolved complaints  
✅ Heatmap view: Density of resolved complaints  
✅ Cluster view: Clusters of resolved complaints

---

## 🗄️ **PHASE 2.3: BACKEND API TESTING**

### **Test 16: GeoJSON Complaints Endpoint**

**Using Browser/Postman:**
```bash
GET http://localhost:8000/api/map/complaints
```

**Expected Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [75.2150, 12.7626]
      },
      "properties": {
        "id": "uuid",
        "title": "...",
        "status": "submitted",
        ...
      }
    }
  ],
  "metadata": {
    "count": 10,
    "filters": {}
  }
}
```

**Verify:**
✅ Valid GeoJSON format  
✅ All complaints included  
✅ Coordinates in [lng, lat] order  
✅ Metadata present

---

### **Test 17: Heatmap Data Endpoint**

```bash
GET http://localhost:8000/api/map/heatmap
```

**Expected Response:**
```json
{
  "data": [
    [12.7626, 75.2150, 1.0],
    [12.7630, 75.2160, 1.0]
  ],
  "metadata": {
    "count": 50,
    "intensity_field": "count"
  }
}
```

**Verify:**
✅ Array of [lat, lng, intensity]  
✅ Intensity values 0.0-1.0  
✅ Count matches complaints

---

### **Test 18: Complaint Clusters Endpoint**

```bash
GET http://localhost:8000/api/map/clusters?radius_km=1&min_complaints=3
```

**Expected Response:**
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "center": {"lat": 12.76, "lng": 75.21},
      "complaint_count": 5,
      "complaint_ids": ["uuid1", "uuid2", ...],
      "status_breakdown": {
        "submitted": 2,
        "resolved": 3
      }
    }
  ],
  "metadata": {
    "cluster_count": 3,
    "total_complaints": 50
  }
}
```

---

### **Test 19: PostGIS Ward Detection**

**If PostGIS is configured:**
```bash
GET http://localhost:8000/api/geocode/ward?lat=12.7626&lng=75.2150
```

**Expected Response (with PostGIS):**
```json
{
  "success": true,
  "ward_id": "uuid",
  "ward_name": "MG Road Ward",
  "ward_number": "1",
  "constituency_id": "uuid",
  "accuracy": "high"
}
```

**Expected Response (without PostGIS):**
```json
{
  "error": "Ward detection requires PostGIS",
  "status": 501,
  "detail": "Please select ward manually"
}
```

---

## 🤖 **PHASE 2.5: AI DUPLICATE DETECTION**

### **Test 20: Check for Duplicates**

**Using API Docs (http://localhost:8000/docs):**

1. Navigate to "AI & ML" section
2. Find `POST /api/ai/duplicate-check`
3. Click "Try it out"
4. Enter test data:

```json
{
  "title": "Road pothole near market",
  "description": "Large pothole causing traffic issues",
  "threshold": 0.85
}
```

5. Click "Execute"

**Expected Response:**
```json
{
  "is_duplicate": true,
  "duplicate_count": 2,
  "similar_complaints": [
    {
      "complaint_id": "uuid",
      "title": "Pothole on market road",
      "similarity_score": 0.92,
      "status": "in_progress",
      "created_at": "2025-10-20T..."
    }
  ],
  "threshold": 0.85,
  "message": "Potential duplicates found"
}
```

**Verify:**
✅ Similarity scores make sense  
✅ Similar complaints returned  
✅ Scores above threshold  
✅ Sorted by similarity

---

### **Test 21: Find Similar Complaints**

```bash
GET http://localhost:8000/api/ai/complaints/{complaint_id}/similar?limit=5
```

**Expected Response:**
```json
{
  "target_complaint_id": "uuid",
  "similar_count": 3,
  "similar_complaints": [
    {
      "complaint_id": "uuid2",
      "similarity_score": 0.88,
      ...
    }
  ]
}
```

---

### **Test 22: Test ML Model Loading**

**In Terminal (Backend):**
```bash
# Watch logs when calling duplicate-check
# Should see: "Loading sentence transformer model..."
# First call: ~5-10 seconds (model loading)
# Subsequent calls: <1 second (model cached)
```

**Performance Check:**
- First API call: 5-10s (model load)
- Subsequent calls: <1s
- Memory usage: +500MB (model in RAM)

---

## 🏘️ **PHASE 2.6: BHOOMI API INTEGRATION**

### **Test 23: RTC Lookup Endpoint**

```bash
GET http://localhost:8000/api/bhoomi/rtc?survey_number=123&village=Puttur
```

**Expected Response (Stub):**
```json
{
  "status": "stub",
  "message": "Bhoomi API integration pending",
  "data": {
    "survey_number": "123",
    "village": "Puttur",
    "owner_name": "[Data from Bhoomi API]"
  },
  "bhoomi_portal_link": "https://landrecords.karnataka.gov.in/...",
  "integration_status": {
    "api_available": false,
    "fallback": "manual_link"
  }
}
```

**Verify:**
✅ Stub response works  
✅ Portal link provided  
✅ Integration status clear  
✅ No errors

---

### **Test 24: All Bhoomi Endpoints**

Test each endpoint returns proper stub response:
- ✅ `GET /api/bhoomi/rtc`
- ✅ `GET /api/bhoomi/property/{id}`
- ✅ `POST /api/bhoomi/link-complaint`
- ✅ `GET /api/bhoomi/villages`
- ✅ `GET /api/bhoomi/search`

---

## 📊 **INTEGRATION TESTING**

### **Test 25: Complete Workflow Test**

**Scenario:** Full complaint lifecycle with all Phase 2 features

**Steps:**
1. Create new complaint with location
2. Upload before photos
3. Assign to department
4. Department updates to "In Progress"
5. Check for duplicate complaints (API)
6. View complaint on map
7. Toggle map views (markers/heatmap/clusters)
8. Department marks as "Resolved"
9. Upload after photos
10. View before/after comparison
11. MLA approves work
12. Verify on map (green pin)

**Duration:** ~10 minutes

**Expected Result:**
✅ All steps complete smoothly  
✅ No errors or crashes  
✅ Data persists correctly  
✅ UI updates in real-time

---

### **Test 26: Performance Testing**

**Test with 100+ Complaints:**

1. Create test data or import sample data
2. Load map with 100+ complaints
3. Measure load time
4. Toggle between view modes
5. Apply/remove filters

**Performance Targets:**
- Map initial load: <3 seconds
- View mode toggle: <500ms
- Filter application: <1 second
- Heatmap rendering: <1 second
- Cluster calculation: <2 seconds

---

### **Test 27: Mobile Responsiveness**

**Steps:**
1. Open map on mobile device or use browser DevTools
2. Test touch interactions
3. Test pinch-to-zoom
4. Test marker taps
5. Test filter panel

**Expected Result:**
✅ Map responsive on mobile  
✅ Touch gestures work  
✅ Popups readable  
✅ Filters accessible  
✅ UI elements not overlapping

---

## 🐛 **COMMON ISSUES & TROUBLESHOOTING**

### **Issue 1: Leaflet CSS Not Loading**

**Symptom:** Map tiles broken, controls missing

**Solution:**
```bash
# Check if leaflet installed
npm list leaflet

# Reinstall if needed
npm install --save leaflet

# Verify CSS import in component
import 'leaflet/dist/leaflet.css';
```

---

### **Issue 2: Marker Icons Not Showing**

**Symptom:** Markers appear as broken images

**Solution:**
Already fixed in `ComplaintMap.jsx`:
```javascript
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/...',
  ...
});
```

---

### **Issue 3: PostGIS Functions Not Found**

**Symptom:** Ward detection returns 500 error

**Solution:**
```sql
-- Verify PostGIS installed
SELECT PostGIS_version();

-- Re-run migration if needed
\i migrations/setup_postgis.sql

-- Check functions exist
\df find_ward_from_coordinates
```

---

### **Issue 4: AI Model Loading Fails**

**Symptom:** Duplicate check returns 500 error

**Solution:**
```bash
# Install sentence-transformers
pip install sentence-transformers

# Download model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"

# Check model cached (~500MB in ~/.cache/torch)
ls ~/.cache/torch/sentence_transformers/
```

---

### **Issue 5: Heatmap Not Rendering**

**Symptom:** Heatmap view shows nothing

**Solution:**
```bash
# Install leaflet.heat
npm install leaflet.heat

# Check import in HeatmapLayer.jsx
import 'leaflet.heat';

# Verify data format: [[lat, lng, intensity], ...]
```

---

## ✅ **TESTING COMPLETION CHECKLIST**

### **Phase 2.1: Before/After** (6 tests)
- [ ] Upload before photos
- [ ] Upload after photos
- [ ] View comparison slider
- [ ] Approve work
- [ ] Reject work
- [ ] Re-approve after rejection

### **Phase 2.2: Interactive Map** (5 tests)
- [ ] Navigate to map page
- [ ] Click markers & popups
- [ ] Apply filters
- [ ] Refresh map
- [ ] Date range filters

### **Phase 2.4: Heatmap & Clustering** (4 tests)
- [ ] Toggle to heatmap
- [ ] Toggle to clusters
- [ ] Toggle back to markers
- [ ] Test with filters

### **Phase 2.3: Backend APIs** (4 tests)
- [ ] GeoJSON endpoint
- [ ] Heatmap data endpoint
- [ ] Clusters endpoint
- [ ] Ward detection endpoint

### **Phase 2.5: AI Features** (3 tests)
- [ ] Duplicate detection
- [ ] Find similar complaints
- [ ] ML model loading

### **Phase 2.6: Bhoomi** (2 tests)
- [ ] RTC lookup stub
- [ ] All Bhoomi endpoints

### **Integration Tests** (3 tests)
- [ ] Complete workflow
- [ ] Performance testing
- [ ] Mobile responsiveness

**Total Tests:** 27

---

## 📝 **TEST RESULTS TEMPLATE**

```markdown
## PHASE 2 TEST RESULTS

**Date:** [Date]
**Tester:** [Name]
**Environment:** Development

### Summary
- Total Tests: 27
- Passed: __
- Failed: __
- Skipped: __

### Failed Tests
1. Test #__: [Name]
   - Issue: [Description]
   - Error: [Error message]
   - Fix: [What needs to be done]

### Performance Metrics
- Map load time: __ seconds
- View mode toggle: __ ms
- Duplicate detection: __ seconds
- Filter application: __ ms

### Browser Compatibility
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Device Testing
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (iPad)
- [ ] Mobile (iPhone/Android)

### Notes
[Any additional observations]
```

---

## 🎯 **NEXT STEPS AFTER TESTING**

### **If All Tests Pass:**
1. ✅ Mark Phase 2 as production-ready
2. ✅ Create deployment plan
3. ✅ Schedule pilot launch
4. ✅ Train users
5. ✅ Monitor in production

### **If Tests Fail:**
1. 🐛 Document all failures
2. 🔧 Prioritize fixes (critical first)
3. 🧪 Re-test after fixes
4. 📝 Update documentation
5. ✅ Repeat until all pass

---

## 📞 **QUICK REFERENCE**

### **URLs:**
- Frontend: http://localhost:3000
- Map View: http://localhost:3000/map
- API Docs: http://localhost:8000/docs
- Backend: http://localhost:8000

### **Login:**
- Phone: `+918242226666`
- OTP: `123456`

### **Sample API Calls:**
```bash
# Get complaints GeoJSON
curl http://localhost:8000/api/map/complaints

# Check for duplicates
curl -X POST http://localhost:8000/api/ai/duplicate-check \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Test desc","threshold":0.85}'

# Ward detection
curl http://localhost:8000/api/geocode/ward?lat=12.76&lng=75.21
```

---

**Testing Guide Version:** 1.0  
**Last Updated:** October 27, 2025  
**Status:** Ready for Testing  

**Happy Testing! 🧪🚀**
