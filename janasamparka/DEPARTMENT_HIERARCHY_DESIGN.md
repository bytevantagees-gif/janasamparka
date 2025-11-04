# Department Hierarchical Structure Design

## Problem Statement
Currently, departments are mixed: some are generic types (PWD, Water Supply) and some are taluk-specific instances (Puttur PWD, Puttur Electricity). This doesn't scale for state-wide deployment where each taluk needs its own department instances with dedicated heads.

## Proposed Structure

### 1. Department Types (State-Level)
**New table: `department_types`**
- id (UUID)
- name (e.g., "Public Works Department")
- code (e.g., "PWD")
- description
- icon
- color
- is_active
- created_at, updated_at

**Examples**:
- PWD (Public Works Department)
- WS (Water Supply & Drainage)
- HEALTH (Health & Sanitation)
- ELEC (Electricity)
- REVENUE (Revenue & Administration)
- EDUCATION (Education)
- AGRICULTURE (Agriculture)
- etc.

### 2. Department Instances (Taluk-Level)
**Existing table: `departments`** - Enhanced
- id (UUID)
- department_type_id (FK to department_types) **NEW**
- name (e.g., "Puttur PWD", "Bantwal Water Supply")
- code (inherited from type, can be overridden)
- constituency_id (FK)
- taluk_panchayat_id (FK) - Primary jurisdiction
- gram_panchayat_id (FK) - Optional for GP-specific depts
- zilla_panchayat_id (FK) - Optional for ZP-level depts
- city_corporation_id (FK) - Optional for city depts
- head_officer_id (FK to users) **NEW** - Department head
- contact_phone
- contact_email
- office_address **NEW**
- description
- is_active **NEW**
- created_at, updated_at

### 3. Hierarchy Example

```
Karnataka State
└── Department Type: PWD
    ├── Puttur Constituency
    │   ├── Puttur Taluk PWD (head: Officer A)
    │   └── Sullia Taluk PWD (head: Officer B)
    ├── Bantwal Constituency
    │   ├── Bantwal Taluk PWD (head: Officer C)
    │   └── Vittal Taluk PWD (head: Officer D)
    └── Mangalore City South Constituency
        └── Mangalore PWD (head: Officer E)
```

## Database Changes

### Step 1: Create department_types table
```sql
CREATE TABLE department_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_department_types_code ON department_types(code);
CREATE INDEX ix_department_types_is_active ON department_types(is_active);
```

### Step 2: Modify departments table
```sql
-- Add new columns
ALTER TABLE departments 
ADD COLUMN department_type_id UUID,
ADD COLUMN head_officer_id UUID,
ADD COLUMN office_address TEXT,
ADD COLUMN is_active BOOLEAN DEFAULT true;

-- Add foreign keys
ALTER TABLE departments
ADD CONSTRAINT fk_departments_type 
    FOREIGN KEY (department_type_id) 
    REFERENCES department_types(id);

ALTER TABLE departments
ADD CONSTRAINT fk_departments_head_officer 
    FOREIGN KEY (head_officer_id) 
    REFERENCES users(id);

-- Create indexes
CREATE INDEX ix_departments_type_id ON departments(department_type_id);
CREATE INDEX ix_departments_head_officer_id ON departments(head_officer_id);
CREATE INDEX ix_departments_is_active ON departments(is_active);
```

### Step 3: Migrate existing data
```sql
-- Insert department types from existing unique codes
INSERT INTO department_types (name, code, description)
SELECT DISTINCT 
    CASE 
        WHEN code = 'PWD' THEN 'Public Works Department'
        WHEN code = 'WS' OR code = 'WATER' THEN 'Water Supply & Drainage'
        WHEN code = 'ELEC' THEN 'Electricity Department'
        WHEN code = 'SAN' THEN 'Sanitation Department'
        WHEN code = 'ROADS' THEN 'Roads Department'
        WHEN code = 'HEALTH' THEN 'Health & Sanitation'
        WHEN code = 'REVENUE' THEN 'Revenue & Administration'
        WHEN code = 'EDUCATION' THEN 'Education Department'
        ELSE name
    END as name,
    code,
    description
FROM departments
WHERE code IS NOT NULL;

-- Link existing departments to types
UPDATE departments d
SET department_type_id = (
    SELECT id FROM department_types dt 
    WHERE dt.code = d.code
    LIMIT 1
);
```

## API Changes

### New Endpoints

