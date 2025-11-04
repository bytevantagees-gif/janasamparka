# Ward-Centric Complaint Management System - Complete Redesign

## ✅ What Changed: From Panchayat-First to Ward-First

### Old Flow (DEPRECATED):
```
Citizen → GP/TP/ZP/Department → Officer
```

### NEW Flow (CURRENT):
```
Citizen → Ward → Department → Officer
         ↓           ↓
    (Ward Officer assigns with public note)
                (Department Officer updates with public notes)
```

---

## 🎯 Core Principle

**"Wards come under Panchayats, Town Panchayats, City Corporations. Complaints are basically assigned to them."**

- **Wards** are the first point of contact for all complaints
- **Ward Officers** triage and assign to appropriate departments
- **Citizens** only see **public notes** (meaningful progress updates)
- **Officers** use **internal notes** for coordination

---

## 📊 Database Changes

### Migration: `79bec4cadb9f_ward_panchayat_linking_and_complaint_redesign`

#### 1. Wards Table Updates
```sql
ALTER TABLE wards ADD COLUMN ward_type VARCHAR(20);
-- Values: 'gram_panchayat', 'taluk_panchayat', 'city_corporation', 'municipality'

ALTER TABLE wards ADD COLUMN gram_panchayat_id UUID;
ALTER TABLE wards ADD COLUMN taluk_panchayat_id UUID;
ALTER TABLE wards ADD COLUMN city_corporation_id UUID;
-- FK constraints to respective tables
```

**Ward Types:**
- `gram_panchayat` - Rural villages under Gram Panchayats
- `taluk_panchayat` - Towns under Taluk Panchayats  
- `city_corporation` - Urban wards under City Corporations
- `municipality` - Municipality wards

#### 2. Complaints Table Updates
```sql
-- NEW: Public notes visible to citizens
ALTER TABLE complaints ADD COLUMN public_notes TEXT;

-- NEW: Ward officer who processed the complaint
ALTER TABLE complaints ADD COLUMN ward_officer_id UUID;
-- FK to users table
```

#### 3. Users Table Updates
```sql
-- NEW: Ward assignment for ward officers
ALTER TABLE users ADD COLUMN ward_id UUID;
-- FK to wards table
```

#### 4. New User Role
```python
class UserRole:
    WARD_OFFICER = "ward_officer"  # NEW ROLE
```

---

## 🔄 Complaint Lifecycle

### Stage 1: Citizen Submits Complaint
```python
POST /api/complaints/

Response:
{
  "id": "uuid",
  "assignment_type": "ward",  # Always "ward" initially
  "ward_id": "uuid",
  "status": "submitted",
  "dept_id": null,            # Not assigned yet
  "ward_officer_id": null     # No officer yet
}
```

### Stage 2: Ward Officer Reviews & Assigns
```python
GET /api/complaints/my-ward  # Ward officer sees all complaints in their ward

POST /api/complaints/{id}/ward-assign
{
  "dept_id": "uuid",
  "public_note": "This appears to be a drainage issue. Forwarding to Public Works Department for immediate action."
}

Response:
{
  "success": true,
  "assigned_department": "Public Works Department",
  "ward_officer_name": "Ramesh Kumar"
}

# Complaint now has:
{
  "assignment_type": "department",
  "dept_id": "uuid",
  "ward_officer_id": "uuid",
  "status": "assigned",
  "public_notes": "[2025-10-30 13:00] Ward Officer: This appears to be a drainage issue..."
}
```

### Stage 3: Department Officer Works on It
```python
# Department officer adds progress updates
POST /api/complaints/{id}/public-note
{
  "note": "Work order issued to contractor. Work will begin on November 2nd."
}

# Citizens see:
{
  "public_notes": "[2025-10-30 13:00] Ward Officer: This appears to be a drainage issue...\n\n[2025-10-31 10:30] PWD Officer: Work order issued to contractor. Work will begin on November 2nd."
}

# Internal coordination (citizens don't see):
POST /api/complaints/{id}/internal-note
{
  "note": "Budget sanctioned from Q3 allocation. Contractor: ABC Constructions. Estimated completion: 5 days."
}
```

### Stage 4: Complaint Resolved
```python
PATCH /api/complaints/{id}/status
{
  "status": "resolved"
}

POST /api/complaints/{id}/public-note
{
  "note": "Drainage work completed. Please verify and provide feedback."
}
```

