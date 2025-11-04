# Department Jurisdiction System - Complete Implementation

**Date**: October 30, 2025  
**Status**: ✅ Backend Complete  
**Purpose**: Ensure geographical isolation - Puttur PWD ≠ Mangalore PWD

---

## Problem Statement

**User Question**: 
> "When a complaint in a Puttur TP ward is assigned to the Puttur PWD department, how do we ensure it doesn't get assigned to the Mangalore PWD department?"

**Answer**: Add **jurisdiction fields** to departments to link them to specific GP/TP/Corporation levels.

---

## Solution Overview

### Database Changes

**Migration**: `e300c119a978_add_jurisdiction_to_departments.py`

Added 4 jurisdiction fields to `departments` table:
- `gram_panchayat_id` → For GP-level departments (e.g., Anjegundi GP PWD)
- `taluk_panchayat_id` → For TP-level departments (e.g., Puttur TP PWD)
- `zilla_panchayat_id` → For ZP-level departments (e.g., Dakshina Kannada ZP Planning)
- `city_corporation_id` → For urban departments (e.g., Mangalore Corp PWD)

**Mutually Exclusive**: Only one jurisdiction field should be set per department.

### Updated Models

#### Department Model
```python
class Department(Base):
    __tablename__ = "departments"
    
    id: UUID
    name: str  # "Public Works Department"
    code: str  # "PWD"
    constituency_id: UUID  # MLA constituency
    
    # JURISDICTION: Department serves ONE of these levels
    gram_panchayat_id: Optional[UUID]       # Rural GP level
    taluk_panchayat_id: Optional[UUID]      # Town Panchayat level
    zilla_panchayat_id: Optional[UUID]      # District level
    city_corporation_id: Optional[UUID]     # Urban corporation level
```

#### Ward Model (Already Has Links)
```python
class Ward(Base):
    __tablename__ = "wards"
    
    id: UUID
    name: str
    ward_type: str  # 'gram_panchayat', 'taluk_panchayat', 'city_corporation'
    
    # Ward belongs to ONE of these
    gram_panchayat_id: Optional[UUID]
    taluk_panchayat_id: Optional[UUID]
    city_corporation_id: Optional[UUID]
```

---

## Jurisdiction Matching Logic

### Updated: `ward_assign_to_department()`

**File**: `/backend/app/services/complaint_routing.py`

```python
def ward_assign_to_department(
    db: Session,
    complaint: Complaint,
    dept_id: UUID,
    ward_officer_id: UUID,
    public_note: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Ward officer assigns complaint to department.
    
    JURISDICTION VALIDATION:
    - Ward in Puttur GP → Only Puttur GP departments
    - Ward in Puttur TP → Only Puttur TP departments  
    - Ward in Mangalore City Corp → Only Mangalore Corp departments
    """
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        return False, "Department not found"
    
    ward = db.query(Ward).filter(Ward.id == complaint.ward_id).first()
    if not ward:
        return False, "Ward not found"
    
    # JURISDICTION CHECK: Department must match ward's parent body
    jurisdiction_match = False
    error_msg = "Department jurisdiction mismatch"
    
    if ward.gram_panchayat_id:
        if dept.gram_panchayat_id == ward.gram_panchayat_id:
            jurisdiction_match = True
        else:
            error_msg = "This department does not serve the ward's Gram Panchayat"
    
    elif ward.taluk_panchayat_id:
        if dept.taluk_panchayat_id == ward.taluk_panchayat_id:
            jurisdiction_match = True
        else:
            error_msg = "This department does not serve the ward's Taluk Panchayat"
    
    elif ward.city_corporation_id:
        if dept.city_corporation_id == ward.city_corporation_id:
            jurisdiction_match = True
        else:
            error_msg = "This department does not serve the ward's City Corporation"
    
    if not jurisdiction_match:
        return False, error_msg
    
    # Assignment proceeds...
    complaint.assignment_type = "department"
    complaint.dept_id = dept_id
    complaint.ward_officer_id = ward_officer_id
    
    # Add public note...
    return True, None
```

**Key Feature**: Returns `Tuple[bool, Optional[str]]` with descriptive error message.

