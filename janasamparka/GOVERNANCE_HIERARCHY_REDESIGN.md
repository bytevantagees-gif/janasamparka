# Karnataka Governance Hierarchy Redesign

## Current Issues
1. ❌ City Corporations table doesn't exist (city_corporation_id is NULL in wards)
2. ❌ Town Municipalities not represented
3. ❌ Departments only at Taluk level, not at all administrative levels
4. ❌ Complaint assignment doesn't consider proper hierarchy
5. ❌ Ward ownership unclear (which entity owns which ward?)

## Proper Karnataka Governance Structure

```
State: Karnataka
│
├── Zilla Panchayat (District Level)
│   ├── Has: President, CEO, Office
│   ├── Owns: District-level departments (Health, Education, PWD, etc.)
│   │
│   ├── Taluk Panchayat (Sub-district/Taluk Level)
│   │   ├── Has: President, Executive Officer, Office
│   │   ├── Owns: Taluk-level departments
│   │   │
│   │   ├── Gram Panchayat (Village Level)
│   │   │   ├── Has: President, Vice President, Secretary
│   │   │   ├── Owns: GP-level wards (typically 10-20 wards)
│   │   │   ├── Owns: GP-level departments (Junior Engineer, Secretary, etc.)
│   │   │   └── Wards
│   │   │       ├── Ward Member (Elected)
│   │   │       └── Ward Officer (Staff)
│   │   │
│   │   └── Town Panchayat / Town Municipality (Urban areas within Taluk)
│   │       ├── Has: President, Chief Officer
│   │       ├── Owns: Municipal wards (typically 20-30)
│   │       ├── Owns: Municipal departments
│   │       └── Wards
│   │
│   └── City Corporation (Major Cities - outside Taluk hierarchy)
│       ├── Has: Mayor, Commissioner
│       ├── Owns: Corporation wards (50-60 for tier-2 cities)
│       ├── Owns: Corporation departments (larger scale)
│       └── Wards
│           ├── Corporator (Elected)
│           └── Ward Officer (Staff)
```

## Database Schema Changes Required

### 1. Create City Corporations Table

```sql
CREATE TABLE city_corporations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    
    -- Hierarchy
    constituency_id UUID NOT NULL REFERENCES constituencies(id),
    zilla_panchayat_id UUID REFERENCES zilla_panchayats(id),
    
    -- Location
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Karnataka',
    
    -- Stats
    total_wards INTEGER NOT NULL DEFAULT 0,
    total_population INTEGER NOT NULL DEFAULT 0,
    area_sq_km DECIMAL(10, 2),
    
    -- Leadership
    mayor_name VARCHAR(255),
    deputy_mayor_name VARCHAR(255),
    commissioner_name VARCHAR(255),
    
    -- Contact
    office_phone VARCHAR(20),
    office_email VARCHAR(255),
    office_address TEXT,
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT true,
    tier VARCHAR(10) CHECK (tier IN ('tier-1', 'tier-2', 'tier-3')),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_city_corporations_constituency ON city_corporations(constituency_id);
CREATE INDEX idx_city_corporations_zilla ON city_corporations(zilla_panchayat_id);
CREATE INDEX idx_city_corporations_active ON city_corporations(is_active);
```

### 2. Create Town Municipalities Table

```sql
CREATE TABLE town_municipalities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    
    -- Hierarchy (Town Municipalities are within Taluks)
    constituency_id UUID NOT NULL REFERENCES constituencies(id),
    taluk_panchayat_id UUID NOT NULL REFERENCES taluk_panchayats(id),
    zilla_panchayat_id UUID REFERENCES zilla_panchayats(id),
    
    -- Location
    taluk_name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Karnataka',
    
    -- Stats
    total_wards INTEGER NOT NULL DEFAULT 0,
    total_population INTEGER NOT NULL DEFAULT 0,
    area_sq_km DECIMAL(10, 2),
    
    -- Leadership
    president_name VARCHAR(255),
    vice_president_name VARCHAR(255),
    chief_officer_name VARCHAR(255),
    
    -- Contact
    office_phone VARCHAR(20),
    office_email VARCHAR(255),
    office_address TEXT,
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT true,
    municipality_class VARCHAR(20) CHECK (municipality_class IN ('Class-I', 'Class-II', 'Class-III')),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_town_muni_constituency ON town_municipalities(constituency_id);
CREATE INDEX idx_town_muni_taluk ON town_municipalities(taluk_panchayat_id);
CREATE INDEX idx_town_muni_zilla ON town_municipalities(zilla_panchayat_id);
CREATE INDEX idx_town_muni_active ON town_municipalities(is_active);
```

### 3. Update Wards Table

