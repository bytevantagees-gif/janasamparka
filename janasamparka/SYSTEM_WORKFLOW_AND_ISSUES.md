# System Workflow and Issues - Analysis & Fixes

## 🔴 Critical Issues Identified

### 1. Moderator Login Issue
**Problem**: You logged in as Moderator but see Citizen interface.

**Root Cause**: 
- Frontend likely using wrong role detection logic
- Need to check which user you logged in as

**Diagnosis**:
```bash
# Check if moderator users exist
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
mods = db.query(User).filter(User.role == 'moderator').all()
print(f'Moderators: {[(m.name, m.phone, m.role) for m in mods]}')
db.close()
"
```

**Solution Needed**:
1. ✅ Backend supports moderator role (seen in routes)
2. ❌ No moderator users created in seed scripts
3. ❌ Frontend may not handle moderator role properly

---

### 2. Arabian Sea Location Issue 🌊
**Problem**: Most complaints show locations over Arabian Sea.

**Root Cause**: **Lat/Lng coordinates ARE CORRECT in seed script**
- Seed script uses: `lat=12.8±0.5`, `lng=74.8±0.5`
- This is correct for Dakshina Kannada (12.4-13.5°N, 74.6-75.5°E)

**Possible Causes**:
1. **Frontend Map Rendering**: Map may be swapping lat/lng
2. **PostGIS POINT Format**: Using `ST_Point(lng, lat)` instead of `ST_Point(lat, lng)`
3. **Database Storage**: Check if coordinates are stored correctly

**Verification Query**:
```sql
-- Check actual stored coordinates
SELECT id, title, lat, lng, location_description
FROM complaints
LIMIT 10;

-- If using PostGIS POINT:
SELECT id, title, ST_X(location), ST_Y(location) 
FROM complaints
WHERE location IS NOT NULL
LIMIT 10;
```

**Fix Required**: Check frontend map component - likely using `[lng, lat]` instead of `[lat, lng]`

---

## 📋 Complaint Workflow System

### Current Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLAINT LIFECYCLE                       │
└─────────────────────────────────────────────────────────────┘

1. CITIZEN FILES COMPLAINT
   └─> Status: SUBMITTED
       Assignment: Goes to WARD (not department directly)
       └─> API: POST /api/complaints/

2. WARD OFFICER REVIEWS
   └─> Can assign to appropriate department
       └─> API: POST /api/complaints/{id}/ward/assign-department
       └─> Status: SUBMITTED → ASSIGNED

3. DEPARTMENT RECEIVES
   └─> Department Officer assigned
       └─> Status: ASSIGNED
       └─> Can sub-assign to other officers
       └─> API: POST /api/complaints/{id}/sub-assign

4. WORK IN PROGRESS
   └─> Department updates status
       └─> API: PUT /api/complaints/{id}/status
       └─> Status: ASSIGNED → IN_PROGRESS

5. WORK COMPLETED
   └─> Department marks resolved
       └─> Status: IN_PROGRESS → RESOLVED
       └─> Requires approval from MLA/Moderator

6. APPROVAL WORKFLOW
   ├─> MLA/Moderator Approves:
   │   └─> API: POST /api/complaints/{id}/work/approve
   │       └─> Status: RESOLVED → CLOSED
   │
   └─> MLA/Moderator Rejects:
       └─> API: POST /api/complaints/{id}/work/reject
           └─> Status: RESOLVED → IN_PROGRESS (rework needed)

7. CITIZEN FEEDBACK
   └─> Citizen rates and reviews closed complaint
       └─> API: POST /api/complaints/{id}/rate
