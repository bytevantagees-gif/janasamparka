# 🏛️ Multi-Tenant Architecture Guide

## Overview

Janasamparka uses a **shared database, multi-tenant architecture** where multiple constituencies (tenants) share the same database infrastructure while maintaining complete data isolation.

---

## 🎯 Architecture Strategy

### **Single Database with Tenant Isolation**

```
┌────────────────────────────────────────────────────────┐
│                    Shared Database                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Constituency │  │ Constituency │  │ Constituency │ │
│  │   Puttur     │  │   Mangalore  │  │   Udupi      │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤ │
│  │ Users        │  │ Users        │  │ Users        │ │
│  │ Complaints   │  │ Complaints   │  │ Complaints   │ │
│  │ Wards        │  │ Wards        │  │ Wards        │ │
│  │ Departments  │  │ Departments  │  │ Departments  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema Changes

### **New Table: Constituencies**

```sql
constituencies
├── id (UUID, PK)
├── name (VARCHAR) - "Puttur", "Mangalore", etc.
├── code (VARCHAR) - "PUT001", "MNG001", etc.
├── district (VARCHAR)
├── state (VARCHAR)
├── mla_name (VARCHAR)
├── mla_party (VARCHAR)
├── mla_contact_phone (VARCHAR)
├── mla_contact_email (VARCHAR)
├── total_population (INTEGER)
├── total_wards (INTEGER)
├── assembly_number (INTEGER)
├── is_active (BOOLEAN)
├── subscription_tier (VARCHAR) - basic/premium/enterprise
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### **Updated Tables with constituency_id**

All major tables now include `constituency_id` foreign key:

**users**
```sql
ALTER TABLE users 
ADD COLUMN constituency_id UUID REFERENCES constituencies(id);
```

**wards**
```sql
ALTER TABLE wards 
ADD COLUMN constituency_id UUID NOT NULL REFERENCES constituencies(id);
-- REMOVED: constituency VARCHAR (replaced with FK)
```

**departments**
```sql
ALTER TABLE departments 
ADD COLUMN constituency_id UUID NOT NULL REFERENCES constituencies(id);
-- CHANGED: code is no longer UNIQUE (same dept can exist per constituency)
```

**complaints**
```sql
ALTER TABLE complaints 
ADD COLUMN constituency_id UUID NOT NULL REFERENCES constituencies(id);
CREATE INDEX idx_complaints_constituency ON complaints(constituency_id);
```

**polls**
```sql
ALTER TABLE polls 
ADD COLUMN constituency_id UUID NOT NULL REFERENCES constituencies(id);
CREATE INDEX idx_polls_constituency ON polls(constituency_id);
```

---

## 🔒 Data Isolation Strategy

### **1. Query-Level Filtering**

Every query automatically filters by `constituency_id`:

```python
# Bad - No tenant filtering
complaints = db.query(Complaint).all()

# Good - Filtered by constituency
complaints = db.query(Complaint)\
    .filter(Complaint.constituency_id == current_constituency_id)\
    .all()
```

### **2. Middleware-Based Tenant Context**

```python
# Automatically set constituency_id from authenticated user
@router.get("/complaints/")
async def list_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get user's constituency
    constituency_id = current_user.constituency_id
    
    # Filter by constituency
    complaints = db.query(Complaint)\
        .filter(Complaint.constituency_id == constituency_id)\
        .all()
    
    return complaints
```

### **3. Row-Level Security (PostgreSQL RLS - Optional)**

For additional security, enable PostgreSQL Row-Level Security:

```sql
ALTER TABLE complaints ENABLE ROW LEVEL SECURITY;

CREATE POLICY constituency_isolation ON complaints
    USING (constituency_id = current_setting('app.current_constituency_id')::UUID);
```

---

## 👥 User Access Patterns

### **1. Citizen Users**
- Belong to ONE constituency
- Can only see/create data in their constituency
- `user.constituency_id` is set during registration

### **2. Department Officers**
- Belong to ONE constituency
- Can only see complaints assigned to their department in their constituency

### **3. MLA Users**
- Primary constituency set in `user.constituency_id`
- Can access their own constituency data
- Special role: `UserRole.MLA`

### **4. Super Admin Users**
- Can access ALL constituencies
- `user.constituency_id` can be NULL
- Role: `UserRole.ADMIN`
- Queries can optionally filter by constituency or view all

---

## 🔧 Implementation Examples

### **1. Creating a New Constituency**

```python
# Create Puttur Constituency
puttur = Constituency(
    name="Puttur",
    code="PUT001",
    district="Dakshina Kannada",
    state="Karnataka",
    mla_name="Ashok Kumar Rai",
    mla_party="Congress",
    mla_contact_phone="+919876543210",
    assembly_number=172,
    total_wards=35,
    is_active=True,
    subscription_tier="premium"
)
db.add(puttur)
db.commit()
```