---

## 🔐 Role-Based Access

| Action | Citizen | Ward Officer | Dept Officer | Admin |
|--------|---------|--------------|--------------|-------|
| Submit complaint | ✅ | ✅ | ✅ | ✅ |
| View public notes | ✅ | ✅ | ✅ | ✅ |
| View internal notes | ❌ | ✅ | ✅ | ✅ |
| See ward complaints | ❌ | Own ward only | ❌ | All |
| Assign to department | ❌ | ✅ | ❌ | ✅ |
| Add public note | ❌ | ✅ | ✅ | ✅ |
| Add internal note | ❌ | ✅ | ✅ | ✅ |
| Update status | ❌ | ❌ | ✅ | ✅ |

---

## 📝 API Reference

### New Endpoints

#### 1. Ward Officer Assigns to Department
```http
POST /api/complaints/{complaint_id}/ward-assign
Authorization: Bearer <token>
Content-Type: application/json

{
  "dept_id": "550e8400-e29b-41d4-a716-446655440000",
  "public_note": "Forwarding to PWD for road repair"
}

Response 200:
{
  "success": true,
  "message": "Complaint assigned to Public Works Department successfully",
  "complaint_id": "...",
  "assigned_department": "Public Works Department",
  "ward_officer_name": "Ramesh Kumar"
}
```

**Authorization:**
- Role: `WARD_OFFICER`
- Must be assigned to the complaint's ward
- Complaint must be at `assignment_type="ward"`

---

#### 2. Get Ward Complaints
```http
GET /api/complaints/my-ward?page=1&page_size=20&status=submitted
Authorization: Bearer <token>

Response 200:
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "complaints": [
    {
      "id": "...",
      "title": "Street light not working",
      "ward_id": "...",
      "assignment_type": "ward",
      "status": "submitted",
      "created_at": "2025-10-30T10:30:00Z"
    }
  ]
}
```

**Authorization:**
- Role: `WARD_OFFICER`
- Shows only complaints from officer's assigned ward
- Only shows complaints with `assignment_type="ward"` (not yet assigned to departments)

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 20, max: 100)
- `status` - Filter by complaint status
- `category` - Filter by category
- `search` - Full-text search

---

#### 3. Add Public Note
```http
POST /api/complaints/{complaint_id}/public-note
Authorization: Bearer <token>
Content-Type: application/json

{
  "note": "Work order issued. Work will start on Monday."
}

Response 200:
{
  "success": true,
  "message": "Public note added successfully",
  "complaint_id": "...",
  "public_notes": "[2025-10-30 13:00] Ward Officer: Forwarding to PWD...\n\n[2025-10-31 10:00] PWD Officer: Work order issued..."
}
```

**Authorization:**
- Roles: `WARD_OFFICER`, `DEPARTMENT_OFFICER`, `MODERATOR`, `MLA`, `ADMIN`
- Must have access to complaint's constituency

**Use Cases:**
- "Materials procured, work starting tomorrow"
- "Work completed, please verify"
- "Waiting for contractor availability"
- "Additional survey required"

---

#### 4. Add Internal Note
```http
POST /api/complaints/{complaint_id}/internal-note
Authorization: Bearer <token>
Content-Type: application/json

{
  "note": "Budget approved from Q3 allocation. Contractor: ABC Ltd."
}

Response 200:
{
  "success": true,
  "message": "Internal note added successfully",
  "complaint_id": "...",
  "internal_notes": "..."
}
```

**Authorization:**
- Roles: `WARD_OFFICER`, `DEPARTMENT_OFFICER`, `MODERATOR`, `MLA`, `ADMIN`
- Must have access to complaint's constituency

**Use Cases:**
- "Escalate to senior engineer"
- "Budget discussion with ZP pending"
- "Citizen very angry, high priority"
- "Coordinate with electricity department"

---

### Modified Endpoints

#### Complaint Creation (Updated)
```http
POST /api/complaints/

OLD Payload:
{
  "title": "...",
  "description": "...",
  "ward_id": "uuid",
  "gram_panchayat_id": "uuid",  # OLD: Could specify GP
  "dept_id": "uuid"              # OLD: Could specify dept
}

NEW Payload:
{
  "title": "...",
  "description": "...",
  "ward_id": "uuid"  # REQUIRED: Ward only
}

# All complaints now go to ward initially
# Ward officers will assign to departments
```

