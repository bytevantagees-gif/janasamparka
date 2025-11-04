# 🌍 Multi-Region Access Control Architecture

## Overview

This document explains how **all users** (citizens, officers, moderators, auditors, MLAs) are assigned to constituencies/taluks, ensuring they only see relevant data for their regions.

---

## 🎯 Problem Statement

### Before (Issues)
- ❌ Citizens saw data from all constituencies
- ❌ Officers saw complaints outside their jurisdiction
- ❌ Moderators could moderate submissions from any constituency
- ❌ Auditors audited data beyond their assigned region
- ❌ No support for multi-taluk constituencies (e.g., Puttur MLA covers Puttur + Kadaba taluks)

### After (Solution)
- ✅ **Every user** assigned to specific constituency/constituencies
- ✅ **Data automatically filtered** by user's constituency
- ✅ **Multi-taluk support** - One constituency can span multiple taluks
- ✅ **Secure by default** - Users cannot access other regions' data
- ✅ **Admin override** - Admin role can see all constituencies

---

## 🏗️ Architecture

### User-Constituency Mapping

```
User Model (ALL ROLES):
├── constituency_id: UUID  # Primary assigned constituency
├── role: UserRole         # citizen, officer, moderator, auditor, mla, admin
└── name, phone, profile_photo, etc.

Constituency Model:
├── id: UUID
├── name: "Puttur"
├── code: "PUT001"
├── taluks: ["Puttur", "Kadaba"]  # Multi-taluk support
└── mla_name, district, state, etc.
```

### Role-Based Access Matrix

| Role              | Constituency Assignment | Access Scope                                    |
|-------------------|------------------------|-------------------------------------------------|
| **Citizen**       | Required (1)           | Own submissions + constituency data             |
| **Officer**       | Required (1+)          | Assigned complaints in their constituency       |
| **Moderator**     | Required (1+)          | Triage queue for their constituency             |
| **Auditor**       | Required (1+)          | Compliance/audit data for their constituency    |
| **MLA**           | Required (1)           | Full constituency analytics and oversight       |
| **Admin**         | None (NULL)            | **ALL constituencies** (system-wide access)     |

---

## 🔄 Data Flow

### 1. User Login & Constituency Selection

```javascript
// Citizen Login Flow
User logs in with OTP
  ↓
Check if user.constituency_id exists
  ↓
  NO → Show ConstituencySelector (first-time setup)
  YES → Redirect to dashboard with constituency context
```

### 2. API Request Filtering

```python
# Backend - Automatic Constituency Filtering
@router.get("/complaints")
async def list_complaints(
    current_user: User = Depends(require_auth),
    constituency_filter: UUID = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    
    # Automatic filtering by constituency
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    return query.all()
```

### 3. Frontend State Management

```javascript
// AuthContext automatically provides constituency
const { user } = useAuth();
// user.constituency_id is available in ALL components

// API calls automatically filtered
const { data } = useQuery({
  queryKey: ['complaints', user.constituency_id],
  queryFn: () => complaintsAPI.getAll()  // Backend handles filtering
});
```

---

## 📋 Implementation Details

### Backend: User Schema

The `users` table already has `constituency_id`:

```sql
-- Existing Schema (✅ Already Implemented)
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  phone VARCHAR(15) UNIQUE NOT NULL,
  role user_role NOT NULL,
  constituency_id UUID REFERENCES constituencies(id),  -- ✅ Exists
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Backend: Complaint Schema

All submissions linked to constituencies:

```sql
-- Existing Schema (✅ Already Implemented)
CREATE TABLE complaints (
  id UUID PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  constituency_id UUID NOT NULL REFERENCES constituencies(id),  -- ✅ Exists
  user_id UUID NOT NULL REFERENCES users(id),
  status complaint_status DEFAULT 'submitted',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast constituency filtering
CREATE INDEX idx_complaints_constituency ON complaints(constituency_id);
```

### Backend: Multi-Taluk Support

To support constituencies spanning multiple taluks (like Puttur + Kadaba under one MLA):

```sql
-- Option 1: Simple Array in Constituency
ALTER TABLE constituencies
ADD COLUMN taluks TEXT[] DEFAULT '{}';

-- Update example:
UPDATE constituencies
SET taluks = ARRAY['Puttur', 'Kadaba']
WHERE code = 'PUT001';

-- Option 2: Junction Table (More Flexible)
CREATE TABLE constituency_taluks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  constituency_id UUID NOT NULL REFERENCES constituencies(id),
  taluk_name VARCHAR(100) NOT NULL,
  district VARCHAR(100),
  UNIQUE(constituency_id, taluk_name)
);

