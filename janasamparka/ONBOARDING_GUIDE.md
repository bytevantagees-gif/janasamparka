# 🚀 Multi-Constituency Onboarding Guide

## Quick Answer: How Multi-Constituency Works

✅ **Shared Database** - All constituencies use the same PostgreSQL database  
✅ **Tenant Isolation** - Each record has a `constituency_id` foreign key  
✅ **User Assignment** - Users belong to one constituency  
✅ **Admin Access** - Super admins can access all constituencies  
✅ **Scalable** - Supports 100+ constituencies on single database  

---

## 📋 Onboarding New Constituency - Step by Step

### **Step 1: Create Constituency Record**

```python
# Via Python/API
from app.models import Constituency
from app.core.database import SessionLocal

db = SessionLocal()

mangalore = Constituency(
    name="Mangalore North",
    code="MNG001",
    district="Dakshina Kannada",
    state="Karnataka",
    mla_name="B.A. Mohiuddin Bava",
    mla_party="Congress",
    mla_contact_phone="+919876543210",
    mla_contact_email="bava@karnataka.gov.in",
    assembly_number=129,
    total_wards=45,
    is_active=True,
    subscription_tier="premium"
)
db.add(mangalore)
db.commit()

print(f"Created constituency: {mangalore.id}")
```

### **Step 2: Add Wards for the Constituency**

```python
# Add wards
wards_data = [
    {"name": "Ward 1 - Kadri", "ward_number": 1, "taluk": "Mangalore", "population": 5000},
    {"name": "Ward 2 - Pandeshwar", "ward_number": 2, "taluk": "Mangalore", "population": 6000},
    # ... more wards
]

for ward_data in wards_data:
    ward = Ward(
        **ward_data,
        constituency_id=mangalore.id
    )
    db.add(ward)

db.commit()
```

### **Step 3: Create Departments**

```python
# Add departments for the constituency
departments = [
    {"name": "Public Works Department", "code": "PWD"},
    {"name": "Water Supply", "code": "WATER"},
    {"name": "Electricity", "code": "BESCOM"},
    {"name": "Health & Sanitation", "code": "HEALTH"},
]

for dept_data in departments:
    dept = Department(
        **dept_data,
        constituency_id=mangalore.id
    )
    db.add(dept)

db.commit()
```

### **Step 4: Create MLA User Account**

```python
# Create MLA user
mla_user = User(
    name="B.A. Mohiuddin Bava",
    phone="+919876543210",
    role=UserRole.MLA,
    constituency_id=mangalore.id,
    locale_pref="kn"
)
db.add(mla_user)
db.commit()
```

### **Step 5: Create Department Officer Accounts**

```python
# Create department officers
pwd_officer = User(
    name="Ramesh Kumar",
    phone="+919876543211",
    role=UserRole.DEPARTMENT_OFFICER,
    constituency_id=mangalore.id
)
db.add(pwd_officer)
db.commit()
```

---

## 🔄 Citizen Registration Flow

### **Option 1: GPS-Based Auto-Assignment**

```python
@router.post("/register")
async def register_user(
    phone: str,
    lat: float,
    lng: float,
    db: Session = Depends(get_db)
):
    # Find ward from coordinates
    ward = db.query(Ward).filter(
        func.ST_Contains(Ward.geom, func.ST_Point(lng, lat))
    ).first()
    
    if not ward:
        raise HTTPException(status_code=400, detail="Location not in any ward")
    
    # Create user with auto-assigned constituency
    user = User(
        phone=phone,
        constituency_id=ward.constituency_id,
        role=UserRole.CITIZEN
    )
    db.add(user)
    db.commit()
    
    return {"user_id": user.id, "constituency": ward.constituency_id}
```

### **Option 2: Manual Selection**

```python
@router.get("/constituencies")
async def list_active_constituencies(db: Session = Depends(get_db)):
    """Get list of active constituencies for selection"""
    constituencies = db.query(Constituency)\
        .filter(Constituency.is_active == True)\
        .all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "district": c.district,
            "mla_name": c.mla_name
        }
        for c in constituencies
    ]

@router.post("/register")
async def register_user(
    phone: str,
    constituency_id: UUID,
    db: Session = Depends(get_db)
):
    user = User(
        phone=phone,
        constituency_id=constituency_id,
        role=UserRole.CITIZEN
    )
    db.add(user)
    db.commit()
    
    return user
```

---

## 🎯 Example: 3 Constituencies Setup

```python
# Constituency 1: Puttur
puttur = Constituency(
    name="Puttur", code="PUT001", 
    district="Dakshina Kannada",
    mla_name="Ashok Kumar Rai"
)

# Constituency 2: Mangalore North  
mangalore_n = Constituency(
    name="Mangalore North", code="MNG001",
    district="Dakshina Kannada", 
    mla_name="B.A. Mohiuddin Bava"
)

# Constituency 3: Udupi
udupi = Constituency(
    name="Udupi", code="UDU001",
    district="Udupi",
    mla_name="Yashpal Suvarna"
)
```

**Result:**
- 3 separate MLAs
- 3 separate sets of wards, departments, users
- Complete data isolation
- Single shared infrastructure

---

## 📊 Data Isolation Example

### **Citizen A (Puttur)**
```python
user_a = User(
    phone="+919111111111",
    constituency_id=puttur.id
)

# This citizen can only:
# - See complaints in Puttur
# - Vote in Puttur polls
# - Contact Puttur MLA
# - Access Puttur ward info
```