```sql
-- Add town_municipality_id foreign key
ALTER TABLE wards ADD COLUMN town_municipality_id UUID REFERENCES town_municipalities(id);
CREATE INDEX idx_wards_town_municipality ON wards(town_municipality_id);

-- Add ward officer fields
ALTER TABLE wards ADD COLUMN ward_officer_id UUID REFERENCES users(id);
ALTER TABLE wards ADD COLUMN ward_member_name VARCHAR(255); -- Elected representative
ALTER TABLE wards ADD COLUMN ward_member_phone VARCHAR(20);
ALTER TABLE wards ADD COLUMN ward_member_party VARCHAR(100);

-- Add constraints to ensure ward belongs to ONE entity
ALTER TABLE wards ADD CONSTRAINT check_ward_parent CHECK (
    (gram_panchayat_id IS NOT NULL AND taluk_panchayat_id IS NULL AND city_corporation_id IS NULL AND town_municipality_id IS NULL) OR
    (taluk_panchayat_id IS NOT NULL AND gram_panchayat_id IS NULL AND city_corporation_id IS NULL AND town_municipality_id IS NULL) OR
    (city_corporation_id IS NOT NULL AND gram_panchayat_id IS NULL AND taluk_panchayat_id IS NULL AND town_municipality_id IS NULL) OR
    (town_municipality_id IS NOT NULL AND gram_panchayat_id IS NULL AND taluk_panchayat_id IS NULL AND city_corporation_id IS NULL)
);
```

### 4. Update Departments Table

```sql
-- Add town_municipality_id
ALTER TABLE departments ADD COLUMN town_municipality_id UUID REFERENCES town_municipalities(id);
CREATE INDEX idx_departments_town_municipality ON departments(town_municipality_id);

-- Add level indicator
ALTER TABLE departments ADD COLUMN administrative_level VARCHAR(20) 
    CHECK (administrative_level IN ('state', 'zilla', 'taluk', 'gram_panchayat', 'town_municipality', 'city_corporation'));

-- Add constraint to ensure department belongs to ONE entity
ALTER TABLE departments ADD CONSTRAINT check_dept_parent CHECK (
    (zilla_panchayat_id IS NOT NULL AND taluk_panchayat_id IS NULL AND gram_panchayat_id IS NULL AND city_corporation_id IS NULL AND town_municipality_id IS NULL) OR
    (taluk_panchayat_id IS NOT NULL AND zilla_panchayat_id IS NULL AND gram_panchayat_id IS NULL AND city_corporation_id IS NULL AND town_municipality_id IS NULL) OR
    (gram_panchayat_id IS NOT NULL AND zilla_panchayat_id IS NULL AND taluk_panchayat_id IS NULL AND city_corporation_id IS NULL AND town_municipality_id IS NULL) OR
    (city_corporation_id IS NOT NULL AND zilla_panchayat_id IS NULL AND taluk_panchayat_id IS NULL AND gram_panchayat_id IS NULL AND town_municipality_id IS NULL) OR
    (town_municipality_id IS NOT NULL AND zilla_panchayat_id IS NULL AND taluk_panchayat_id IS NULL AND gram_panchayat_id IS NULL AND city_corporation_id IS NULL) OR
    (zilla_panchayat_id IS NULL AND taluk_panchayat_id IS NULL AND gram_panchayat_id IS NULL AND city_corporation_id IS NULL AND town_municipality_id IS NULL AND constituency_id IS NOT NULL) -- Constituency-level
);
```

### 5. Update Complaints Table

```sql
-- Add town_municipality_id
ALTER TABLE complaints ADD COLUMN town_municipality_id UUID REFERENCES town_municipalities(id);
ALTER TABLE complaints ADD COLUMN city_corporation_id UUID REFERENCES city_corporations(id);
CREATE INDEX idx_complaints_town_municipality ON complaints(town_municipality_id);
CREATE INDEX idx_complaints_city_corporation ON complaints(city_corporation_id);

-- Add fields to track assignment hierarchy
ALTER TABLE complaints ADD COLUMN assigned_entity_type VARCHAR(30)
    CHECK (assigned_entity_type IN ('ward', 'gram_panchayat', 'taluk_panchayat', 'town_municipality', 'city_corporation', 'zilla_panchayat', 'department'));
ALTER TABLE complaints ADD COLUMN assigned_entity_id UUID;

-- Add escalation tracking
ALTER TABLE complaints ADD COLUMN escalation_level INTEGER DEFAULT 0;
ALTER TABLE complaints ADD COLUMN can_escalate_to VARCHAR(30);
```

### 6. Create Administrative Hierarchy View