### **2. Creating Ward for Constituency**

```python
# Create ward in Puttur
ward = Ward(
    name="Ward 1 - Market Area",
    ward_number=1,
    taluk="Puttur",
    constituency_id=puttur.id,  # Link to constituency
    population=5000
)
db.add(ward)
db.commit()
```

### **3. User Registration with Constituency**

```python
# Citizen registers in Puttur
user = User(
    name="Rajesh Kumar",
    phone="+919876543210",
    role=UserRole.CITIZEN,
    constituency_id=puttur.id  # Assigned to Puttur
)
db.add(user)
db.commit()
```

### **4. Creating Complaint (Auto-filtered)**

```python
# Complaint automatically gets constituency from user
complaint = Complaint(
    title="Pothole on Main Road",
    description="...",
    user_id=user.id,
    constituency_id=user.constituency_id,  # Inherit from user
    lat=12.9141,
    lng=75.2479
)
db.add(complaint)
db.commit()
```

---

## 🌐 API Changes

### **Updated Authentication Flow**

```python
@router.post("/verify-otp")
async def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    # ... verify OTP ...
    
    # Check if user exists
    user = db.query(User).filter(User.phone == phone).first()
    
    if not user:
        # New user - need to assign constituency
        # Option 1: Based on phone number area code
        # Option 2: User selects during registration
        # Option 3: GPS-based ward detection
        
        # For now, use a default (or require during registration)
        default_constituency = db.query(Constituency)\
            .filter(Constituency.code == "PUT001")\
            .first()
        
        user = User(
            name=f"User {phone[-4:]}",
            phone=phone,
            role=UserRole.CITIZEN,
            constituency_id=default_constituency.id if default_constituency else None
        )
        db.add(user)
        db.commit()
    
    # Generate tokens with constituency info
    access_token = create_access_token(data={
        "sub": str(user.id),
        "role": user.role,
        "constituency_id": str(user.constituency_id) if user.constituency_id else None
    })
    
    return TokenResponse(access_token=access_token, ...)
```

### **Filtered Endpoints**

```python
@router.get("/complaints/")
async def list_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    
    # Filter by constituency
    if current_user.role != UserRole.ADMIN:
        # Regular users see only their constituency
        query = query.filter(Complaint.constituency_id == current_user.constituency_id)
    else:
        # Admin can optionally filter or see all
        # Could add ?constituency_id= query param
        pass
    
    return query.all()
```

---

## 📈 Scaling Scenarios

### **Scenario 1: Single Constituency (MVP)**
```python
# Only Puttur constituency exists
constituencies = 1
users = ~1000
complaints_per_month = ~500
```

### **Scenario 2: Multiple Constituencies (Growth)**
```python
# 5 constituencies in Karnataka
constituencies = 5
users = ~5000
complaints_per_month = ~2500
```

### **Scenario 3: State-Wide Deployment**
```python
# All 224 constituencies in Karnataka
constituencies = 224
users = ~250,000
complaints_per_month = ~50,000

# Database considerations:
# - Table partitioning by constituency_id
# - Read replicas for each region
# - Caching layer (Redis)
```

### **Scenario 4: National Scale**
```python
# Multiple states
constituencies = 4000+
users = ~5,000,000
complaints_per_month = ~1,000,000

# Architecture changes needed:
# - Separate database per state (sharding)
# - Distributed caching
# - Message queue for async processing
# - CDN for static assets
```

---

## 🔐 Security Considerations

### **1. Tenant Isolation Enforcement**

```python
# Middleware to enforce tenant isolation
class TenantIsolationMiddleware:
    async def __call__(self, request: Request, call_next):
        # Extract user from token
        user = get_user_from_token(request)
        
        # Set tenant context
        request.state.constituency_id = user.constituency_id
        
        response = await call_next(request)
        return response
```

### **2. Prevent Cross-Tenant Data Access**

```python
# Validate constituency_id in all queries
def validate_constituency_access(
    resource_constituency_id: UUID,
    user: User
):
    if user.role == UserRole.ADMIN:
        return True  # Admin can access all
    
    if resource_constituency_id != user.constituency_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Resource belongs to different constituency"
        )
    return True
```

### **3. Audit Logging**

```python
# Log all cross-constituency access
@router.get("/complaints/{complaint_id}")
async def get_complaint(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    # Check constituency access
    if complaint.constituency_id != current_user.constituency_id:
        if current_user.role == UserRole.ADMIN:
            # Log admin access to different constituency
            AuditLog.create(
                user_id=current_user.id,
                action="cross_constituency_access",
                resource_type="complaint",
                resource_id=complaint_id,
                from_constituency=current_user.constituency_id,
                to_constituency=complaint.constituency_id
            )
        else:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return complaint
```

