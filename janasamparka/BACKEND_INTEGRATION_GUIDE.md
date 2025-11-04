# 🔌 Backend Integration Guide

## API Endpoints Implementation Status

This document outlines which API endpoints need to be implemented or connected to the frontend.

---

## ✅ Already Working (Frontend Connected)

### **Authentication**
- ✅ `POST /auth/request-otp` - Request OTP
- ✅ `POST /auth/verify-otp` - Verify OTP and get JWT
- ✅ `GET /auth/me` - Get current user
- ✅ `POST /auth/refresh` - Refresh JWT token

### **Complaints (Read Operations)**
- ✅ `GET /complaints` - List complaints with filters
- ✅ `GET /complaints/{id}` - Get complaint details

### **Departments**
- ✅ `GET /departments` - List all departments
- ✅ `GET /departments/{id}` - Get department details

### **Wards**
- ✅ `GET /wards` - List all wards
- ✅ `GET /wards/{id}` - Get ward details

### **Users**
- ✅ `GET /users` - List all users
- ✅ `GET /users/{id}` - Get user details

### **Constituencies**
- ✅ `GET /constituencies` - List constituencies
- ✅ `GET /constituencies/{id}` - Get constituency details

### **Polls (Read Operations)**
- ✅ `GET /polls` - List all polls
- ✅ `GET /polls/{id}` - Get poll details

---

## 🔄 Needs Backend Implementation (UI Ready)

### **1. Complaint Status Update**
**Frontend:** ✅ StatusUpdateModal component ready  
**Backend:** ❌ Endpoint needs implementation

```python
# Endpoint to implement
@router.put("/complaints/{id}/status")
async def update_complaint_status(
    id: UUID,
    status_data: ComplaintStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update complaint status with notes
    
    Request Body:
    {
        "new_status": "in_progress",  # submitted, under_review, in_progress, resolved, rejected
        "note": "Started work on the issue"
    }
    
    Response:
    {
        "success": true,
        "complaint": {...}  # Updated complaint object
    }
    """
    pass
```

**Schema needed:**
```python
class ComplaintStatusUpdate(BaseModel):
    new_status: str  # Use enum
    note: Optional[str] = None
```

---

### **2. Department Assignment**
**Frontend:** ✅ DepartmentAssignModal component ready  
**Backend:** ❌ Endpoint needs implementation

```python
# Endpoint to implement
@router.post("/complaints/{id}/assign")
async def assign_complaint_to_department(
    id: UUID,
    assignment_data: ComplaintAssignment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign complaint to department
    
    Request Body:
    {
        "department_id": "dept-uuid",
        "officer_id": "officer-uuid",  # Optional
        "priority": "high",  # low, medium, high, urgent
        "note": "Assignment instructions"
    }
    
    Response:
    {
        "success": true,
        "complaint": {...}  # Updated complaint object
    }
    """
    pass
```

**Schema needed:**
```python
class ComplaintAssignment(BaseModel):
    department_id: UUID
    officer_id: Optional[UUID] = None
    priority: str  # Use enum
    note: Optional[str] = None
```

---

### **3. Photo Upload**
**Frontend:** ✅ PhotoUploadModal component ready  
**Backend:** ❌ Endpoint needs implementation

```python
# Endpoint to implement
@router.post("/media/upload")
async def upload_media(
    files: List[UploadFile] = File(...),
    complaint_id: UUID = Form(...),
    photo_type: str = Form(...),  # before, during, after
    caption: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload photos for complaint resolution
    
    Request: multipart/form-data
    - files: Multiple image files
    - complaint_id: UUID
    - photo_type: "before" | "during" | "after"
    - caption: Optional description
    
    Response:
    {
        "success": true,
        "media": [...]  # Array of uploaded media objects
    }
    """
    # Save files to storage (local/S3/etc)
    # Create media records in database
    # Link to complaint
    pass
```

**Schema needed:**
```python
class MediaResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    url: str
    media_type: str
    photo_type: str  # before, during, after
    caption: Optional[str]
    uploaded_at: datetime
```

---

### **4. Poll Creation**
**Frontend:** ✅ PollCreateModal component ready  
**Backend:** ❌ Endpoint needs implementation