---

## New API Endpoints

### 1. Get Available Departments for Ward

**Endpoint**: `GET /api/complaints/ward/{ward_id}/available-departments`

**Purpose**: Ward officers see only departments in their jurisdiction when assigning complaints.

**Authorization**: Ward officers only, must be assigned to the specified ward.

**Example Request**:
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/complaints/ward/abc123/available-departments
```

**Example Response**:
```json
[
  {
    "id": "dept-uuid-1",
    "name": "Puttur Public Works Department",
    "code": "PWD",
    "description": "Handles road construction, building maintenance",
    "contact_phone": "+91-8251-234567",
    "contact_email": "puttur.pwd@example.com"
  },
  {
    "id": "dept-uuid-2",
    "name": "Puttur Electricity Department",
    "code": "ELEC",
    "description": "Power supply issues",
    "contact_phone": "+91-8251-234568",
    "contact_email": "puttur.elec@example.com"
  }
]
```

**Logic**:
```python
if ward.gram_panchayat_id:
    query = query.filter(Department.gram_panchayat_id == ward.gram_panchayat_id)
elif ward.taluk_panchayat_id:
    query = query.filter(Department.taluk_panchayat_id == ward.taluk_panchayat_id)
elif ward.city_corporation_id:
    query = query.filter(Department.city_corporation_id == ward.city_corporation_id)
```

### 2. Get Department Complaints (Department View)

**Endpoint**: `GET /api/complaints/my-department`

**Purpose**: Department officers see all complaints assigned to their department (not just individually assigned).

**Authorization**: Department officers only.

**Query Parameters**:
- `status` - Filter by complaint status
- `category` - Filter by category
- `search` - Text search
- `page`, `page_size` - Pagination

**Example Request**:
```bash
curl -H "Authorization: Bearer <dept_officer_token>" \
  "http://localhost:8000/api/complaints/my-department?status=ASSIGNED&page=1&page_size=20"
```

**Example Response**:
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "complaints": [
    {
      "id": "complaint-uuid-1",
      "title": "Pothole on Main Road",
      "status": "ASSIGNED",
      "ward_id": "ward-uuid",
      "dept_id": "dept-uuid",
      "assigned_to": null,
      "public_notes": "[2025-10-30 10:30] Ward Officer: Road issue, needs immediate attention",
      "internal_notes": "[2025-10-30 10:31] Dept Head: Budget available, assign to team"
    }
  ]
}
```

**Difference from `/my-assigned`**:
- `/my-assigned` - Individual officer's assigned complaints
- `/my-department` - All complaints in the department

---

## Updated Workflow

### Complete Flow with Jurisdiction

```
1. Citizen submits complaint
   ↓
   assignment_type = "ward"
   ward_id = <citizen's ward>

2. Ward Officer logs in
   ↓
   GET /my-ward → Sees all complaints in their ward
   ↓
   GET /ward/{ward_id}/available-departments → Sees ONLY departments in jurisdiction
   
   Example: Ward in Puttur TP
   - ✅ Shows: Puttur PWD, Puttur Electricity, Puttur Water Supply
   - ❌ Hides: Mangalore PWD, Mangalore Electricity

3. Ward Officer assigns to department
   ↓
   POST /{complaint_id}/ward-assign
   Body: { "dept_id": "puttur-pwd-uuid", "public_note": "Road damage needs repair" }
   ↓
   Backend validates:
   - ✅ ward.taluk_panchayat_id == dept.taluk_panchayat_id (Both Puttur TP)
   - ❌ If dept is Mangalore PWD: Returns 400 "Department jurisdiction mismatch"
   
4. Department Officer (Puttur PWD)
   ↓
   GET /my-department → Sees all Puttur PWD complaints
   ↓
   Only sees complaints from wards in Puttur TP
   ↓
   Assigns to specific officer
   ↓
   POST /{complaint_id}/assign → Sets assigned_to field

5. Individual Officer
   ↓
   GET /my-assigned → Sees their personal complaints
   ↓
   Adds public/internal notes, updates status
```

---

## Example Scenarios

### Scenario 1: Rural Gram Panchayat

