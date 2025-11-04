# Testing Scenario: Department Jurisdiction System

**Date**: October 30, 2025  
**Purpose**: End-to-end testing of ward-to-department jurisdiction validation

---

## Seed Data Summary

### Departments Created (15 total)

#### Taluk Panchayat Level (8 departments)

**Puttur TP Departments** (5):
- Puttur Public Works Department (PWD)
- Puttur Electricity Department (ELEC)
- Puttur Water Supply & Drainage (WATER)
- Puttur Health & Sanitation (HEALTH)
- Puttur Revenue & Administration (REVENUE)

**Bantwal TP Departments** (3):
- Bantwal Public Works Department (PWD)
- Bantwal Electricity Department (ELEC)
- Bantwal Water Supply & Drainage (WATER)

#### Gram Panchayat Level (2 departments)

**Panemangalore GP Departments**:
- Panemangalore GP Public Works (PWD)
- Panemangalore GP Water Supply (WATER)

### Wards Linked (9 wards)

**Puttur TP Wards** (5):
- Ward 1 - Kemminje
- Ward 2 - Neria
- Ward 3 - Kabaka
- Ward 4 - Kavu
- Ward 5 - Bolwar

**Bantwal TP Wards** (3):
- Central Ward (Ward 1)
- East Ward (Ward 2)
- West Ward (Ward 3)

**Panemangalore GP Ward** (1):
- North Ward (Ward 4)

### Test User Accounts

**Note**: System uses Firebase authentication. Create these accounts in Firebase with these phone numbers.

**Ward Officers**:
- Phone: +919876543210 (Ward 1 - Kemminje, Puttur TP)
- Phone: +919876543211 (Ward 2 - Neria, Puttur TP)
- Phone: +919876543212 (Ward 3 - Kabaka, Puttur TP)

**Department Officers**:
- Phone: +919876543220 (Puttur PWD Head)
- Phone: +919876543221 (Puttur PWD Engineer)
- Phone: +919876543222 (Puttur Electricity)
- Phone: +919876543223 (Puttur Water Supply)
- Phone: +919876543224 (Bantwal PWD)

---

## Test Scenarios

### Scenario 1: Valid Assignment (Puttur Ward → Puttur PWD) ✅

**Setup**:
1. Citizen creates complaint in Ward 1 - Kemminje (Puttur TP)
2. Complaint gets `assignment_type = "ward"`
3. Ward officer +919876543210 logs in

**Expected Behavior**:
```http
GET /api/complaints/ward/532ce9c5-ed09-49ec-9bb0-6dd5c92193df/available-departments

Response: [
  {
    "id": "<puttur-pwd-id>",
    "name": "Puttur Public Works Department",
    "code": "PWD"
  },
  {
    "id": "<puttur-elec-id>",
    "name": "Puttur Electricity Department",
    "code": "ELEC"
  },
  {
    "id": "<puttur-water-id>",
    "name": "Puttur Water Supply & Drainage",
    "code": "WATER"
  },
  {
    "id": "<puttur-health-id>",
    "name": "Puttur Health & Sanitation",
    "code": "HEALTH"
  },
  {
    "id": "<puttur-revenue-id>",
    "name": "Puttur Revenue & Administration",
    "code": "REVENUE"
  }
]
// Note: ONLY Puttur TP departments shown
// Bantwal and Panemangalore departments are HIDDEN
```

**Assignment**:
```http
POST /api/complaints/{complaint_id}/ward-assign
Body: {
  "dept_id": "<puttur-pwd-id>",
  "public_note": "Pothole on main road, assigning to PWD for repair"
}

Response: 200 OK
{
  "success": true,
  "message": "Complaint assigned to Puttur Public Works Department successfully",
  "assigned_department": "Puttur Public Works Department"
}
```

**Verification**:
- Complaint now has `assignment_type = "department"`
- Complaint has `dept_id = <puttur-pwd-id>`
- `public_notes` contains ward officer's note
- PWD officer +919876543220 can see it in `GET /my-department`

---

### Scenario 2: Invalid Assignment (Puttur Ward → Bantwal PWD) ❌

**Setup**:
1. Complaint in Ward 1 - Kemminje (Puttur TP)
2. Ward officer tries to assign to Bantwal PWD (different jurisdiction)

**Expected Behavior**:
```http
POST /api/complaints/{complaint_id}/ward-assign
Body: {
  "dept_id": "<bantwal-pwd-id>",  // Wrong jurisdiction!
  "public_note": "Road issue"
}

Response: 400 Bad Request
{
  "detail": "This department does not serve the ward's Taluk Panchayat"
}
```

