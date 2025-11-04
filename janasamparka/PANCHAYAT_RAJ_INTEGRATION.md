# 🏛️ Panchayat Raj System Integration

## Overview

Integrated 3-tier **Panchayat Raj System** into Janasamparka for rural governance:

```
┌─────────────────────────────────────────────────────────────┐
│              PANCHAYAT RAJ HIERARCHY                        │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │ Zilla Panchayat  │ ◄─── District Level
                    │ (ZP President,   │      (Highest Tier)
                    │  CEO)            │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
     ┌──────▼──────┐  ┌──────▼──────┐  ┌─────▼───────┐
     │Taluk Panch. │  │Taluk Panch. │  │Taluk Panch. │ ◄─ Taluk/Block Level
     │(TP President,│  │(Puttur)     │  │(Kadaba)     │    (Middle Tier)
     │ EO)         │  └──────┬──────┘  └──────┬──────┘
     └─────────────┘         │                │
                    ┌────────┼────────┬───────┼───────┐
                    │        │        │       │       │
             ┌──────▼───┐ ┌──▼───┐ ┌─▼──┐ ┌──▼───┐ ┌─▼──┐
             │Gram Panch│ │GP-002│ │GP-3│ │GP-004│ │GP-5│ ◄─ Village Level
             │(PDO, VA, │ │      │ │    │ │      │ │    │    (Lowest Tier)
             │President)│ └──────┘ └────┘ └──────┘ └────┘
             └──────────┘
```

---

## 🏢 3-Tier Structure

### 1. **Zilla Panchayat (ZP)** - District Level
- **Scope**: Entire district (e.g., Dakshina Kannada)
- **Leadership**: 
  - ZP President (Elected)
  - Chief Executive Officer (CEO) - IAS Officer
- **Responsibilities**:
  - District-wide planning and coordination
  - Budget allocation to Taluk Panchayats
  - Monitor implementation of schemes
  - Coordinate with state government

### 2. **Taluk Panchayat (TP)** - Taluk/Block Level
- **Scope**: Taluk (e.g., Puttur Taluk, Kadaba Taluk)
- **Leadership**:
  - TP President (Elected)
  - Executive Officer (EO) - KAS Officer
- **Responsibilities**:
  - Taluk-level planning and coordination
  - Supervise Gram Panchayats
  - Implement government schemes at taluk level
  - Tax collection and revenue management

### 3. **Gram Panchayat (GP)** - Village Level
- **Scope**: Village or group of villages
- **Leadership**:
  - GP President (Elected)
  - Vice President (Elected)
  - **PDO (Panchayat Development Officer)** - Administrative head
  - **Village Accountant (VA)** - Revenue and tax officer
- **Responsibilities**:
  - Village-level governance
  - Issue certificates (birth, death, caste, income)
  - Collect property tax, water tax
  - Implement welfare schemes
  - Maintain village infrastructure

---

## 👥 Panchayat Raj Roles

### Administrative Roles

#### 1. **PDO (Panchayat Development Officer)**
- **Assignment**: Gram Panchayat level
- **Responsibilities**:
  - Overall administration of Gram Panchayat
  - Oversee progress of development works
  - Monitor scheme implementation
  - Coordinate with departments
  - Prepare reports and budgets
  - Secretary to GP meetings
- **Access**: Full visibility into assigned Gram Panchayat
- **Reports to**: Taluk Panchayat Officer

#### 2. **Village Accountant (VA)**
- **Assignment**: Gram Panchayat level (may cover multiple villages)
- **Responsibilities**:
  - Issue certificates (income, caste, domicile, nativity)
  - Maintain land records
  - Collect property tax, water tax, trade license fees
  - Update revenue records
  - Facilitate government schemes
  - Birth and death registration
- **Access**: Assigned Gram Panchayat(s)
- **Reports to**: PDO and Taluk Panchayat Officer