```python
# Endpoint to implement
@router.post("/polls")
async def create_poll(
    poll_data: PollCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new poll
    
    Request Body:
    {
        "title": "Which road should be repaired first?",
        "description": "Help us prioritize...",
        "ward_id": "ward-uuid" | "all",
        "start_date": "2025-10-27T00:00:00",
        "end_date": "2025-11-03T23:59:59",
        "options": [
            {"option_text": "Main Road"},
            {"option_text": "Temple Street"},
            {"option_text": "Market Road"}
        ]
    }
    
    Response:
    {
        "success": true,
        "poll": {...}  # Created poll object with options
    }
    """
    pass
```

**Schemas needed:**
```python
class PollOptionCreate(BaseModel):
    option_text: str

class PollCreate(BaseModel):
    title: str
    description: str
    ward_id: Optional[str] = "all"
    start_date: datetime
    end_date: datetime
    options: List[PollOptionCreate]

class PollResponse(BaseModel):
    id: UUID
    title: str
    description: str
    ward_id: Optional[UUID]
    ward_name: str
    start_date: datetime
    end_date: datetime
    is_active: bool
    total_votes: int
    options: List[PollOptionResponse]
    created_at: datetime
```

---

### **5. Poll Voting (Mobile App)**
**Frontend:** ⏭️ Mobile app feature  
**Backend:** ❌ Endpoint needs implementation

```python
# Endpoint to implement
@router.post("/polls/{id}/vote")
async def vote_on_poll(
    id: UUID,
    vote_data: VoteSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit vote for a poll option
    
    Request Body:
    {
        "option_id": "option-uuid"
    }
    
    Response:
    {
        "success": true,
        "message": "Vote recorded",
        "poll": {...}  # Updated poll with new vote counts
    }
    
    Validation:
    - User can only vote once per poll
    - Poll must be active
    - Option must belong to the poll
    """
    pass
```

---

### **6. End Poll**
**Frontend:** ✅ Button exists in Polls page  
**Backend:** ❌ Endpoint needs implementation

```python
# Endpoint to implement
@router.post("/polls/{id}/end")
async def end_poll(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End an active poll
    
    Response:
    {
        "success": true,
        "poll": {...}  # Updated poll with is_active=false
    }
    
    Validation:
    - Only MLA/Admin can end polls
    - Poll must be active
    """
    pass
```

---

## 📊 Additional Recommended Endpoints

### **Dashboard Analytics**
```python
@router.get("/dashboard/analytics")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard analytics
    
    Response:
    {
        "complaints": {
            "total": 156,
            "by_status": {...},
            "by_category": {...},
            "trend": [...]
        },
        "departments": {
            "performance": [...],
            "leaderboard": [...]
        },
        "wards": {
            "top_performing": [...],
            "complaint_distribution": [...]
        }
    }
    """
    pass
```

### **Report Generation**
```python
@router.get("/reports/generate")
async def generate_report(
    report_type: str,  # weekly, monthly, custom
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate PDF/Excel report
    
    Returns: File download
    """
    pass
```

---

## 🔐 Authentication & Authorization

### **Required Permissions:**

| Endpoint | Citizen | Moderator | Dept Officer | MLA | Admin |
|----------|---------|-----------|--------------|-----|-------|
| View Complaints | ✅ Own | ✅ All | ✅ Assigned | ✅ All | ✅ All |
| Update Status | ❌ | ✅ | ✅ | ✅ | ✅ |
| Assign Department | ❌ | ✅ | ❌ | ✅ | ✅ |
| Upload Photos | ❌ | ✅ | ✅ | ✅ | ✅ |
| Create Polls | ❌ | ❌ | ❌ | ✅ | ✅ |
| Vote on Polls | ✅ | ✅ | ✅ | ✅ | ✅ |
| View Analytics | ❌ | ✅ | ✅ | ✅ | ✅ |

---

## 🛠️ Implementation Checklist

### **High Priority (Core Workflow)**
- [ ] `PUT /complaints/{id}/status` - Status update
- [ ] `POST /complaints/{id}/assign` - Department assignment
- [ ] `POST /media/upload` - Photo upload
- [ ] Status history logging (automatic)
- [ ] Notification system (push/SMS)