### **Citizen B (Mangalore)**
```python
user_b = User(
    phone="+919222222222",
    constituency_id=mangalore_n.id
)

# This citizen can only:
# - See complaints in Mangalore North
# - Vote in Mangalore North polls
# - Contact Mangalore North MLA
# - Access Mangalore wards
```

### **Super Admin**
```python
admin = User(
    phone="+919000000000",
    role=UserRole.ADMIN,
    constituency_id=None  # Can access all
)

# Admin can:
# - View all constituencies
# - Compare performance across MLAs
# - Access system-wide analytics
# - Manage all users
```

---

## 🔍 Query Examples

### **Get Complaints for Specific Constituency**

```python
# Puttur MLA sees only Puttur complaints
puttur_complaints = db.query(Complaint)\
    .filter(Complaint.constituency_id == puttur.id)\
    .all()

# Mangalore MLA sees only Mangalore complaints
mangalore_complaints = db.query(Complaint)\
    .filter(Complaint.constituency_id == mangalore_n.id)\
    .all()
```

### **Cross-Constituency Comparison (Admin Only)**

```python
# Admin can compare all constituencies
from sqlalchemy import func

stats = db.query(
    Constituency.name,
    func.count(Complaint.id).label('total_complaints')
).join(
    Complaint, 
    Complaint.constituency_id == Constituency.id
).group_by(
    Constituency.id
).all()

# Result:
# [
#   ("Puttur", 150),
#   ("Mangalore North", 200),
#   ("Udupi", 120)
# ]
```

---

## 🛠️ API Endpoints for Multi-Tenant

### **Create New Constituency (Admin Only)**

```python
@router.post("/api/admin/constituencies")
async def create_constituency(
    constituency_data: ConstituencyCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    constituency = Constituency(**constituency_data.dict())
    db.add(constituency)
    db.commit()
    return constituency
```

### **List All Constituencies (Public)**

```python
@router.get("/api/constituencies")
async def list_constituencies(db: Session = Depends(get_db)):
    return db.query(Constituency)\
        .filter(Constituency.is_active == True)\
        .all()
```

### **Get Constituency Details**

```python
@router.get("/api/constituencies/{constituency_id}")
async def get_constituency(
    constituency_id: UUID,
    db: Session = Depends(get_db)
):
    constituency = db.query(Constituency)\
        .filter(Constituency.id == constituency_id)\
        .first()
    
    if not constituency:
        raise HTTPException(status_code=404)
    
    # Include statistics
    total_users = db.query(User)\
        .filter(User.constituency_id == constituency_id)\
        .count()
    
    total_complaints = db.query(Complaint)\
        .filter(Complaint.constituency_id == constituency_id)\
        .count()
    
    return {
        **constituency.__dict__,
        "statistics": {
            "total_users": total_users,
            "total_complaints": total_complaints
        }
    }
```

---

## 📈 Scaling Path

### **Phase 1: Single Constituency (Current)**
- Puttur only
- ~1,000 users
- Single MLA

### **Phase 2: Pilot Expansion (Month 3-6)**
- Add 2-3 more constituencies
- ~5,000 users total
- Test multi-tenant isolation

### **Phase 3: District-Wide (Month 6-12)**
- All constituencies in Dakshina Kannada
- ~8 constituencies
- ~20,000 users

### **Phase 4: State-Wide (Year 2)**
- All 224 Karnataka constituencies
- ~500,000 users
- Consider database sharding

---

## ✅ Checklist: Onboarding New Constituency

- [ ] Create `Constituency` record
- [ ] Add all wards with geographic boundaries
- [ ] Create department records (PWD, Water, Health, etc.)
- [ ] Create MLA user account
- [ ] Create department officer accounts
- [ ] Import existing citizen data (if any)
- [ ] Configure notification settings
- [ ] Train MLA office staff
- [ ] Launch mobile app for constituency
- [ ] Monitor for first week

---

## 🔐 Security Notes

1. **Data Isolation**: Enforced at database query level
2. **Access Control**: Role-based (CITIZEN, MLA, DEPARTMENT_OFFICER, ADMIN)
3. **Audit Logging**: All cross-constituency access logged
4. **API Security**: JWT tokens include constituency_id
5. **Testing**: Always test with multiple constituencies

---

## 💡 Quick Commands

### **Create First Constituency**
```bash
cd backend
python -c "
from app.models import Constituency
from app.core.database import SessionLocal

db = SessionLocal()
c = Constituency(
    name='Puttur', 
    code='PUT001',
    district='Dakshina Kannada',
    is_active=True
)
db.add(c)
db.commit()
print(f'Created: {c.id}')
"
```

### **List All Constituencies**
```bash
curl http://localhost:8000/api/constituencies
```

### **Get Constituency Stats**
```bash
curl http://localhost:8000/api/constituencies/{id}
```

---

## 🎓 Summary

**Multi-tenancy is achieved through:**

1. ✅ `Constituency` model as tenant entity
2. ✅ `constituency_id` foreign key in all tables
3. ✅ Query-level filtering by constituency
4. ✅ User-level constituency assignment
5. ✅ Role-based access control
6. ✅ Admin override for cross-constituency access

**Benefits:**

- 💰 Cost-effective (shared infrastructure)
- 🚀 Easy to scale (add new constituencies instantly)
- 🔒 Secure (complete data isolation)
- 📊 Flexible (constituency-level or state-level analytics)
- 🛠️ Maintainable (single codebase, single database)

---

**Ready to onboard your first 3 constituencies!** 🎉