-- Example data:
INSERT INTO constituency_taluks (constituency_id, taluk_name, district) VALUES
  ('puttur-constituency-id', 'Puttur', 'Dakshina Kannada'),
  ('puttur-constituency-id', 'Kadaba', 'Dakshina Kannada');
```

---

## 🎨 Frontend Implementation

### 1. Citizen Experience

**First Login:**
```
Login with OTP
  ↓
ConstituencySelector (full-page card UI)
  ↓
Select constituency (Puttur, Mangalore, Bantwal, etc.)
  ↓
Dashboard shows relevant data ONLY for selected constituency
```

**Subsequent Logins:**
```
Login with OTP
  ↓
Dashboard (constituency already saved)
  ↓
Can change constituency in Settings page
```

### 2. Officer/Moderator/Auditor Experience

**Admin assigns constituency during user creation:**
```
Admin creates Officer account
  ↓
Admin selects constituency: "Puttur"
  ↓
Officer sees ONLY Puttur complaints in work queue
```

**Visual Indicators:**
```jsx
// Dashboard Header
<div className="header">
  <h1>Officer Dashboard</h1>
  <p>Viewing: {user.constituency_name} • {user.constituency_taluks?.join(', ')}</p>
</div>
```

### 3. Officer Dashboard (constituency-filtered)

```jsx
// Officer Dashboard Component
export default function OfficerDashboard() {
  const { user } = useAuth();

  // Fetch complaints assigned to THIS officer in THEIR constituency
  const { data } = useQuery({
    queryKey: ['complaints', 'my-assignments', user.constituency_id],
    queryFn: async () => {
      // Backend automatically filters by constituency_id
      const response = await complaintsAPI.getAll({
        assigned_to: user.id
      });
      return response.data;
    }
  });

  // Display constituency info
  return (
    <div>
      <h1>Officer Dashboard</h1>
      <p>Your Region: {user.constituency_name}</p>
      <p>Taluks: {user.constituency_taluks?.join(', ') || 'All taluks'}</p>
      
      {/* Work queue shows ONLY their constituency's complaints */}
      <WorkQueue complaints={data?.complaints} />
    </div>
  );
}
```

### 4. Moderator Dashboard (constituency-filtered)

```jsx
// Moderator Dashboard Component
export default function ModeratorDashboard() {
  const { user } = useAuth();

  // Triage queue filtered by moderator's constituency
  const { data } = useQuery({
    queryKey: ['complaints', 'triage-queue', user.constituency_id],
    queryFn: async () => {
      // Backend filters: WHERE constituency_id = user.constituency_id
      const response = await complaintsAPI.getAll({
        status: 'submitted'
      });
      return response.data;
    }
  });

  return (
    <div>
      <h1>Moderator Control Center</h1>
      <p>{user.constituency_name} • {user.constituency_taluks?.join(', ')}</p>
      
      {/* Only see submissions from their constituency */}
      <TriageQueue submissions={data?.complaints} />
    </div>
  );
}
```

### 5. Auditor Dashboard (constituency-filtered)

```jsx
// Auditor Dashboard Component
export default function AuditorDashboard() {
  const { user } = useAuth();

  // Compliance metrics for auditor's assigned constituency
  const { data: complianceData } = useQuery({
    queryKey: ['analytics', 'compliance', user.constituency_id],
    queryFn: () => analyticsAPI.getCompliance()
  });

  return (
    <div>
      <h1>Auditor Dashboard</h1>
      <p>Auditing: {user.constituency_name}</p>
      
      {/* Red flags, SLA breaches - constituency-specific */}
      <ComplianceMetrics data={complianceData} />
    </div>
  );
}
```

---

## 🔒 Security Implementation

### Backend: Automatic Filtering Middleware

```python
# app/core/auth.py
def get_user_constituency_id(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[UUID]:
    """
    Returns constituency_id for automatic filtering.
    
    - Admin: Returns None (sees ALL constituencies)
    - Other roles: Returns user's constituency_id
    - No auth: Returns None (development mode)
    """
    if not current_user:
        return None  # Development/testing without auth
    
    if current_user.role == UserRole.ADMIN:
        return None  # Admin sees everything
    
    return current_user.constituency_id
```

### Backend: Endpoint Example

```python
# app/routers/complaints.py
@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    List complaints - automatically filtered by constituency.
    
    - Officers: See complaints assigned to them in their constituency
    - Moderators: See all complaints in their constituency
    - Auditors: Read-only access to their constituency
    - Admin: See all constituencies
    """
    query = db.query(Complaint)
    
    # Automatic constituency filtering (unless admin)
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
    
    # Role-specific additional filters
    if current_user.role == UserRole.DEPARTMENT_OFFICER:
        # Officers only see complaints assigned to them
        query = query.filter(Complaint.assigned_to == current_user.id)
    
    return query.all()
```

---

## 🧪 Testing Guide

### Test Scenarios

**Scenario 1: Citizen in Puttur**
```
1. Login as +919988770001 (Puttur citizen)
2. Select "Puttur" constituency (first time)
3. Dashboard shows ONLY Puttur submissions
4. Create new submission → automatically tagged with Puttur constituency_id
5. View map → see ONLY Puttur area complaints
```

**Scenario 2: Officer in Mangalore**
```
1. Admin assigns officer to "Mangalore" constituency
2. Officer logs in (+918242226101)
3. Work queue shows ONLY:
   - Complaints assigned to this officer
   - In Mangalore constituency
4. Cannot see Puttur or Bantwal complaints
```

**Scenario 3: Moderator in Bantwal**
```
1. Moderator logs in (assigned to Bantwal)
2. Triage queue shows ONLY Bantwal submissions
3. Cannot moderate Puttur or Mangalore submissions
4. Analytics show Bantwal-specific metrics
```

**Scenario 4: Admin (All Constituencies)**
```
1. Admin logs in (no constituency assigned)
2. Dashboard shows ALL constituencies
3. Can switch between constituencies in dropdown
4. Analytics compare Puttur vs Mangalore vs Bantwal
```

### Test Commands

```bash
# Login as different users
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -d '{"phone": "+919988770001", "otp": "123456"}'  # Puttur Citizen

curl -X POST http://localhost:8000/api/auth/verify-otp \
  -d '{"phone": "+918242226101", "otp": "123456"}'  # Mangalore Officer

# Check constituency filtering
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/complaints  # Should only return constituency-specific data
```

---

## 📊 Multi-Taluk Constituencies

### Example: Puttur Constituency

Puttur MLA constituency covers **two taluks**:
- **Puttur Taluk**
- **Kadaba Taluk**

**Database Setup:**
```sql
-- Update Puttur constituency to include both taluks
UPDATE constituencies
SET taluks = ARRAY['Puttur', 'Kadaba']
WHERE code = 'PUT001';

-- All complaints from either taluk belong to Puttur constituency
INSERT INTO complaints (title, constituency_id, taluk_name) VALUES
  ('Road repair needed', 'puttur-constituency-id', 'Puttur'),
  ('Water shortage', 'puttur-constituency-id', 'Kadaba');
```

**Frontend Display:**
```jsx
// Show constituency with taluks
<p>Your Constituency: {user.constituency_name}</p>
<p>Taluks: {user.constituency_taluks?.join(', ')}</p>

// Output:
// Your Constituency: Puttur
// Taluks: Puttur, Kadaba
```

---

## 🚀 Migration Path

### For Existing Data

```sql
-- 1. Assign existing users to constituencies
UPDATE users
SET constituency_id = (
  SELECT id FROM constituencies WHERE code = 'PUT001'
)
WHERE role = 'citizen' AND phone LIKE '+91998877%';

-- 2. Assign officers to constituencies
UPDATE users
SET constituency_id = (
  SELECT id FROM constituencies WHERE code = 'MNG001'
)
WHERE role = 'department_officer' AND phone = '+918242226101';

-- 3. Ensure all complaints have constituency_id
UPDATE complaints c
SET constituency_id = u.constituency_id
FROM users u
WHERE c.user_id = u.id AND c.constituency_id IS NULL;
```

---

## 📝 Admin User Management

### Constituency Assignment UI

**When admin creates/edits a user:**

```jsx
// Admin User Form
<FormField>
  <label>Constituency Assignment</label>
  <select name="constituency_id" required={role !== 'admin'}>
    <option value="">-- Select Constituency --</option>
    <option value="puttur-id">Puttur (Puttur, Kadaba)</option>
    <option value="mangalore-id">Mangalore North</option>
    <option value="bantwal-id">Bantwal</option>
  </select>
  <p className="help-text">
    {role === 'admin' 
      ? 'Admins can access all constituencies' 
      : 'User will only see data from this constituency'}
  </p>
</FormField>
```

---

## 🎯 Key Benefits

### For Citizens
✅ See complaints/feedback relevant to their area  
✅ No clutter from other constituencies  
✅ Better sense of community engagement  
✅ Can submit complaints, feedback, ideas, queries (not just issues)

### For Officers
✅ Work queue shows ONLY their jurisdiction  
✅ No confusion with other constituencies  
✅ Better focus on local issues  

### For Moderators
✅ Triage queue filtered by region  
✅ Quality control within scope  
✅ No accidental cross-constituency moderation  

### For Auditors
✅ Audit metrics for specific constituency  
✅ Identify red flags in their region  
✅ Compliance tracking scoped to jurisdiction  

### For MLAs
✅ Full visibility into their constituency  
✅ Multi-taluk support (e.g., Puttur + Kadaba)  
✅ Analytics and performance metrics  

### For Admins
✅ System-wide oversight  
✅ Compare constituencies  
✅ Manage users across all regions  

---

## 📦 Submission Types (Not Just Complaints)

Citizens can now submit:
- **Complaints** - Issues requiring resolution
- **Feedback** - Comments on services/programs
- **Ideas** - Suggestions for improvement
- **Queries** - Questions seeking information

**Frontend Updated:**
- ✅ "New Submission" button (not "New Complaint")
- ✅ "My Submissions" section
- ✅ "Share Feedback" action card
- ✅ Terminology reflects broader use case

---

## 🔍 Next Steps

1. ✅ **Frontend terminology updated** - "Submissions" instead of "Complaints"
2. ⏳ **Multi-taluk database** - Add taluks array to constituencies table
3. ⏳ **Constituency filtering** - Update officer/moderator/auditor dashboards
4. ⏳ **Admin UI** - Add constituency assignment in user management
5. ⏳ **Testing** - Verify filtering works for all roles
6. ⏳ **Documentation** - Update API docs with constituency filtering

---

## 📚 Related Documentation

- `CONSTITUENCY_SELECTION_COMPLETE.md` - Citizen constituency selection
- `ROLE_DASHBOARDS_IMPLEMENTATION_COMPLETE.md` - Role-based dashboards
- `MULTI_CONSTITUENCY_ARCHITECTURE.md` - Multi-tenancy architecture
- `MULTI_TENANT_ARCHITECTURE.md` - Data isolation strategy

---

**Last Updated:** October 30, 2024  
**Status:** Implementation In Progress  
**Test Status:** Pending Multi-Region Verification