```

---

## 👥 Role-Based Permissions

### Who Can See What?

#### **CITIZEN**
- ✅ View: Their own complaints
- ✅ Create: New complaints
- ✅ Update: Their own complaints (before assignment)
- ✅ Rate: Closed complaints they filed
- ❌ Cannot: See other citizens' complaints
- ❌ Cannot: Change status or assign

**API Endpoints**:
```
GET    /api/complaints/me          # My complaints
POST   /api/complaints/             # File complaint
PUT    /api/complaints/{id}         # Update my complaint
DELETE /api/complaints/{id}         # Delete my complaint
POST   /api/complaints/{id}/rate    # Rate closed complaint
```

---

#### **MODERATOR**
- ✅ View: **ALL complaints** in their constituency
- ✅ Assign: Complaints to departments
- ✅ Update: Complaint status
- ✅ Approve/Reject: Completed work
- ✅ Manage: News, schedules, polls
- ✅ Access: Analytics and reports
- ❌ Cannot: Delete complaints (admin only)

**API Endpoints**:
```
GET    /api/complaints/              # All constituency complaints
GET    /api/complaints/{id}          # Any complaint details
POST   /api/complaints/{id}/assign   # Assign to department
PUT    /api/complaints/{id}/status   # Update status
POST   /api/complaints/{id}/work/approve   # Approve work
POST   /api/complaints/{id}/work/reject    # Reject work
GET    /api/analytics/constituency   # Analytics dashboard
```

**Permission Checks in Code**:
```python
# From complaints.py line 633
if current_user.role not in (UserRole.ADMIN, UserRole.MLA, UserRole.MODERATOR):
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

---

#### **DEPARTMENT_OFFICER / DEPARTMENT_USER**
- ✅ View: Complaints assigned to their department
- ✅ Update: Status of assigned complaints
- ✅ Sub-assign: To other officers in department
- ✅ Add: Internal notes
- ✅ Upload: Work photos/media
- ❌ Cannot: Assign to other departments
- ❌ Cannot: Approve final work (only MLA/Moderator)

**API Endpoints**:
```
GET    /api/complaints/              # Dept's complaints (filtered)
GET    /api/complaints/{id}          # Assigned complaint details
PUT    /api/complaints/{id}/status   # Update status
POST   /api/complaints/{id}/sub-assign     # Sub-assign
POST   /api/complaints/{id}/notes/internal # Add internal notes
POST   /api/complaints/{id}/media          # Upload photos
```

---

#### **MLA**
- ✅ View: **ALL complaints** in their constituency
- ✅ Assign: Complaints to departments
- ✅ Approve/Reject: Completed work
- ✅ Access: Full analytics dashboard
- ✅ Create: News, schedules, announcements
- ✅ Manage: Polls and forums
- ✅ View: Citizen ratings and feedback

**API Endpoints**:
```
GET    /api/complaints/              # All constituency complaints
GET    /api/analytics/mla-dashboard  # Full analytics
POST   /api/complaints/{id}/work/approve
POST   /api/complaints/{id}/work/reject
GET    /api/analytics/department-performance
GET    /api/analytics/ward-statistics
```

---

#### **ADMIN**
- ✅ View: **ALL complaints** (all constituencies)
- ✅ Manage: Users, departments, constituencies
- ✅ Delete: Any complaint
- ✅ Access: System-wide analytics
- ✅ Configure: System settings

---

## 🔧 CRUD Operations for Complaints

### ✅ **CREATE** - Who Can Create?
**Citizens, Department Officers, MLAs, Moderators, Admin**

```bash
POST /api/complaints/

{
  "title": "Road pothole near market",
  "description": "Large pothole causing accidents",
  "category": "Roads",
  "priority": "high",
  "lat": 12.8145,
  "lng": 74.8432,
  "ward_id": "uuid-here",
  "location_description": "MG Road, Ward 5"
}
```

**Response**: 201 Created with complaint ID

---

### ✅ **READ** - Who Can Read?

#### Get All Complaints (Filtered by Role)
```bash
GET /api/complaints/?page=1&page_size=20

# Optional filters:
?status=submitted
?priority=high
?category=Roads
?ward_id=uuid
?dept_id=uuid
?assigned_to_me=true
?user_id=uuid          # Only for admin/MLA
```

**Role-based filtering**:
- **Citizen**: Only their own (`user_id = current_user.id`)
- **Department Officer**: Only assigned to their department
- **Moderator/MLA**: All in their constituency
- **Admin**: All complaints

#### Get Single Complaint
```bash
GET /api/complaints/{complaint_id}
```