```sql
CREATE OR REPLACE VIEW administrative_hierarchy AS
SELECT 
    'zilla_panchayat' as entity_type,
    zp.id as entity_id,
    zp.name as entity_name,
    NULL::uuid as parent_id,
    'district' as level,
    zp.constituency_id,
    zp.district,
    zp.total_population as population
FROM zilla_panchayats zp
WHERE zp.is_active = true

UNION ALL

SELECT 
    'taluk_panchayat',
    tp.id,
    tp.name,
    tp.zilla_panchayat_id,
    'taluk',
    tp.constituency_id,
    tp.district,
    tp.total_population
FROM taluk_panchayats tp
WHERE tp.is_active = true

UNION ALL

SELECT 
    'gram_panchayat',
    gp.id,
    gp.name,
    gp.taluk_panchayat_id,
    'village',
    gp.constituency_id,
    gp.district,
    gp.population
FROM gram_panchayats gp
WHERE gp.is_active = true

UNION ALL

SELECT 
    'town_municipality',
    tm.id,
    tm.name,
    tm.taluk_panchayat_id,
    'town',
    tm.constituency_id,
    tm.district,
    tm.total_population
FROM town_municipalities tm
WHERE tm.is_active = true

UNION ALL

SELECT 
    'city_corporation',
    cc.id,
    cc.name,
    cc.zilla_panchayat_id,
    'city',
    cc.constituency_id,
    cc.district,
    cc.total_population
FROM city_corporations cc
WHERE cc.is_active = true;
```

## Complaint Assignment Logic

### Assignment Rules:

1. **Citizen Submits Complaint**
   - Selects Ward (or location auto-detects ward)
   - System identifies parent entity (GP/TM/CC)
   - Complaint assigned to ward officer first

2. **Ward Officer Assessment**
   - Can resolve directly (minor issues)
   - OR escalate to GP/TM/CC department
   - OR escalate to Taluk-level department
   - OR escalate to Zilla-level department

3. **Escalation Hierarchy**:
   ```
   Ward → Gram Panchayat Department → Taluk Department → Zilla Department
   Ward → Town Municipality Department → Taluk Department → Zilla Department
   Ward → City Corporation Department → Zilla Department
   ```

4. **Department Assignment Matrix**:

| Issue Type | Ward Level | GP/TM Level | Taluk Level | Zilla Level |
|------------|-----------|-------------|-------------|-------------|
| Street Light | ✅ | ✅ | ❌ | ❌ |
| Pothole (minor) | ✅ | ✅ | ❌ | ❌ |
| Road (major) | ❌ | ❌ | ✅ PWD | ✅ PWD |
| Water Supply | ✅ | ✅ | ✅ | ❌ |
| Drainage | ✅ | ✅ | ✅ | ❌ |
| Health | ❌ | ✅ PHC | ✅ CHC | ✅ District Hospital |
| Education | ❌ | ✅ Primary | ✅ High School | ✅ PU College |
| Electricity | ❌ | ❌ | ✅ MESCOM | ✅ MESCOM |
| Police | ❌ | ❌ | ✅ Station | ✅ District HQ |

## Implementation Priority

### Phase 1: Database Schema (TODAY)
1. ✅ Create city_corporations table
2. ✅ Create town_municipalities table
3. ✅ Update wards table with constraints
4. ✅ Update departments table
5. ✅ Update complaints table
6. ✅ Create administrative_hierarchy view

### Phase 2: Seed Data (TODAY)
1. Create 2-3 City Corporations (Mangalore, Udupi, Karwar)
2. Create 4-5 Town Municipalities
3. Link existing 21 city_corporation wards to actual corporations
4. Create departments at all levels
5. Update ward_type values correctly

### Phase 3: Backend API (TODAY)
1. City Corporations CRUD
2. Town Municipalities CRUD
3. Update Departments API with level filtering
4. Update Wards API with proper parent filtering
5. Complaint assignment logic with hierarchy
6. Escalation API

### Phase 4: Frontend (TODAY)
1. City Corporations management page
2. Town Municipalities management page
3. Hierarchical department view (by level)
4. Complaint assignment UI with hierarchy selector
5. Escalation UI

### Phase 5: Complaint Workflow (TOMORROW)
1. Smart assignment based on issue type and location
2. Auto-escalation after timeout
3. Department routing based on capacity
4. Performance tracking by administrative level

## Benefits

1. **Clear Hierarchy**: Every ward, department, complaint knows its parent entity
2. **Proper Escalation**: Complaints can be escalated through proper channels
3. **Accurate Reporting**: Analytics by GP/TM/CC/Taluk/Zilla levels
4. **Citizen Clarity**: Citizens know which body is responsible
5. **Scalability**: Can add more cities, towns, GPs easily
6. **Compliance**: Matches Karnataka Panchayat Raj Act structure

## Next Steps

Would you like me to:
1. **Execute Phase 1** (Database schema changes) - Create tables and constraints
2. **Execute Phase 2** (Seed data) - Create sample corporations, municipalities, link wards
3. **Execute Phase 3** (Backend APIs) - Build CRUD for new entities
4. **All of the above** - Complete end-to-end implementation

Choose an option and I'll implement it immediately!