#### 3. **Taluk Panchayat Officer**
- **Assignment**: Taluk Panchayat level
- **Responsibilities**:
  - Coordinate all Gram Panchayats in taluk
  - Monitor PDOs and VAs
  - Implement taluk-level schemes
  - Budget preparation and allocation
  - Revenue supervision
- **Access**: All Gram Panchayats in assigned Taluk Panchayat
- **Reports to**: Zilla Panchayat Officer

#### 4. **Zilla Panchayat Officer**
- **Assignment**: Zilla Panchayat level
- **Responsibilities**:
  - District-wide coordination
  - Monitor all Taluk Panchayats
  - District planning and budgeting
  - Liaise with state government
  - Audit and compliance
- **Access**: All Taluk and Gram Panchayats in district
- **Reports to**: District Commissioner / CEO

### Elected Representatives

#### 5. **GP President (Gram Panchayat President)**
- **Assignment**: Gram Panchayat level
- **Responsibilities**:
  - Chair GP meetings
  - Village-level decision making
  - Represent villagers
  - Approve development works
- **Access**: Assigned Gram Panchayat
- **Elected by**: GP members (ward members)

#### 6. **TP President (Taluk Panchayat President)**
- **Assignment**: Taluk Panchayat level
- **Responsibilities**:
  - Chair TP meetings
  - Taluk-level policy decisions
  - Coordinate with Gram Panchayats
- **Access**: Assigned Taluk Panchayat and all its GPs
- **Elected by**: TP members

#### 7. **ZP President (Zilla Panchayat President)**
- **Assignment**: Zilla Panchayat level
- **Responsibilities**:
  - Chair ZP meetings
  - District-level leadership
  - Coordinate with state government
- **Access**: Entire district (all TPs and GPs)
- **Elected by**: ZP members

---

## 🗄️ Database Schema

### Zilla Panchayats Table
```sql
CREATE TABLE zilla_panchayats (
    id UUID PRIMARY KEY,
    name VARCHAR(255),           -- "Dakshina Kannada ZP"
    code VARCHAR(50) UNIQUE,     -- "ZP-DK-001"
    district VARCHAR(100),       -- "Dakshina Kannada"
    state VARCHAR(50),           -- "Karnataka"
    total_taluk_panchayats INT,
    total_gram_panchayats INT,
    total_population INT,
    president_name VARCHAR(255),
    chief_executive_officer_name VARCHAR(255),
    office_phone VARCHAR(15),
    office_email VARCHAR(255),
    office_address TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Taluk Panchayats Table
```sql
CREATE TABLE taluk_panchayats (
    id UUID PRIMARY KEY,
    name VARCHAR(255),               -- "Puttur Taluk Panchayat"
    code VARCHAR(50) UNIQUE,         -- "TP-PUT-001"
    zilla_panchayat_id UUID,         -- FK to Zilla Panchayat
    constituency_id UUID NOT NULL,   -- FK to Constituency
    taluk_name VARCHAR(100),         -- "Puttur"
    district VARCHAR(100),           -- "Dakshina Kannada"
    total_gram_panchayats INT,
    total_population INT,
    president_name VARCHAR(255),
    executive_officer_name VARCHAR(255),
    office_phone VARCHAR(15),
    ...
);
```

### Gram Panchayats Table
```sql
CREATE TABLE gram_panchayats (
    id UUID PRIMARY KEY,
    name VARCHAR(255),               -- "Bolwar Gram Panchayat"
    code VARCHAR(50) UNIQUE,         -- "GP-PUT-001"
    taluk_panchayat_id UUID,         -- FK to Taluk Panchayat
    constituency_id UUID NOT NULL,   -- FK to Constituency
    taluk_name VARCHAR(100),         -- "Puttur"
    district VARCHAR(100),           -- "Dakshina Kannada"
    population INT,
    households INT,
    villages_covered INT,
    president_name VARCHAR(255),
    vice_president_name VARCHAR(255),
    secretary_name VARCHAR(255),     -- PDO name
    office_phone VARCHAR(15),
    ...
);
```

### Users Table (Extended)
```sql
ALTER TABLE users
ADD COLUMN gram_panchayat_id UUID REFERENCES gram_panchayats(id);