**Permissions**: Must be in same constituency (except admin)

---

### ✅ **UPDATE** - Who Can Update?

#### Update Complaint Details (Title, Description)
```bash
PUT /api/complaints/{complaint_id}

{
  "title": "Updated title",
  "description": "Updated description"
}
```

**Who**: Citizens (own complaints), Moderators, MLAs, Admin  
**When**: Before assignment (citizens), anytime (moderators/MLAs)

#### Update Status
```bash
PUT /api/complaints/{complaint_id}/status

{
  "status": "in_progress",
  "note": "Work started today"
}
```

**Who**: Department Officers, Moderators, MLAs, Admin  
**Status Flow**: 
- submitted → assigned (by moderator/MLA)
- assigned → in_progress (by department officer)
- in_progress → resolved (by department officer)
- resolved → closed (by MLA/moderator approval)

#### Assign to Department
```bash
POST /api/complaints/{complaint_id}/assign

{
  "dept_id": "uuid",
  "assigned_to": "uuid-of-officer",
  "note": "Assigned to PWD"
}
```

**Who**: Moderators, MLAs, Admin

#### Sub-assign Within Department
```bash
POST /api/complaints/{complaint_id}/sub-assign

{
  "assigned_to": "uuid-of-another-officer",
  "note": "Reassigned to field officer"
}
```

**Who**: Department Officers, Moderators

---

### ✅ **DELETE** - Who Can Delete?

```bash
DELETE /api/complaints/{complaint_id}
```

**Who**: 
- **Citizens**: Can delete their own complaints (only if status = submitted)
- **Admin**: Can delete any complaint

**From code** (line 423):
```python
async def delete_complaint(
    complaint_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    # Citizens can only delete their own submitted complaints
    if current_user.role == UserRole.CITIZEN:
        if complaint.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if complaint.status != ComplaintStatus.SUBMITTED:
            raise HTTPException(status_code=400, 
                detail="Can only delete submitted complaints")
    
    # Admin can delete any complaint
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, 
            detail="Only admins can delete complaints")
```

---

## 📊 How MLAs View Complaints

### MLA Dashboard Endpoints

```bash
# All constituency complaints
GET /api/complaints/?constituency_id={mla_constituency}

# Dashboard statistics
GET /api/complaints/stats
Response:
{
  "total": 100,
  "by_status": {
    "submitted": 21,
    "assigned": 19,
    "in_progress": 18,
    "resolved": 21,
    "closed": 21
  },
  "by_priority": {
    "low": 25,
    "medium": 40,
    "high": 25,
    "urgent": 10
  },
  "by_department": { ... }
}

# Ward-wise breakdown
GET /api/analytics/ward-statistics?constituency_id={id}

# Department performance
GET /api/analytics/department-performance?constituency_id={id}

# Trends over time
GET /api/analytics/trends?constituency_id={id}&days=30
```

---

## 🚨 Issues to Fix

### 1. Create Moderator Users
**Current**: No moderator users in database

**Fix**: Add moderator seed script
```python
# Add to seed_data.py or create seed_moderators.py
moderator = User(
    id=uuid.uuid4(),
    name="Constituency Moderator",
    phone="+919900000001",
    role="moderator",
    constituency_id=puttur_constituency.id,
    is_active=True,
    locale_pref="en"
)
db.add(moderator)
db.commit()
```

---

### 2. Fix Arabian Sea Coordinates
**Check frontend map component**:

```javascript
// WRONG - Leaflet/Mapbox uses [lat, lng]
new google.maps.LatLng(complaint.lng, complaint.lat)  // ❌

// CORRECT
new google.maps.LatLng(complaint.lat, complaint.lng)  // ✅
```

**Or check PostGIS usage**:
```sql
-- PostGIS ST_Point is (longitude, latitude)
ST_Point(lng, lat)  -- ✅ Correct
ST_Point(lat, lng)  -- ❌ Wrong
```

---

### 3. Frontend Role Detection
**Check frontend auth context**:
```typescript
// Should handle moderator role
const userRole = user.role; // "moderator"

if (userRole === "moderator") {
  // Show moderator dashboard
  // Allow viewing all complaints
  // Show approval buttons
}
```

