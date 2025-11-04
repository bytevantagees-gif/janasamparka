# Multi-Constituency Architecture - How Data is Organized

## Overview
The Janasamparka MLA Connect app supports **multiple constituencies** in a single system. Each constituency (MLA's area) has its own isolated data for wards, departments, polls, budgets, FAQs, and more.

**Date**: October 30, 2025  
**Architecture**: Multi-Tenant by Constituency  
**Current Constituencies**: 3 (Puttur, Mangalore, Bantwal)

---

## Database Architecture

### Constituency as Central Entity

The `constituencies` table is the **parent table** for all constituency-specific data:

```sql
CREATE TABLE constituencies (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    code VARCHAR UNIQUE NOT NULL,
    state VARCHAR NOT NULL,
    district VARCHAR,
    mla_id UUID REFERENCES users(id),  -- Link to MLA user
    description TEXT,
    population INTEGER,
    area_sq_km NUMERIC,
    boundaries GEOMETRY(Polygon, 4326),  -- PostGIS polygon
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Constituency-Linked Entities

### 1. **Wards** (`wards` table)
Each constituency has multiple wards (voting areas/neighborhoods).

```sql
CREATE TABLE wards (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    ward_number INTEGER NOT NULL,
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    population INTEGER,
    area_sq_km NUMERIC,
    boundaries GEOMETRY(Polygon, 4326),
    councilor_name VARCHAR,
    councilor_phone VARCHAR,
    created_at TIMESTAMP
);
```

**Relationship**: 
- **Constituency (1) → Wards (Many)**
- Each ward belongs to exactly ONE constituency
- Query: `SELECT * FROM wards WHERE constituency_id = 'puttur-id'`

**Example**:
- Puttur Constituency has 15 wards
- Mangalore Constituency has 60 wards
- Bantwal Constituency has 25 wards

---

### 2. **Departments** (`departments` table)
Government departments operate within each constituency.

```sql
CREATE TABLE departments (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    head_officer_id UUID REFERENCES users(id),
    description TEXT,
    phone VARCHAR,
    email VARCHAR,
    office_address TEXT,
    created_at TIMESTAMP
);
```

**Relationship**:
- **Constituency (1) → Departments (Many)**
- Same department (e.g., "Roads & Transport") exists separately in each constituency
- Officers are assigned to departments within their constituency

**Example**:
```
Puttur Constituency:
  - Roads & Transport Department
  - Water Supply Department
  - Electricity Department

Mangalore Constituency:
  - Roads & Transport Department (different from Puttur's)
  - Water Supply Department
  - Sanitation Department
```

---

### 3. **Polls** (`polls` table)
Polls/surveys are constituency-specific.

```sql
CREATE TABLE polls (
    id UUID PRIMARY KEY,
    question TEXT NOT NULL,
    description TEXT,
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    created_by UUID REFERENCES users(id),
    options JSONB,  -- ["Option 1", "Option 2", "Option 3"]
    starts_at TIMESTAMP,
    ends_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    total_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP
);
```

**Relationship**:
- **Constituency (1) → Polls (Many)**
- Each poll is visible only to citizens of that constituency
- MLA creates polls for their own constituency only

**Example**:
```
Poll in Puttur: "Should we prioritize road repairs in Ward 5?"
Poll in Mangalore: "New bus route - which area should it cover?"
```

---

### 4. **Budgets** (`ward_budgets`, `department_budgets`)
Budget allocations are tracked per constituency.

```sql
CREATE TABLE ward_budgets (
    id UUID PRIMARY KEY,
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    ward_id UUID REFERENCES wards(id),
    fiscal_year INTEGER NOT NULL,
    allocated_amount NUMERIC(15,2),
    utilized_amount NUMERIC(15,2),
    category VARCHAR,  -- 'roads', 'water', 'electricity'
    description TEXT
);

CREATE TABLE department_budgets (
    id UUID PRIMARY KEY,
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    department_id UUID REFERENCES departments(id),
    fiscal_year INTEGER NOT NULL,
    allocated_amount NUMERIC(15,2),
    utilized_amount NUMERIC(15,2),
    category VARCHAR,
    description TEXT
);
```

**Relationship**:
- **Constituency (1) → Ward Budgets (Many)**
- **Constituency (1) → Department Budgets (Many)**
- Budget transparency per constituency
- Each MLA manages their own constituency's budget

---

### 5. **FAQs** (`faq_solutions` table)
Frequently Asked Questions are constituency-specific.

```sql
CREATE TABLE faq_solutions (
    id UUID PRIMARY KEY,
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR,  -- 'roads', 'water', 'healthcare'
    language VARCHAR DEFAULT 'en',  -- 'en', 'kn', 'hi'
    helpful_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP
);
```

**Relationship**:
- **Constituency (1) → FAQs (Many)**
- Solutions relevant to one constituency may not apply to others
- Search results filtered by constituency

**Example**:
```
Puttur FAQ: "How to report potholes on Kadaba Road?"
Mangalore FAQ: "Beach cleaning schedule for Panambur Beach?"
```

---

### 6. **Complaints** (`complaints` table)
Complaints are filed by citizens within a constituency.

```sql
CREATE TABLE complaints (
    id UUID PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    category VARCHAR,
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    ward_id UUID REFERENCES wards(id),
    citizen_id UUID REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    status VARCHAR,
    priority_score INTEGER,
    location_lat NUMERIC,
    location_lng NUMERIC,
    created_at TIMESTAMP
);
```

**Relationship**:
- **Constituency (1) → Complaints (Many)**
- **Ward (1) → Complaints (Many)**
- Complaints visible only within the constituency
- Assigned to officers within the same constituency

---

### 7. **Users** (`users` table)
Users are linked to constituencies based on their role.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    phone VARCHAR UNIQUE NOT NULL,
    role VARCHAR,  -- 'admin', 'mla', 'moderator', 'officer', 'citizen'
    constituency_id UUID REFERENCES constituencies(id),  -- ✅ LINKED
    ward_id UUID REFERENCES wards(id),  -- For citizens
    department_id UUID REFERENCES departments(id),  -- For officers
    created_at TIMESTAMP
);
```

**User-Constituency Relationships**:

| Role | Constituency Link | Access Scope |
|------|-------------------|--------------|
| **Admin** | None (NULL) | All constituencies |
| **MLA** | Their constituency | Own constituency only |
| **Moderator** | Specific constituency | Own constituency only |
| **Department Officer** | Via department → constituency | Own constituency only |
| **Citizen** | Specific constituency | Own constituency only |
| **Auditor** | Specific constituency | Own constituency (read-only) |

---

## Data Isolation & Access Control

### How Data is Filtered

**1. Automatic Filtering by Current User**:
```python
# In API endpoints
current_user = get_current_user()

if current_user.role == "mla" or current_user.role == "moderator":
    # Filter by user's constituency
    constituencies = db.query(Constituency).filter(
        Constituency.id == current_user.constituency_id
    ).all()
    
    wards = db.query(Ward).filter(
        Ward.constituency_id == current_user.constituency_id
    ).all()
    
    complaints = db.query(Complaint).filter(
        Complaint.constituency_id == current_user.constituency_id
    ).all()
```

**2. Admin Access (All Constituencies)**:
```python
if current_user.role == "admin":
    # No constituency filter - see everything
    all_constituencies = db.query(Constituency).all()
    all_wards = db.query(Ward).all()
    all_complaints = db.query(Complaint).all()
```

**3. Citizen Access (Own Constituency + Ward)**:
```python
if current_user.role == "citizen":
    # Filter by citizen's constituency and ward
    my_complaints = db.query(Complaint).filter(
        Complaint.citizen_id == current_user.id,
        Complaint.constituency_id == current_user.constituency_id
    ).all()
```

---

## API Endpoint Examples

### Get Wards for a Constituency
```http
GET /api/wards?constituency_id={constituency_id}

Response:
{
  "wards": [
    {
      "id": "ward-1-id",
      "name": "Ward 1 - Kadaba Circle",
      "ward_number": 1,
      "constituency_id": "puttur-constituency-id",
      "population": 5000
    },
    {
      "id": "ward-2-id",
      "name": "Ward 2 - Market Area",
      "ward_number": 2,
      "constituency_id": "puttur-constituency-id",
      "population": 7500
    }
  ]
}
```

### Get Departments for a Constituency
```http
GET /api/departments?constituency_id={constituency_id}

Response:
{
  "departments": [
    {
      "id": "dept-1-id",
      "name": "Roads & Transport",
      "constituency_id": "puttur-constituency-id",
      "head_officer_name": "John Doe",
      "phone": "+919876543210"
    }
  ]
}
```

### Create Poll (MLA Only)
```http
POST /api/polls

Body:
{
  "question": "Should we prioritize road repairs?",
  "options": ["Yes", "No", "Maybe"],
  "constituency_id": "puttur-constituency-id",  // Auto-filled from current user
  "ends_at": "2025-11-15T23:59:59Z"
}
```

---

## Current Test Data

### Constituencies (3)
1. **Puttur** - `constituency_id_1`
2. **Mangalore** - `constituency_id_2`
3. **Bantwal** - `constituency_id_3`

### Test Users (29 total)

| Role | Constituency | Count |
|------|-------------|-------|
| Admin | - | 1 |
| MLA | Puttur | 1 |
| MLA | Mangalore | 1 |
| MLA | Bantwal | 1 |
| Moderator | Puttur | 2 |
| Moderator | Mangalore | 2 |
| Moderator | Bantwal | 2 |
| Officer | Puttur | 3 |
| Officer | Mangalore | 3 |
| Officer | Bantwal | 3 |
| Auditor | Puttur | 1 |
| Auditor | Mangalore | 1 |
| Auditor | Bantwal | 1 |
| Citizen | Puttur | 2 |
| Citizen | Mangalore | 3 |
| Citizen | Bantwal | 2 |

---

## Adding New Constituencies

### Step 1: Create Constituency
```sql
INSERT INTO constituencies (id, name, code, state, district)
VALUES (
    gen_random_uuid(),
    'Udupi',
    'UDU',
    'Karnataka',
    'Udupi'
);
```

### Step 2: Create Wards for New Constituency
```sql
INSERT INTO wards (id, name, ward_number, constituency_id)
VALUES 
    (gen_random_uuid(), 'Ward 1 - City Center', 1, 'udupi-constituency-id'),
    (gen_random_uuid(), 'Ward 2 - Beach Area', 2, 'udupi-constituency-id');
```

### Step 3: Create Departments
```sql
INSERT INTO departments (id, name, constituency_id)
VALUES 
    (gen_random_uuid(), 'Roads & Transport', 'udupi-constituency-id'),
    (gen_random_uuid(), 'Water Supply', 'udupi-constituency-id');
```

### Step 4: Assign MLA
```sql
UPDATE users 
SET constituency_id = 'udupi-constituency-id'
WHERE id = 'mla-user-id';
```

---

## Frontend Implementation

### Constituency Selection
When a user logs in, their constituency is automatically determined:

```javascript
// Get current user's constituency
const { data: userData } = useQuery({
  queryKey: ['current-user'],
  queryFn: () => authAPI.getCurrentUser()
});

const constituencyId = userData?.data?.constituency_id;

// Use in API calls
const { data: wards } = useQuery({
  queryKey: ['wards', constituencyId],
  queryFn: () => axios.get(`/api/wards?constituency_id=${constituencyId}`)
});

const { data: departments } = useQuery({
  queryKey: ['departments', constituencyId],
  queryFn: () => axios.get(`/api/departments?constituency_id=${constituencyId}`)
});
```

### Admin View (All Constituencies)
```javascript
// Admin can switch between constituencies
const [selectedConstituency, setSelectedConstituency] = useState(null);

if (user.role === 'admin') {
  // Show constituency selector
  const { data: constituencies } = useQuery({
    queryKey: ['constituencies'],
    queryFn: () => axios.get('/api/constituencies')
  });
  
  // Filter data by selected constituency
  const filteredData = data.filter(
    item => item.constituency_id === selectedConstituency
  );
}
```

---

## Benefits of This Architecture

### 1. **Data Isolation**
- Each constituency's data is completely separate
- No cross-constituency data leaks
- Security through database-level foreign keys

### 2. **Scalability**
- Easy to add new constituencies without affecting existing ones
- Each constituency can have different numbers of wards, departments
- Can handle hundreds of constituencies in one system

### 3. **Customization**
- FAQs specific to each constituency
- Polls relevant to local issues
- Budget tracking per constituency

### 4. **Role-Based Access**
- MLAs see only their constituency
- Citizens see only their constituency
- Admin sees all constituencies
- Officers see only their constituency's department data

### 5. **Efficient Queries**
```sql
-- Always filtered by constituency_id for non-admins
SELECT * FROM complaints 
WHERE constituency_id = 'puttur-id' 
  AND status = 'pending';

-- Indexed for performance
CREATE INDEX idx_complaints_constituency 
ON complaints(constituency_id);
```

---

## Summary

**How Departments, Wards, Polls, etc. are Managed:**

1. ✅ **Every entity has `constituency_id` foreign key**
2. ✅ **Users are linked to constituencies via `constituency_id`**
3. ✅ **API automatically filters by user's constituency** (except admins)
4. ✅ **Database constraints ensure data integrity**
5. ✅ **Each constituency operates independently**
6. ✅ **Admin can view/manage all constituencies**

**Current Setup:**
- 3 constituencies (Puttur, Mangalore, Bantwal)
- 29 test users across all roles
- All tables have constituency_id foreign keys
- Role-based access control implemented
- Multi-tenancy by design

This architecture supports unlimited constituencies in a single system while maintaining data isolation and security! 🎉