**Changes:**
- `assignment_type` always set to `"ward"`
- `dept_id`, `gram_panchayat_id`, `taluk_panchayat_id`, `zilla_panchayat_id` all set to `null`
- `ward_id` is required

---

## 🏗️ Model Changes

### Ward Model (Updated)
```python
class Ward(Base):
    __tablename__ = "wards"
    
    id: UUID
    name: str
    ward_number: int
    taluk: str
    constituency_id: UUID
    
    # NEW: Link to parent administrative body
    ward_type: Optional[str]  # 'gram_panchayat', 'taluk_panchayat', 'city_corporation'
    gram_panchayat_id: Optional[UUID]
    taluk_panchayat_id: Optional[UUID]
    city_corporation_id: Optional[UUID]
    
    population: int
    geom: Geometry
```

**Relationships:**
- `ward_type="gram_panchayat"` → `gram_panchayat_id` is set
- `ward_type="taluk_panchayat"` → `taluk_panchayat_id` is set
- `ward_type="city_corporation"` → `city_corporation_id` is set

---

### Complaint Model (Updated)
```python
class Complaint(Base):
    __tablename__ = "complaints"
    
    # ... existing fields ...
    
    ward_id: UUID  # Always set
    
    # NEW: Ward officer who processed complaint
    ward_officer_id: Optional[UUID]  # Set when ward assigns to dept
    
    # NEW: Public notes (citizen-visible)
    public_notes: Optional[str]
    
    # Existing: Internal notes (officer-only)
    internal_notes: Optional[str]
    notes_are_internal: bool = True
    
    # Assignment type: 'ward' (initial) or 'department' (after ward assigns)
    assignment_type: str  # 'ward' → 'department'
    
    # Department (set by ward officer)
    dept_id: Optional[UUID]  # Null until ward assigns
    
    # Legacy fields (kept for backward compatibility, not used in new flow)
    gram_panchayat_id: Optional[UUID]  # Deprecated
    taluk_panchayat_id: Optional[UUID]  # Deprecated
    zilla_panchayat_id: Optional[UUID]  # Deprecated
```

---

### User Model (Updated)
```python
class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    WARD_OFFICER = "ward_officer"  # NEW ROLE
    DEPARTMENT_OFFICER = "department_officer"
    # ... other roles ...

class User(Base):
    __tablename__ = "users"
    
    id: UUID
    name: str
    role: UserRole
    
    constituency_id: Optional[UUID]
    
    # NEW: Ward assignment for ward officers
    ward_id: Optional[UUID]
    
    # Department assignment for dept officers
    department_id: Optional[UUID]
    
    # Panchayat assignments (for panchayat officials)
    gram_panchayat_id: Optional[UUID]
    taluk_panchayat_id: Optional[UUID]
    zilla_panchayat_id: Optional[UUID]
```

---

## 📱 Frontend Requirements

### Ward Officer Dashboard

**Page:** `/ward-officer/dashboard`

**Components Needed:**

1. **Complaint List**
   - Fetches: `GET /api/complaints/my-ward`
   - Shows: All complaints in officer's ward
   - Filters: Status, Category, Search
   - Actions: "Assign to Department" button

2. **Assign Modal**
   - Department dropdown (filtered by constituency)
   - Public note textarea (required, min 10 chars)
   - "Assign" button
   - API: `POST /api/complaints/{id}/ward-assign`

3. **Statistics Cards**
   - Total complaints in ward
   - Pending assignment (status=submitted)
   - Assigned today
   - Average response time

**Example Code:**
```jsx
// Ward Officer Dashboard
const WardOfficerDashboard = () => {
  const { data: complaints } = useQuery({
    queryKey: ['ward-complaints'],
    queryFn: () => api.get('/api/complaints/my-ward')
  });
  
  const assignMutation = useMutation({
    mutationFn: ({ complaintId, deptId, publicNote }) =>
      api.post(`/api/complaints/${complaintId}/ward-assign`, {
        dept_id: deptId,
        public_note: publicNote
      })
  });
  
  return (
    <div>
      <h1>Ward Complaints</h1>
      <ComplaintList 
        complaints={complaints}
        onAssign={(id) => openAssignModal(id)}
      />
    </div>
  );
};
```

---

### Citizen Complaint View (Updated)

**Changes:**
- Show `public_notes` field (formatted with timestamps)
- **DO NOT** show `internal_notes` (officers only)
- Show assignment flow: "Submitted → Assigned to [Department]"