ADD COLUMN taluk_panchayat_id UUID REFERENCES taluk_panchayats(id);

ADD COLUMN zilla_panchayat_id UUID REFERENCES zilla_panchayats(id);

-- New roles added to UserRole enum:
-- 'pdo', 'village_accountant', 'taluk_panchayat_officer', 
-- 'zilla_panchayat_officer', 'gp_president', 'tp_president', 'zp_president'
```

---

## 🔗 Integration with Existing System

### Hierarchy Relationships

```
Constituency (MLA)
  ├─ Taluk 1 (e.g., Puttur)
  │   ├─ Taluk Panchayat (TP-PUT-001)
  │   │   ├─ Gram Panchayat 1 (GP-PUT-001)
  │   │   │   ├─ PDO
  │   │   │   ├─ Village Accountant
  │   │   │   └─ GP President
  │   │   ├─ Gram Panchayat 2 (GP-PUT-002)
  │   │   └─ Gram Panchayat 3 (GP-PUT-003)
  │   └─ Urban Wards (existing ward system)
  │
  └─ Taluk 2 (e.g., Kadaba)
      ├─ Taluk Panchayat (TP-KAD-001)
      │   ├─ Gram Panchayat 1 (GP-KAD-001)
      │   └─ Gram Panchayat 2 (GP-KAD-002)
      └─ Urban Wards (if any)

Zilla Panchayat (District Level)
  ├─ Monitors all Taluk Panchayats in district
  └─ Coordinates with multiple constituencies
```

### Key Points
- **Gram Panchayats** belong to **rural areas** within a taluk
- **Wards** belong to **urban/municipal areas** (existing system)
- Both link to same **Constituency** (MLA jurisdiction)
- **MLA** oversees both urban (wards) and rural (panchayats) areas

---

## 📊 Role-Based Access Control

### Access Matrix

| Role                      | Level              | Access Scope                                    |
|---------------------------|--------------------|-------------------------------------------------|
| **Citizen**               | Village            | Own submissions in their GP/ward                |
| **PDO**                   | Gram Panchayat     | All submissions in assigned GP                  |
| **Village Accountant**    | Gram Panchayat     | All submissions in assigned GP(s)               |
| **GP President**          | Gram Panchayat     | All data in their GP (elected representative)   |
| **Taluk Panchayat Officer**| Taluk Panchayat   | All GPs in assigned TP                          |
| **TP President**          | Taluk Panchayat    | All data in TP and its GPs                      |
| **Zilla Panchayat Officer**| Zilla Panchayat   | All TPs and GPs in district                     |
| **ZP President**          | Zilla Panchayat    | All data in ZP, TPs, and GPs                    |
| **Department Officer**    | Constituency       | Assigned work in constituency (urban + rural)   |
| **MLA**                   | Constituency       | Full constituency (urban wards + rural GPs)     |
| **Admin**                 | System-wide        | All constituencies, panchayats, wards           |

### Filtering Logic

```python
# PDO/VA sees only their Gram Panchayat
if user.role in ['pdo', 'village_accountant', 'gp_president']:
    filter = gram_panchayat_id == user.gram_panchayat_id

# Taluk Panchayat Officer sees all GPs in their TP
if user.role in ['taluk_panchayat_officer', 'tp_president']:
    filter = taluk_panchayat_id == user.taluk_panchayat_id

# Zilla Panchayat Officer sees all TPs and GPs in district
if user.role in ['zilla_panchayat_officer', 'zp_president']:
    filter = zilla_panchayat_id == user.zilla_panchayat_id

# MLA sees entire constituency (urban + rural)
if user.role == 'mla':
    filter = constituency_id == user.constituency_id