---

## 🛠️ Migration Strategy

### **Step 1: Create Constituencies Table**

```bash
cd backend
alembic revision --autogenerate -m "Add constituencies table and multi-tenant support"
alembic upgrade head
```

### **Step 2: Seed Initial Constituency**

```python
# Create seed data for Puttur
from app.models import Constituency
from app.core.database import SessionLocal

db = SessionLocal()

puttur = Constituency(
    name="Puttur",
    code="PUT001",
    district="Dakshina Kannada",
    state="Karnataka",
    mla_name="Ashok Kumar Rai",
    mla_party="Congress",
    assembly_number=172,
    is_active=True
)
db.add(puttur)
db.commit()
```

### **Step 3: Migrate Existing Data**

```python
# Update existing records with constituency_id
puttur_id = db.query(Constituency).filter(Constituency.code == "PUT001").first().id

# Update wards
db.query(Ward).update({Ward.constituency_id: puttur_id})

# Update departments
db.query(Department).update({Department.constituency_id: puttur_id})

# Update complaints
db.query(Complaint).update({Complaint.constituency_id: puttur_id})

db.commit()
```

---

## 📊 Analytics & Reporting

### **Constituency-Level Dashboard**

```python
@router.get("/analytics/constituency/{constituency_id}")
async def get_constituency_analytics(
    constituency_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate access
    validate_constituency_access(constituency_id, current_user)
    
    # Get constituency
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    
    # Get statistics
    total_complaints = db.query(Complaint)\
        .filter(Complaint.constituency_id == constituency_id)\
        .count()
    
    resolved = db.query(Complaint)\
        .filter(
            Complaint.constituency_id == constituency_id,
            Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
        )\
        .count()
    
    return {
        "constituency": constituency,
        "total_complaints": total_complaints,
        "resolved_complaints": resolved,
        "resolution_rate": (resolved / total_complaints * 100) if total_complaints > 0 else 0
    }
```

### **Cross-Constituency Comparison (Admin Only)**

```python
@router.get("/analytics/cross-constituency")
async def cross_constituency_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only admins can access
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all constituencies with stats
    constituencies = db.query(Constituency).filter(Constituency.is_active == True).all()
    
    results = []
    for constituency in constituencies:
        total = db.query(Complaint)\
            .filter(Complaint.constituency_id == constituency.id)\
            .count()
        
        resolved = db.query(Complaint)\
            .filter(
                Complaint.constituency_id == constituency.id,
                Complaint.status == ComplaintStatus.RESOLVED
            )\
            .count()
        
        results.append({
            "constituency": constituency.name,
            "total_complaints": total,
            "resolved": resolved,
            "resolution_rate": (resolved / total * 100) if total > 0 else 0
        })
    
    return sorted(results, key=lambda x: x["resolution_rate"], reverse=True)
```

---

## ✅ Best Practices

### **1. Always Filter by Constituency**
```python
# ✅ Good
complaints = db.query(Complaint)\
    .filter(Complaint.constituency_id == constituency_id)\
    .all()

# ❌ Bad - Missing constituency filter
complaints = db.query(Complaint).all()
```

### **2. Validate Constituency Access**
```python
# ✅ Good
if complaint.constituency_id != user.constituency_id and user.role != UserRole.ADMIN:
    raise HTTPException(status_code=403)

# ❌ Bad - No validation
return complaint
```

### **3. Include Constituency in API Responses**
```python
# ✅ Good - Include for transparency
{
    "complaint_id": "...",
    "constituency": {
        "id": "...",
        "name": "Puttur",
        "code": "PUT001"
    }
}
```

### **4. Use Database Indexes**
```python
# All constituency_id foreign keys should be indexed
CREATE INDEX idx_complaints_constituency ON complaints(constituency_id);
CREATE INDEX idx_wards_constituency ON wards(constituency_id);
```

---

## 🎯 Summary

✅ **Data Isolation**: Every entity linked to constituency  
✅ **Scalability**: Single database supports 100+ constituencies  
✅ **Security**: Query-level and row-level isolation  
✅ **Flexibility**: Admin users can access multiple constituencies  
✅ **Analytics**: Both per-constituency and cross-constituency reporting  
✅ **Future-proof**: Easy to shard/separate if needed  

---

## 📞 Next Steps

1. Run database migration: `alembic upgrade head`
2. Create initial constituencies
3. Update API endpoints with tenant filtering
4. Add constituency selection during user registration
5. Test multi-tenant isolation
6. Deploy and onboard first 3 constituencies

---

**Version:** 1.0  
**Last Updated:** October 2025