**Example:**
```jsx
const ComplaintDetail = ({ complaint }) => {
  return (
    <div>
      <h2>{complaint.title}</h2>
      <p>{complaint.description}</p>
      
      <div className="assignment-flow">
        {complaint.assignment_type === 'ward' ? (
          <Badge color="blue">Being reviewed by Ward Officer</Badge>
        ) : (
          <Badge color="green">Assigned to {complaint.department_name}</Badge>
        )}
      </div>
      
      {/* Citizens only see public notes */}
      {complaint.public_notes && (
        <div className="public-updates">
          <h3>Progress Updates</h3>
          <div className="notes">{complaint.public_notes}</div>
        </div>
      )}
      
      {/* Internal notes NOT shown to citizens */}
    </div>
  );
};
```

---

## 🧪 Testing Checklist

### Backend API Testing

- [x] Migration applied successfully
- [x] Backend starts without errors
- [ ] Create complaint → `assignment_type="ward"`, `dept_id=null`
- [ ] Ward officer calls `GET /api/complaints/my-ward` → sees ward complaints
- [ ] Ward officer assigns to dept → `assignment_type="department"`, `dept_id` set, public note added
- [ ] Add public note → `public_notes` updated with timestamp
- [ ] Add internal note → `internal_notes` updated, `public_notes` unchanged
- [ ] Citizen views complaint → sees `public_notes`, NOT `internal_notes`
- [ ] Ward officer from different ward tries to assign → 403 Forbidden
- [ ] Non-ward-officer tries `GET /my-ward` → 403 Forbidden

### Database Verification

```sql
-- Check wards table
SELECT id, name, ward_type, gram_panchayat_id, taluk_panchayat_id 
FROM wards LIMIT 5;

-- Check complaints flow
SELECT id, title, assignment_type, ward_id, dept_id, ward_officer_id, 
       public_notes, internal_notes
FROM complaints 
ORDER BY created_at DESC LIMIT 10;

-- Check ward officers
SELECT id, name, role, ward_id 
FROM users 
WHERE role = 'ward_officer';
```

---

## 🚀 Migration Path

### For Existing Complaints

**Option 1: Leave as-is (Recommended)**
- Keep old complaints with their current assignments
- New complaints use ward-first flow
- Both flows coexist

**Option 2: Migrate old complaints**
```sql
-- Set all old complaints to ward-first
UPDATE complaints 
SET assignment_type = 'ward',
    dept_id = NULL,
    ward_officer_id = NULL
WHERE assignment_type IN ('gram_panchayat', 'taluk_panchayat', 'zilla_panchayat');
```

### For Wards Without Panchayat Links

```sql
-- Link wards to panchayats (example)
UPDATE wards 
SET ward_type = 'gram_panchayat',
    gram_panchayat_id = (
        SELECT id FROM gram_panchayats 
        WHERE constituency_id = wards.constituency_id 
        LIMIT 1
    )
WHERE ward_type IS NULL;
```

---

## ✅ Summary

**What was implemented:**
1. ✅ Ward model updated with panchayat/corporation linking
2. ✅ Complaint model updated with `ward_officer_id` and `public_notes`
3. ✅ User model updated with `ward_id` assignment
4. ✅ New role: `WARD_OFFICER`
5. ✅ Complaint creation changed to ward-first
6. ✅ New endpoint: `POST /ward-assign` - Ward assigns to department
7. ✅ New endpoint: `GET /my-ward` - Ward officer sees complaints
8. ✅ New endpoint: `POST /public-note` - Add citizen-visible note
9. ✅ New endpoint: `POST /internal-note` - Add officer-only note
10. ✅ Database migration applied successfully
11. ✅ Backend restarted and operational

**What's pending:**
- ⏳ Frontend: Ward Officer Dashboard
- ⏳ Frontend: Update Citizen Complaint View (show public notes only)
- ⏳ Frontend: Update Admin/Moderator views
- ⏳ Seed data: Create ward officers and link wards to panchayats
- ⏳ Testing: End-to-end workflow testing

**Architecture:**
- **Simple**: Citizen → Ward → Department (2-step process)
- **Clear**: Ward officers are gatekeepers, department officers execute
- **Transparent**: Citizens see meaningful public notes, not internal coordination

---

**Status:** Backend 100% complete. Ready for frontend dashboard development.