# Admin sees everything
if user.role == 'admin':
    filter = None  # No filtering
```

---

## 🎯 Use Cases

### 1. Citizen Submits Request to Gram Panchayat

**Scenario**: Villager needs birth certificate

```
1. Citizen logs in → Assigned to GP
2. Submits request: "Need birth certificate"
3. Request auto-assigned to:
   - Village Accountant (VA) of that GP
   - PDO gets notification
4. VA processes → Issues certificate
5. PDO monitors completion
6. Citizen receives notification
```

**Data Flow**:
```sql
INSERT INTO complaints (
  title: "Birth certificate needed",
  constituency_id: puttur_constituency,
  gram_panchayat_id: bolwar_gp,
  user_id: citizen_id,
  assigned_to: village_accountant_id
);
```

### 2. PDO Monitors Development Works

**Scenario**: PDO tracks progress of road repair

```
1. PDO logs in → Dashboard shows assigned GP
2. Sees all complaints/requests from GP villages
3. Assigns work to department officer
4. Monitors progress
5. Updates completion status
6. Generates report for TP Officer
```

**Dashboard Query**:
```sql
SELECT * FROM complaints
WHERE gram_panchayat_id = pdo_user.gram_panchayat_id
AND status IN ('submitted', 'in_progress');
```

### 3. Village Accountant Issues Certificate

**Scenario**: VA issues income certificate

```
1. VA logs in → Sees certificate requests
2. Filters by type: "Income Certificate"
3. Verifies documents
4. Generates certificate
5. Collects fee (tax)
6. Updates status: "Completed"
7. Citizen receives SMS notification
```

### 4. Taluk Panchayat Officer Oversees Multiple GPs

**Scenario**: TP Officer monitors tax collection

```
1. TP Officer logs in → Dashboard shows all GPs in taluk
2. Views tax collection report:
   - GP-PUT-001: ₹2.5 lakhs
   - GP-PUT-002: ₹1.8 lakhs
   - GP-PUT-003: ₹2.1 lakhs
3. Identifies underperforming GPs
4. Sends reminder to PDOs/VAs
5. Generates taluk-wide report for ZP
```

**Analytics Query**:
```sql
SELECT 
  gp.name,
  COUNT(c.id) as total_requests,
  SUM(c.tax_collected) as revenue
FROM gram_panchayats gp
LEFT JOIN complaints c ON c.gram_panchayat_id = gp.id
WHERE gp.taluk_panchayat_id = tp_officer.taluk_panchayat_id
GROUP BY gp.id;
```

### 5. MLA Views Both Urban and Rural Areas

**Scenario**: MLA reviews constituency-wide issues

```
1. MLA logs in → Dashboard shows:
   - Urban wards: 35 wards (Puttur town)
   - Rural GPs: 25 Gram Panchayats
2. Views combined analytics:
   - Urban complaints: 45
   - Rural complaints: 78
3. Filters by priority/category
4. Compares urban vs rural development
```

---

## 🚀 Sample Data (Puttur Constituency)

### Zilla Panchayat
```
Dakshina Kannada Zilla Panchayat
├─ District: Dakshina Kannada
├─ President: Meenakshi Shanthigodu
├─ CEO: Dr. Kumar R.
└─ Total Population: 2,100,000
```

### Taluk Panchayats
```
1. Puttur Taluk Panchayat (TP-PUT-001)
   ├─ Taluk: Puttur
   ├─ Constituency: Puttur (PUT001)
   ├─ President: Rajesh Kumar
   ├─ Executive Officer: Suresh B.O.
   ├─ Total GPs: 25
   └─ Population: 145,000

2. Kadaba Taluk Panchayat (TP-KAD-001)
   ├─ Taluk: Kadaba
   ├─ Constituency: Puttur (PUT001)
   ├─ President: Savitha Rao
   ├─ Executive Officer: Prakash M.
   ├─ Total GPs: 18
   └─ Population: 95,000