---

## 🔄 Complete Complaint Lifecycle Example

### Scenario: Citizen Reports Pothole

```bash
# 1. Citizen files complaint
POST /api/complaints/
{
  "title": "Large pothole on MG Road",
  "description": "Dangerous pothole near bus stand",
  "category": "Roads",
  "priority": "high",
  "lat": 12.8145,
  "lng": 74.8432
}
# Status: SUBMITTED

# 2. Moderator assigns to PWD
POST /api/complaints/{id}/assign
{
  "dept_id": "pwd-dept-id",
  "assigned_to": "pwd-officer-id"
}
# Status: ASSIGNED
# Notification sent to PWD officer

# 3. PWD officer starts work
PUT /api/complaints/{id}/status
{
  "status": "in_progress",
  "note": "Work crew dispatched"
}
# Status: IN_PROGRESS
# Notification sent to citizen

# 4. PWD officer completes work
PUT /api/complaints/{id}/status
{
  "status": "resolved",
  "note": "Pothole filled and road leveled"
}
POST /api/complaints/{id}/media
{
  "media_type": "image",
  "url": "photo-of-completed-work.jpg"
}
# Status: RESOLVED
# Notification sent to MLA/Moderator for approval

# 5. MLA approves work
POST /api/complaints/{id}/work/approve
{
  "comments": "Good work, verified on-site"
}
# Status: CLOSED
# Notification sent to citizen

# 6. Citizen provides feedback
POST /api/complaints/{id}/rate
{
  "rating": 5,
  "feedback": "Fixed quickly, thank you!"
}
# Citizen rating recorded
```

---

## 🔍 Testing Checklist

### Test Moderator Access
```bash
# 1. Create moderator user (if not exists)
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.models.constituency import Constituency
import uuid

db = SessionLocal()
const = db.query(Constituency).first()

mod = User(
    id=uuid.uuid4(),
    name='Test Moderator',
    phone='+919900000001',
    role='moderator',
    constituency_id=const.id,
    is_active=True
)
db.add(mod)
db.commit()
print(f'Created: {mod.name} - {mod.phone}')
"

# 2. Login as moderator
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919900000001"}'

# 3. Verify OTP and get token
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919900000001", "otp": "XXXXXX"}'

# 4. Get all complaints (should see ALL constituency complaints)
curl -X GET http://localhost:8000/api/complaints/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📍 Next Steps

1. **Create Moderator Users**:
   ```bash
   docker compose exec backend python create_moderator.py
   ```

2. **Verify Coordinates**:
   ```bash
   docker compose exec db psql -U mlauser -d mla_connect -c \
     "SELECT id, title, lat, lng FROM complaints LIMIT 5;"
   ```

3. **Check Frontend Map**:
   - Inspect map component code
   - Verify lat/lng order in map markers
   - Check PostGIS POINT format if used

4. **Test Role-Based Access**:
   - Login as each role
   - Verify appropriate complaints visible
   - Test assignment and status updates

---

## 📞 Quick Reference

### User Roles Available
- `citizen` - General public
- `moderator` - Constituency moderator ⚠️ **MISSING IN SEED DATA**
- `department_user` / `department_officer` - Dept staff
- `mla` - Member of Legislative Assembly
- `admin` - System administrator

### Complaint Statuses
- `submitted` - New complaint
- `assigned` - Assigned to department
- `in_progress` - Work ongoing
- `resolved` - Work completed (awaiting approval)
- `closed` - Approved and closed

### Key APIs
```
POST   /api/complaints/                    # Create
GET    /api/complaints/                    # List (filtered)
GET    /api/complaints/{id}                # Read one
PUT    /api/complaints/{id}                # Update details
DELETE /api/complaints/{id}                # Delete
PUT    /api/complaints/{id}/status         # Update status
POST   /api/complaints/{id}/assign         # Assign to dept
POST   /api/complaints/{id}/work/approve   # Approve work
POST   /api/complaints/{id}/rate           # Citizen rating
```
