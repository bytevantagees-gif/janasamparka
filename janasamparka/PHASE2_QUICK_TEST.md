# 🚀 PHASE 2 - QUICK TEST (10 Minutes)

## ⚡ **FASTEST WAY TO TEST EVERYTHING**

### **1. Setup (2 minutes)**

```bash
# Make script executable
chmod +x quick_test_phase2.sh

# Run setup script
./quick_test_phase2.sh
```

### **2. Start Servers (1 minute)**

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd admin-dashboard
npm run dev
```

### **3. Quick Tests (7 minutes)**

#### **Test 1: Map View (2 min)** ⭐
1. Go to http://localhost:3000
2. Login: `+918242226666` / OTP: `123456`
3. Click "Map View" in sidebar
4. ✅ See complaints as colored pins
5. ✅ Click a pin → popup appears
6. ✅ Click heatmap icon → see density
7. ✅ Click cluster icon → see clusters

**Pass if:** All 3 view modes work

---

#### **Test 2: Before/After Photos (3 min)** ⭐
1. Go to any complaint
2. Click "Upload Photos"
3. Select type: "Before" → upload image
4. Click "Update Status" → "Resolved"
5. Click "Upload Photos" again
6. Select type: "After" → upload image
7. ✅ See comparison slider
8. ✅ Drag slider left/right
9. Click "Approve Work" → add comments → submit
10. ✅ Status shows "Approved"

**Pass if:** Slider works, approval succeeds

---

#### **Test 3: API Endpoints (2 min)** ⭐
1. Go to http://localhost:8000/docs
2. Find "Map" section
3. Try: `GET /api/map/complaints`
4. ✅ See GeoJSON response
5. Find "AI & ML" section
6. Try: `POST /api/ai/duplicate-check`
7. Enter test data, execute
8. ✅ See similarity results

**Pass if:** Both APIs return 200 OK

---

## ✅ **PASS CRITERIA**

✅ **Test 1 Pass:** All 3 map views render  
✅ **Test 2 Pass:** Slider works, approval succeeds  
✅ **Test 3 Pass:** APIs return 200 with valid data

**If all 3 pass:** Phase 2 is working! 🎉

---

## 🐛 **QUICK FIXES**

### **Map Not Loading?**
```bash
cd admin-dashboard
npm install leaflet react-leaflet
npm run dev
```

### **API Errors?**
```bash
cd backend
pip install shapely geopy faiss-cpu
uvicorn app.main:app --reload
```

### **Photos Not Uploading?**
```bash
mkdir -p backend/uploads/media
chmod 777 backend/uploads/media
```

### **PostGIS Errors?**
```sql
-- Run in psql
CREATE EXTENSION IF NOT EXISTS postgis;
```

---

## 📊 **COMPLETE TEST RESULTS**

After quick test, fill this out:

```
PHASE 2 QUICK TEST RESULTS
==========================

Date: ___________
Time: ___ minutes

✅ Test 1: Map View          [ PASS / FAIL ]
✅ Test 2: Before/After       [ PASS / FAIL ]
✅ Test 3: API Endpoints      [ PASS / FAIL ]

Issues Found:
_________________________________
_________________________________

Overall Status: [ PASS / FAIL ]

Next Action:
[ ] Deploy to production
[ ] Run full test suite (27 tests)
[ ] Fix issues and retest
[ ] Continue to Phase 3
```

---

## 🎯 **NEXT STEPS**

### **If Quick Test Passes:**
1. ✅ Run full test suite (PHASE2_TESTING_GUIDE.md)
2. ✅ Performance testing with 100+ complaints
3. ✅ Mobile device testing
4. ✅ Deploy to staging/production

### **If Quick Test Fails:**
1. 🐛 Check error logs
2. 🔧 Apply quick fixes above
3. 🧪 Rerun quick test
4. 📞 Consult detailed guide if still failing

---

## 📞 **SUPPORT**

**Detailed Guide:** See PHASE2_TESTING_GUIDE.md  
**Documentation:** See PHASE2_COMPLETE.md  
**API Reference:** http://localhost:8000/docs

---

**Total Time:** ~10 minutes  
**Confidence Level:** High if all 3 pass  
**Next:** Full testing or deployment

🚀 **Happy Testing!**