**Verification**:
- Complaint remains at ward level
- `assignment_type` still = "ward"
- No department assignment made
- Error message clearly indicates jurisdiction mismatch

---

### Scenario 3: GP-Level Department (Panemangalore Ward → Panemangalore PWD) ✅

**Setup**:
1. Citizen creates complaint in North Ward (Panemangalore GP)
2. Ward type: `gram_panchayat`

**Expected Behavior**:
```http
GET /api/complaints/ward/1df18859-86ef-4edd-8198-f64d661d754b/available-departments

Response: [
  {
    "id": "<panemangalore-pwd-id>",
    "name": "Panemangalore GP Public Works",
    "code": "PWD"
  },
  {
    "id": "<panemangalore-water-id>",
    "name": "Panemangalore GP Water Supply",
    "code": "WATER"
  }
]
// Note: ONLY Panemangalore GP departments
// Puttur TP and Bantwal TP departments are HIDDEN
```

**Assignment**:
```http
POST /api/complaints/{complaint_id}/ward-assign
Body: {
  "dept_id": "<panemangalore-pwd-id>",
  "public_note": "Village road repair needed"
}

Response: 200 OK
```

---

### Scenario 4: Cross-TP Assignment Blocked ❌

**Setup**:
1. Complaint in Bantwal TP Central Ward
2. Ward officer tries to assign to Puttur TP PWD

**Expected Behavior**:
```http
POST /api/complaints/{complaint_id}/ward-assign
Body: {
  "dept_id": "<puttur-pwd-id>",  // Different TP!
  "public_note": "Road issue"
}

Response: 400 Bad Request
{
  "detail": "This department does not serve the ward's Taluk Panchayat"
}
```

---

### Scenario 5: Department Dashboard (Jurisdiction Filtering)

**Setup**:
1. Multiple complaints assigned to different departments
2. Department officer +919876543220 (Puttur PWD) logs in

**Expected Behavior**:
```http
GET /api/complaints/my-department

Response: {
  "total": 3,
  "complaints": [
    // ONLY complaints from Puttur TP wards
    {
      "id": "...",
      "title": "Pothole on Main Road",
      "ward_id": "<puttur-ward-1-id>",
      "dept_id": "<puttur-pwd-id>",
      "assignment_type": "department"
    }
  ]
}
// Note: Bantwal PWD complaints are NOT visible here
```

**Verification**:
- Puttur PWD officer sees ONLY Puttur TP ward complaints
- Bantwal PWD complaints are completely isolated
- No cross-jurisdiction visibility

---

## API Endpoints Reference

### 1. Get Available Departments for Ward
```
GET /api/complaints/ward/{ward_id}/available-departments
Authorization: Bearer <ward_officer_token>

Returns: List of departments matching ward's jurisdiction
```

### 2. Assign Complaint to Department
```
POST /api/complaints/{complaint_id}/ward-assign
Authorization: Bearer <ward_officer_token>
Body: {
  "dept_id": "uuid",
  "public_note": "string (required, 10-500 chars)"
}

Validates: dept jurisdiction matches ward jurisdiction
Returns: Success or 400 with jurisdiction error
```

### 3. Ward Officer's Complaints
```
GET /api/complaints/my-ward
Authorization: Bearer <ward_officer_token>

Returns: All complaints in officer's assigned ward
```

### 4. Department's All Complaints
```
GET /api/complaints/my-department
Authorization: Bearer <department_officer_token>

Returns: All complaints assigned to officer's department
```

### 5. Individual Officer's Assignments
```
GET /api/complaints/my-assigned
Authorization: Bearer <department_officer_token>

Returns: Only complaints specifically assigned to this officer
```

---

## Database Verification Queries

### Check Department Jurisdiction
```sql
SELECT 
  d.name,
  d.code,
  CASE 
    WHEN d.gram_panchayat_id IS NOT NULL THEN 'GP Level'
    WHEN d.taluk_panchayat_id IS NOT NULL THEN 'TP Level'
    WHEN d.zilla_panchayat_id IS NOT NULL THEN 'ZP Level'
    WHEN d.city_corporation_id IS NOT NULL THEN 'Corp Level'
  END as level,
  COALESCE(gp.name, tp.name, zp.name) as parent_body
FROM departments d
LEFT JOIN gram_panchayats gp ON d.gram_panchayat_id = gp.id
LEFT JOIN taluk_panchayats tp ON d.taluk_panchayat_id = tp.id
LEFT JOIN zilla_panchayats zp ON d.zilla_panchayat_id = zp.id
WHERE d.taluk_panchayat_id IS NOT NULL OR d.gram_panchayat_id IS NOT NULL
ORDER BY level, d.name;
```