### **Medium Priority (Engagement)**
- [ ] `POST /polls` - Poll creation
- [ ] `POST /polls/{id}/vote` - Voting
- [ ] `POST /polls/{id}/end` - End poll
- [ ] Poll analytics

### **Low Priority (Analytics)**
- [ ] `GET /dashboard/analytics` - Dashboard data
- [ ] `GET /reports/generate` - PDF reports
- [ ] Performance metrics APIs

---

## 📝 Database Migrations Needed

### **1. Add photo_type to media table**
```sql
ALTER TABLE media ADD COLUMN photo_type VARCHAR(20);
-- Values: 'before', 'during', 'after', 'evidence'
```

### **2. Add status_logs table**
```sql
CREATE TABLE status_logs (
    id UUID PRIMARY KEY,
    complaint_id UUID REFERENCES complaints(id),
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_by UUID REFERENCES users(id),
    note TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### **3. Add assignment fields to complaints**
```sql
ALTER TABLE complaints ADD COLUMN assigned_officer_id UUID REFERENCES users(id);
ALTER TABLE complaints ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';
ALTER TABLE complaints ADD COLUMN assigned_at TIMESTAMP;
```

---

## 🧪 Testing Endpoints

### **Using Postman/Thunder Client:**

1. **Get JWT Token:**
```bash
POST http://localhost:8000/auth/verify-otp
{
  "phone": "+918242226666",
  "otp": "123456"
}
```

2. **Test Status Update:**
```bash
PUT http://localhost:8000/complaints/{id}/status
Headers: Authorization: Bearer {token}
{
  "new_status": "in_progress",
  "note": "Started working on this issue"
}
```

3. **Test Department Assignment:**
```bash
POST http://localhost:8000/complaints/{id}/assign
Headers: Authorization: Bearer {token}
{
  "department_id": "{dept-id}",
  "priority": "high",
  "note": "Urgent issue"
}
```

4. **Test Photo Upload:**
```bash
POST http://localhost:8000/media/upload
Headers: Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- files: [image1.jpg, image2.jpg]
- complaint_id: {complaint-id}
- photo_type: "after"
- caption: "Work completed"
```

---

## 🔗 Frontend Integration Points

### **API Client (src/services/api.js)**

Add these methods:

```javascript
// Complaints API
export const complaintsAPI = {
  // ... existing methods
  
  updateStatus: (id, data) => 
    api.put(`/complaints/${id}/status`, data),
    
  assignDepartment: (id, data) => 
    api.post(`/complaints/${id}/assign`, data),
};

// Media API
export const mediaAPI = {
  upload: (formData) => 
    api.post('/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
};

// Polls API
export const pollsAPI = {
  // ... existing methods
  
  create: (data) => 
    api.post('/polls', data),
    
  vote: (id, optionId) => 
    api.post(`/polls/${id}/vote`, { option_id: optionId }),
    
  end: (id) => 
    api.post(`/polls/${id}/end`),
};
```

---

## ✅ Integration Steps

### **Step 1: Implement Backend Endpoints**
1. Add schemas to `app/schemas/`
2. Implement routes in `app/routers/`
3. Add business logic
4. Test with Postman

### **Step 2: Update Frontend API Client**
1. Add methods to `src/services/api.js`
2. Update modal handlers in components
3. Test integration

### **Step 3: Testing**
1. Test each endpoint individually
2. Test complete workflows
3. Test error handling
4. Test with different user roles

### **Step 4: Deploy**
1. Run database migrations
2. Deploy backend
3. Deploy frontend
4. Verify production

---

## 🚨 Important Notes

1. **File Upload:** Configure max file size (10MB recommended)
2. **Storage:** Decide on storage solution (local/S3/CloudFlare R2)
3. **Notifications:** Set up FCM/SMS gateway for notifications
4. **Rate Limiting:** Implement rate limiting on voting endpoints
5. **Validation:** Add proper input validation on all endpoints
6. **Logging:** Log all status changes and assignments for audit trail

---

## 📞 Support

For backend implementation questions:
- Review FastAPI documentation: https://fastapi.tiangolo.com/
- Check Pydantic schemas: https://pydantic-docs.helpmanual.io/
- PostgreSQL + SQLAlchemy: https://docs.sqlalchemy.org/

---

**Document Version:** 1.0  
**Last Updated:** October 27, 2025  
**Status:** Ready for Backend Implementation