```

### Gram Panchayats (Sample)

**Under Puttur Taluk:**
```
1. Bolwar GP (GP-PUT-001)
   ├─ Villages: 3 villages
   ├─ Population: 8,500
   ├─ Households: 1,800
   ├─ President: Manoj Shetty
   └─ PDO: Ramesh

2. Kabaka GP (GP-PUT-002)
   ├─ Villages: 2 villages
   ├─ Population: 6,200
   ├─ Households: 1,300
   ├─ President: Suma Bhat
   └─ PDO: Ganesh

3. Parladka GP (GP-PUT-003)
   ├─ Villages: 2 villages
   ├─ Population: 5,800
   ├─ Households: 1,200
   ├─ President: Krishna Rao
   └─ PDO: Mohan
```

**Under Kadaba Taluk:**
```
4. Nettanige Mudnur GP (GP-KAD-001)
   ├─ Villages: 3 villages
   ├─ Population: 7,200
   ├─ Households: 1,500
   ├─ President: Vasanth Kumar
   └─ PDO: Sunil

5. Kodimbala GP (GP-KAD-002)
   ├─ Villages: 2 villages
   ├─ Population: 5,500
   ├─ Households: 1,100
   ├─ President: Meena Shetty
   └─ PDO: Ravi
```

---

## 🔧 Implementation Steps

### 1. Run Migration
```bash
docker exec -i janasamparka_db psql -U janasamparka -d janasamparka_db \
  -f /path/to/add_panchayat_raj_system.sql
```

### 2. Create Panchayat Users
```sql
-- Create PDO for Bolwar GP
INSERT INTO users (name, phone, role, constituency_id, gram_panchayat_id)
VALUES (
  'Ramesh PDO',
  '+918242220001',
  'pdo',
  (SELECT id FROM constituencies WHERE code = 'PUT001'),
  (SELECT id FROM gram_panchayats WHERE code = 'GP-PUT-001')
);

-- Create Village Accountant
INSERT INTO users (name, phone, role, constituency_id, gram_panchayat_id)
VALUES (
  'Suresh VA',
  '+918242220002',
  'village_accountant',
  (SELECT id FROM constituencies WHERE code = 'PUT001'),
  (SELECT id FROM gram_panchayats WHERE code = 'GP-PUT-001')
);

-- Create Taluk Panchayat Officer
INSERT INTO users (name, phone, role, constituency_id, taluk_panchayat_id)
VALUES (
  'Kumar TP Officer',
  '+918242220100',
  'taluk_panchayat_officer',
  (SELECT id FROM constituencies WHERE code = 'PUT001'),
  (SELECT id FROM taluk_panchayats WHERE code = 'TP-PUT-001')
);
```

### 3. Update Frontend for Panchayat Roles

Create dashboards for:
- PDO Dashboard
- Village Accountant Dashboard
- Taluk Panchayat Officer Dashboard
- GP/TP/ZP President Dashboards

### 4. Update Complaint/Submission Routing

Add panchayat-based routing:
```javascript
// Auto-assign to PDO/VA based on citizen's GP
if (citizen.gram_panchayat_id) {
  complaint.gram_panchayat_id = citizen.gram_panchayat_id;
  complaint.assigned_to = getPDO(citizen.gram_panchayat_id);
}
```

---

## 📝 Next Steps

1. ✅ Database schema created
2. ✅ Migration script ready
3. ⏳ Create Panchayat user roles
4. ⏳ Build PDO/VA dashboards
5. ⏳ Add panchayat filtering to APIs
6. ⏳ Create certificate issuance workflow
7. ⏳ Add tax collection module
8. ⏳ Build panchayat analytics

---

**Status**: ✅ Schema Ready, Awaiting Migration  
**Next Action**: Run migration script to create panchayat tables  
**Documentation**: Complete