**Ward**: Anjegundi Ward 5 (under Anjegundi Gram Panchayat)  
**Departments Available**:
- Anjegundi GP PWD (gram_panchayat_id = Anjegundi GP)
- Anjegundi GP Water Supply (gram_panchayat_id = Anjegundi GP)

**Blocked**:
- Puttur TP PWD (taluk_panchayat_id = Puttur TP)
- Mangalore Corp PWD (city_corporation_id = Mangalore)

### Scenario 2: Town Panchayat

**Ward**: Puttur Ward 12 (under Puttur Taluk Panchayat)  
**Departments Available**:
- Puttur TP PWD (taluk_panchayat_id = Puttur TP)
- Puttur TP Electricity (taluk_panchayat_id = Puttur TP)
- Puttur TP Health (taluk_panchayat_id = Puttur TP)

**Blocked**:
- Anjegundi GP PWD (gram_panchayat_id = Anjegundi GP)
- Mangalore Corp PWD (city_corporation_id = Mangalore)

### Scenario 3: City Corporation

**Ward**: Mangalore Ward 35 (under Mangalore City Corporation)  
**Departments Available**:
- Mangalore PWD (city_corporation_id = Mangalore)
- Mangalore Water Authority (city_corporation_id = Mangalore)
- Mangalore Solid Waste Management (city_corporation_id = Mangalore)

**Blocked**:
- Puttur TP PWD (taluk_panchayat_id = Puttur TP)
- Anjegundi GP PWD (gram_panchayat_id = Anjegundi GP)

---

## Database Seed Data Examples

### Create Departments with Jurisdiction

```sql
-- Puttur TP PWD
INSERT INTO departments (id, name, code, constituency_id, taluk_panchayat_id)
VALUES (
  gen_random_uuid(),
  'Puttur Public Works Department',
  'PWD',
  '<puttur_constituency_uuid>',
  '<puttur_tp_uuid>'
);

-- Mangalore Corp PWD (Different jurisdiction!)
INSERT INTO departments (id, name, code, constituency_id, city_corporation_id)
VALUES (
  gen_random_uuid(),
  'Mangalore Public Works Department',
  'PWD',
  '<mangalore_constituency_uuid>',
  '<mangalore_corp_uuid>'
);

-- Anjegundi GP PWD (GP-level)
INSERT INTO departments (id, name, code, constituency_id, gram_panchayat_id)
VALUES (
  gen_random_uuid(),
  'Anjegundi Gram Panchayat PWD',
  'PWD',
  '<constituency_uuid>',
  '<anjegundi_gp_uuid>'
);
```

**Result**: Three separate PWD departments, each serving different jurisdictions.

---

## Testing Checklist

### 1. Jurisdiction Validation
- [ ] Ward in Puttur TP + Puttur TP PWD → ✅ Success
- [ ] Ward in Puttur TP + Mangalore PWD → ❌ 400 Error "Department jurisdiction mismatch"
- [ ] Ward in Anjegudi GP + Anjegundi GP PWD → ✅ Success
- [ ] Ward in Anjegudi GP + Puttur TP PWD → ❌ 400 Error

### 2. Available Departments Endpoint
- [ ] Ward officer in Puttur ward sees only Puttur TP departments
- [ ] Ward officer in Mangalore ward sees only Mangalore Corp departments
- [ ] Ward officer cannot access departments for other wards
- [ ] Response includes all department details (name, code, description, contact)

### 3. Department Dashboard
- [ ] Puttur PWD officer sees only complaints from Puttur TP wards
- [ ] Mangalore PWD officer sees only complaints from Mangalore wards
- [ ] Department head sees unassigned + assigned complaints
- [ ] Individual officer (GET /my-assigned) sees only their complaints

### 4. Error Messages
- [ ] Jurisdiction mismatch returns clear error: "This department does not serve the ward's Taluk Panchayat"
- [ ] Department not found: "Department not found"
- [ ] Ward not linked to parent: "Ward has no parent panchayat/corporation assigned"

---

## Frontend Integration

### Ward Officer Dashboard Component