#### Department Types
```
GET    /api/department-types/                  - List all department types
GET    /api/department-types/{id}              - Get specific type
POST   /api/department-types/                  - Create new type (admin only)
PUT    /api/department-types/{id}              - Update type (admin only)
DELETE /api/department-types/{id}              - Delete type (admin only)
```

#### Departments (Enhanced)
```
GET    /api/departments/?type_id={id}          - Filter by department type
GET    /api/departments/?taluk_panchayat_id={id} - Filter by taluk
GET    /api/departments/?constituency_id={id}  - Filter by constituency
GET    /api/departments/{id}/officers          - Get department officers
POST   /api/departments/{id}/assign-head       - Assign head officer
```

### Example API Responses

#### List Department Types
```json
{
  "total": 15,
  "items": [
    {
      "id": "uuid",
      "name": "Public Works Department",
      "code": "PWD",
      "description": "Handles infrastructure, roads, buildings",
      "icon": "construction",
      "color": "#FF6B35",
      "is_active": true,
      "instance_count": 45
    }
  ]
}
```

#### List Departments with Filters
```json
{
  "total": 3,
  "items": [
    {
      "id": "uuid",
      "name": "Puttur PWD",
      "department_type": {
        "id": "uuid",
        "name": "Public Works Department",
        "code": "PWD"
      },
      "constituency": {
        "id": "uuid",
        "name": "Puttur"
      },
      "taluk_panchayat": {
        "id": "uuid",
        "name": "Puttur Taluk Panchayat"
      },
      "head_officer": {
        "id": "uuid",
        "name": "Rajesh Kumar",
        "phone": "+919876543210"
      },
      "contact_phone": "+918242220001",
      "office_address": "PWD Office, Puttur, Karnataka",
      "is_active": true
    }
  ]
}
```

## Frontend Changes

### Departments Page - New Design

```
┌─────────────────────────────────────────────────────┐
│ Departments Management                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Filters:                                           │
│  [Department Type ▼] [Constituency ▼] [Taluk ▼]   │
│  [🔍 Search...]                                     │
│                                                     │
│  Statistics:                                        │
│  📊 15 Department Types | 🏢 87 Departments        │
│  👤 82 Department Heads Assigned                    │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Department Type View (Grouped)                     │
│                                                     │
│  🏗️ Public Works Department (PWD)                  │
│  └─ Puttur Taluk PWD                               │
│     Head: Rajesh Kumar | Phone: +919876543210     │
│     Office: PWD Office, Puttur                     │
│     Status: ✅ Active | Complaints: 15            │
│                                                     │
│  └─ Bantwal Taluk PWD                              │
│     Head: Suresh Rao | Phone: +919876543211       │
│     Office: PWD Office, Bantwal                    │
│     Status: ✅ Active | Complaints: 12            │
│                                                     │
│  💧 Water Supply & Drainage (WATER)                │
│  └─ Puttur Water Supply                            │
│     Head: Prakash Shetty | Phone: +919876543220   │
│     Office: Water Office, Puttur                   │
│     Status: ✅ Active | Complaints: 23            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Features
1. **Cascading Filters**:
   - Select Department Type → Shows all taluks with that dept
   - Select Constituency → Shows taluks in that constituency
   - Select Taluk → Shows departments in that taluk

2. **Grouped View**:
   - Group by Department Type
   - Expand/collapse each type
   - Show department instances under each type

3. **Quick Actions**:
   - Edit department details
   - Assign/change head officer
   - View complaints assigned to department
   - View department performance

4. **Add Department Dialog**:
   - Step 1: Select Department Type
   - Step 2: Select Jurisdiction (Taluk/GP/City)
   - Step 3: Assign Head Officer
   - Step 4: Add Contact Details

## Benefits

1. **Scalability**: Easy to add new taluks - just create department instances for each type
2. **Consistency**: All department types standardized at state level
3. **Clear Hierarchy**: State → Constituency → Taluk → Department → Head
4. **Reporting**: Can aggregate complaints by department type across all taluks
5. **Flexibility**: Can have taluk-level, GP-level, or city-level departments
6. **Assignment**: Clear ownership - each department has a designated head

## Implementation Steps

1. ✅ Design schema and API structure
2. ⏳ Create migration script for department_types table
3. ⏳ Migrate existing department data
4. ⏳ Add backend models and schemas
5. ⏳ Update backend routes with filters
6. ⏳ Create frontend hierarchical department page
7. ⏳ Update complaint assignment to use new structure
8. ⏳ Seed data with realistic department instances

## Next Steps
Execute migration, update backend models, then rebuild frontend page with cascading filters.
