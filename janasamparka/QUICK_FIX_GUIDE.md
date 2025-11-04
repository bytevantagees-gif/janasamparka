# 🔧 Quick Fix Guide - Arabian Sea & Moderator Issues

## ✅ Issues Fixed

### 1. Moderator Users Created ✓

**3 moderator users created successfully**:

| Name | Phone | Constituency |
|------|-------|--------------|
| Puttur Moderator | +919900000000 | Puttur |
| Mangalore North Moderator | +919900000001 | Mangalore North |
| Udupi Moderator | +919900000002 | Udupi |

**Test Login**:
```bash
# 1. Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919900000000"}'

# 2. Check backend logs for OTP
docker compose logs backend --tail 20 | grep OTP

# 3. Verify OTP
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919900000000", "otp": "XXXXXX"}'
```

---

### 2. Coordinates Issue Diagnosed ✓

**✅ Database coordinates are CORRECT!**

Sample verified coordinates:
```
Title: Street Lights Issue #1
Lat: 12.5340384, Lng: 74.4512421
Location: Ward 2 - Bus Stand, Puttur

Range:
Latitude:  12.3 to 13.3 ✓
Longitude: 74.3 to 75.3 ✓
```

**⚠️ Issue is in FRONTEND map rendering!**

---

## 🗺️ Frontend Map Fix Required

### Problem
Frontend is likely rendering coordinates incorrectly, causing complaints to appear in Arabian Sea.

### Common Causes

#### 1. **Leaflet/React-Leaflet** (Most Common)
Leaflet uses `[lat, lng]` order:

```javascript
// ❌ WRONG - Swapped coordinates
<Marker position={[complaint.lng, complaint.lat]}>

// ✅ CORRECT
<Marker position={[complaint.lat, complaint.lng]}>
```

#### 2. **Google Maps**
Google Maps uses `{lat, lng}` object:

```javascript
// ❌ WRONG
new google.maps.LatLng(complaint.lng, complaint.lat)

// ✅ CORRECT
new google.maps.LatLng(complaint.lat, complaint.lng)
```

#### 3. **Mapbox**
Mapbox uses `[lng, lat]` order (opposite of Leaflet):

```javascript
// ❌ WRONG with Leaflet - Shows in Arabian Sea
<Marker coordinates={[complaint.lat, complaint.lng]}>

// ✅ CORRECT for Mapbox
<Marker coordinates={[complaint.lng, complaint.lat]}>
```

### How to Fix

#### Step 1: Find Map Component
```bash
# Search frontend code for map components
grep -r "Marker\|MapContainer\|GoogleMap" frontend/src/
```

#### Step 2: Check Coordinate Order
Look for patterns like:
- `[complaint.lng, complaint.lat]` - WRONG for Leaflet
- `[complaint.lat, complaint.lng]` - CORRECT for Leaflet
- `position={` or `coordinates={` or `center={`

#### Step 3: Update All Instances
**Example Fix for Leaflet**:
```diff
// frontend/src/components/ComplaintMap.tsx
- <Marker position={[complaint.lng, complaint.lat]}>
+ <Marker position={[complaint.lat, complaint.lng]}>

// Map center
- <MapContainer center={[constituency.lng, constituency.lat]}>
+ <MapContainer center={[constituency.lat, constituency.lng]}>
```

#### Step 4: Test
1. Clear browser cache
2. Reload frontend
3. Check if complaints now show in correct locations (Karnataka coast, not Arabian Sea)

---

## 🔐 Moderator Dashboard Access

### Expected Behavior

When logged in as **Moderator**, you should:

1. **See ALL complaints** in your constituency (not just yours)
2. **Have assignment powers** (assign to departments)
3. **Approve/reject work** completed by departments
4. **Access analytics** dashboard

### Frontend Check

Verify frontend handles moderator role correctly:

```typescript
// frontend/src/contexts/AuthContext.tsx or similar

// ❌ WRONG - Only checks for 'citizen' or 'mla'
if (user.role === 'citizen') {
  return <CitizenDashboard />
} else if (user.role === 'mla') {
  return <MLADashboard />
}

// ✅ CORRECT - Include moderator
if (user.role === 'citizen') {
  return <CitizenDashboard />
} else if (user.role === 'moderator' || user.role === 'mla') {
  return <ModeratorDashboard />
}
```

### API Permissions Check

Test moderator can see all complaints:

```bash
# Login as moderator
TOKEN="your-moderator-token"

# Should return ALL constituency complaints (not just moderator's)
curl -X GET "http://localhost:8000/api/complaints/" \
  -H "Authorization: Bearer $TOKEN"

# Should work - assign complaint
curl -X POST "http://localhost:8000/api/complaints/{id}/assign" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dept_id": "uuid-here",
    "assigned_to": "uuid-here",
    "note": "Assigned to PWD"
  }'
```

---

## 📊 Complete CRUD for Complaints

### ✅ Available Operations

| Operation | Endpoint | Who Can Do It |
|-----------|----------|---------------|
| **Create** | `POST /api/complaints/` | Citizens, Dept Officers, MLAs, Moderators |
| **Read List** | `GET /api/complaints/` | All (filtered by role) |
| **Read One** | `GET /api/complaints/{id}` | All (constituency check) |
| **Update Details** | `PUT /api/complaints/{id}` | Citizens (own), Moderators, MLAs |
| **Update Status** | `PUT /api/complaints/{id}/status` | Dept Officers, Moderators, MLAs |
| **Assign** | `POST /api/complaints/{id}/assign` | Moderators, MLAs |
| **Delete** | `DELETE /api/complaints/{id}` | Citizens (own, if submitted), Admin |
| **Add Media** | `POST /api/complaints/{id}/media` | Complaint owner, Assigned officer |
| **Rate** | `POST /api/complaints/{id}/rate` | Complaint owner (citizen) |
| **Approve Work** | `POST /api/complaints/{id}/work/approve` | MLAs, Moderators |
| **Reject Work** | `POST /api/complaints/{id}/work/reject` | MLAs, Moderators |

---

## 🧪 Testing Checklist

### Test Moderator Login
```bash
# 1. Create moderator (already done)
✅ Moderators created

# 2. Login via frontend
- Use phone: +919900000000 (Puttur)
- Get OTP from backend logs
- Verify OTP

# 3. Verify dashboard shows:
☐ All constituency complaints (not just own)
☐ Assignment buttons visible
☐ Status update controls
☐ Analytics section
```

### Test Complaint Workflow
```bash
# 1. Citizen files complaint
☐ Use citizen login (+9198000XXXXX)
☐ Create new complaint
☐ Status: SUBMITTED

# 2. Moderator assigns
☐ Login as moderator (+919900000000)
☐ View new complaint
☐ Assign to department
☐ Status: ASSIGNED

# 3. Department works
☐ Login as dept officer (+9197000XXXX)
☐ Update status to IN_PROGRESS
☐ Upload work photos
☐ Mark as RESOLVED

# 4. Moderator approves
☐ Login as moderator
☐ Review completed work
☐ Approve → Status: CLOSED
```

### Test Map Display
```bash
☐ Open complaints map view
☐ Verify markers show in Karnataka (not Arabian Sea)
☐ Expected location: ~12.8°N, 74.8°E
☐ Check coordinates in browser console
```

---

## 🎯 Summary

### ✅ Fixed
- 3 moderator users created for testing
- Database coordinates verified as correct
- Backend permissions already support moderators

### ⚠️ Frontend Fixes Needed
1. **Map coordinates**: Likely using `[lng, lat]` instead of `[lat, lng]`
2. **Role handling**: Verify moderator role triggers correct dashboard
3. **Permissions UI**: Show moderator controls (assign, approve, etc.)

### 📝 Next Steps
1. Check frontend map component coordinate order
2. Verify moderator role routing in frontend
3. Test complete workflow: Citizen → Moderator → Department → MLA
4. Update `DEMO_DATA_GUIDE.md` with moderator credentials

---

## 📞 Quick Commands

```bash
# Create more moderators if needed
docker compose exec backend python create_moderator.py

# Check moderators
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
mods = db.query(User).filter(User.role == 'moderator').all()
for m in mods: print(f'{m.name}: {m.phone}')
"

# Check complaint coordinates
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.complaint import Complaint
from sqlalchemy import func
db = SessionLocal()
stats = db.query(func.min(Complaint.lat), func.max(Complaint.lat), func.min(Complaint.lng), func.max(Complaint.lng)).first()
print(f'Lat: {stats[0]} to {stats[1]}')
print(f'Lng: {stats[2]} to {stats[3]}')
"

# Test moderator login
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919900000000"}'
```