```typescript
// Get available departments for the ward
const { data: departments } = useQuery({
  queryKey: ['ward-departments', wardId],
  queryFn: () => 
    fetch(`/api/complaints/ward/${wardId}/available-departments`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.json())
});

// Assignment form
const assignToDepartment = async (complaintId: string, deptId: string, note: string) => {
  try {
    const response = await fetch(`/api/complaints/${complaintId}/ward-assign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        dept_id: deptId,
        public_note: note  // Required: explain why this department
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      alert(error.detail);  // "Department jurisdiction mismatch"
      return;
    }
    
    const result = await response.json();
    alert(`Assigned to ${result.assigned_department}`);
  } catch (error) {
    console.error('Assignment failed:', error);
  }
};
```

### Department Dropdown (Jurisdiction-Filtered)

```tsx
<Select label="Assign to Department" required>
  {departments?.map(dept => (
    <option key={dept.id} value={dept.id}>
      {dept.name} - {dept.code}
    </option>
  ))}
</Select>
<TextArea 
  label="Public Note (visible to citizen)" 
  placeholder="Explain why you're assigning to this department"
  minLength={10}
  maxLength={500}
  required
/>
```

---

## Migration Applied

**File**: `/backend/alembic/versions/e300c119a978_add_jurisdiction_to_departments.py`

### Upgrade
```python
def upgrade():
    # Add 4 jurisdiction fields
    op.add_column('departments', sa.Column('gram_panchayat_id', sa.UUID(), nullable=True))
    op.add_column('departments', sa.Column('taluk_panchayat_id', sa.UUID(), nullable=True))
    op.add_column('departments', sa.Column('zilla_panchayat_id', sa.UUID(), nullable=True))
    op.add_column('departments', sa.Column('city_corporation_id', sa.UUID(), nullable=True))
    
    # Foreign keys
    op.create_foreign_key('fk_departments_gram_panchayat', 
                          'departments', 'gram_panchayats',
                          ['gram_panchayat_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_departments_taluk_panchayat',
                          'departments', 'taluk_panchayats',
                          ['taluk_panchayat_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_departments_zilla_panchayat',
                          'departments', 'zilla_panchayats',
                          ['zilla_panchayat_id'], ['id'], ondelete='CASCADE')
    
    # Indexes for fast filtering
    op.create_index('ix_departments_gram_panchayat_id', 'departments', ['gram_panchayat_id'])
    op.create_index('ix_departments_taluk_panchayat_id', 'departments', ['taluk_panchayat_id'])
    op.create_index('ix_departments_zilla_panchayat_id', 'departments', ['zilla_panchayat_id'])
    op.create_index('ix_departments_city_corporation_id', 'departments', ['city_corporation_id'])
```

**Status**: ✅ Applied successfully  
**Revision**: `79bec4cadb9f -> e300c119a978`

---

## Key Benefits

### 1. **Geographical Isolation**
- Puttur PWD and Mangalore PWD are completely separate entities
- Each serves only their jurisdiction

### 2. **Data Integrity**
- Enforced at database level with foreign keys
- Enforced at business logic level in routing service
- Enforced at API level in endpoints

### 3. **User Experience**
- Ward officers see only relevant departments (no clutter)
- No confusion about which PWD to assign to
- Clear error messages if jurisdiction mismatch

### 4. **Scalability**
- Works for 3-tier system: GP → TP → ZP
- Works for urban areas: City Corporations
- Easy to add more jurisdiction types later

---

## Summary

**Problem**: Complaint in Puttur assigned to wrong PWD department (Mangalore PWD)

**Solution**: 
1. ✅ Added jurisdiction fields to Department model
2. ✅ Created migration to add FK constraints
3. ✅ Updated `ward_assign_to_department()` with validation
4. ✅ Added `/ward/{id}/available-departments` endpoint
5. ✅ Added `/my-department` endpoint for department officers
6. ✅ Backend restarted successfully

**Result**: **Puttur PWD ≠ Mangalore PWD** (Enforced at multiple levels)

**Next Steps**:
1. Create seed data linking departments to GP/TP/Corporation
2. Build Ward Officer Dashboard (frontend)
3. Test complete workflow end-to-end