### Check Ward Linking
```sql
SELECT 
  w.name,
  w.ward_number,
  w.ward_type,
  COALESCE(gp.name, tp.name) as parent_body
FROM wards w
LEFT JOIN gram_panchayats gp ON w.gram_panchayat_id = gp.id
LEFT JOIN taluk_panchayats tp ON w.taluk_panchayat_id = tp.id
WHERE w.ward_type IS NOT NULL
ORDER BY w.ward_number;
```

### Check Complaint Assignments
```sql
SELECT 
  c.id,
  c.title,
  c.assignment_type,
  w.name as ward_name,
  d.name as department_name,
  CASE
    WHEN c.assignment_type = 'ward' THEN 'At Ward Level'
    WHEN c.assignment_type = 'department' THEN 'At Department Level'
  END as current_stage
FROM complaints c
LEFT JOIN wards w ON c.ward_id = w.id
LEFT JOIN departments d ON c.dept_id = d.id
ORDER BY c.created_at DESC
LIMIT 10;
```

---

## Testing Checklist

### Phase 1: Setup
- [x] Departments created with jurisdiction links
- [x] Wards linked to parent panchayats (GP/TP)
- [ ] Ward officers registered in Firebase
- [ ] Department officers registered in Firebase
- [ ] Test citizen account created

### Phase 2: Ward Assignment
- [ ] Citizen creates complaint → Goes to ward
- [ ] Ward officer logs in → Sees complaint in `/my-ward`
- [ ] Ward officer requests `/ward/{id}/available-departments` → Sees only matching jurisdiction
- [ ] Ward officer assigns to valid department → Success
- [ ] Ward officer tries invalid department → 400 error with clear message

### Phase 3: Department Processing
- [ ] Department officer logs in → `/my-department` shows only their jurisdiction
- [ ] Department head assigns to specific officer
- [ ] Officer adds public note → Citizen sees it
- [ ] Officer adds internal note → Citizen doesn't see it

### Phase 4: Cross-Jurisdiction Validation
- [ ] Puttur ward → Puttur dept: ✅ Allowed
- [ ] Puttur ward → Bantwal dept: ❌ Blocked
- [ ] Bantwal ward → Bantwal dept: ✅ Allowed
- [ ] GP ward → GP dept: ✅ Allowed
- [ ] GP ward → TP dept: ❌ Blocked

### Phase 5: Dashboard Isolation
- [ ] Puttur PWD officer sees only Puttur TP complaints
- [ ] Bantwal PWD officer sees only Bantwal TP complaints
- [ ] No cross-jurisdiction visibility
- [ ] Statistics accurate per jurisdiction

---

## Expected Outcomes

✅ **Geographical Isolation**: Puttur PWD ≠ Bantwal PWD ≠ Panemangalore GP PWD

✅ **Jurisdiction Enforcement**: Backend validates at multiple levels
- Database: Foreign key constraints
- Business Logic: `ward_assign_to_department()` validation
- API: Filtered department lists

✅ **User Experience**: Ward officers see only relevant departments

✅ **Data Integrity**: No way to assign across jurisdictions

✅ **Audit Trail**: All assignments logged with jurisdiction info

---

## Next Steps

1. **Register Firebase Users**: Create accounts for test phone numbers
2. **Build Frontend**: Ward Officer Dashboard with jurisdiction-filtered dropdown
3. **Run Tests**: Execute all 5 scenarios above
4. **Performance**: Test with 100+ departments across multiple TPs
5. **Edge Cases**: Handle wards with no parent, departments with no jurisdiction

---

## Files Modified

- `/backend/app/models/department.py` - Added jurisdiction fields
- `/backend/alembic/versions/e300c119a978_*.py` - Migration
- `/backend/app/services/complaint_routing.py` - Validation logic
- `/backend/app/routers/complaints.py` - New endpoints
- `/backend/seed_departments_and_wards.sql` - Seed data
- `DEPARTMENT_JURISDICTION_SYSTEM.md` - Complete documentation

**Status**: ✅ Backend Complete | ⏳ Frontend Pending
