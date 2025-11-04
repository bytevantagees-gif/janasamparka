# Department Workflow & Escalation Implementation

## Overview
This document describes the comprehensive department workflow improvements implemented for the Janasamparka platform, including smart department suggestions, routing capabilities, case notes, and citizen escalation features.

## Date: October 30, 2025

---

## Features Implemented

### 1. **Department-Specific Map Filtering** ✅
**Location:** `admin-dashboard/src/pages/Map.jsx`

- Department officers now see only complaints relevant to their department on the map view
- Filtering based on:
  - Complaints assigned to the officer
  - Unassigned complaints in their constituency matching their department's categories
  - Category-based filtering using predefined department mappings
- Added "(department view)" indicator in map header for officers

### 2. **Smart Department Suggestions** ✅
**Locations:**
- Backend Service: `backend/app/services/department_suggestion.py`
- API Endpoint: `backend/app/routers/case_management.py`
- Schemas: `backend/app/schemas/case_management.py`

**Features:**
- AI-powered keyword matching algorithm
- Analyzes complaint title, description, category, and location
- Returns top 3 department suggestions with confidence scores
- Department keyword categories include:
  - Roads (PWD, BBMP_ROADS, NHAI)
  - Water Supply (BWSSB)
  - Electricity (BESCOM)
  - Health (BBMP_HEALTH)
  - Education
  - Sanitation
  - Police/Law & Order
  - Environment/Parks

**API Endpoint:**
```
POST /api/v1/case-management/suggest-department
Body: {
  "title": "Pothole on Main Street",
  "description": "Large pothole causing accidents",
  "category": "roads",
  "location_description": "Near City Hall"
}
Query: constituency_id=<uuid>
```

**Response:**
```json
{
  "suggestions": [
    {
      "dept_id": "uuid",
      "dept_name": "Public Works Department",
      "dept_code": "PWD",
      "confidence": 0.75,
      "reason": "Matched keywords related to: roads"
    }
  ],
  "constituency_id": "uuid"
}
```

### 3. **Case Notes System** ✅
**Locations:**
- Model: `backend/app/models/case_note.py`
- API Endpoints: `backend/app/routers/case_management.py`

**Features:**
- Create internal or public notes on complaints
- Note types: general, status_update, department_routing, escalation, resolution, work_update
- Visibility control (public for citizens, internal for staff)
- **Automatic idle timer reset** - notes with `resets_idle_timer=true` update the complaint's `last_activity_at` timestamp
- Prevents premature case aging when officers add updates

**API Endpoints:**
```
POST /api/v1/case-management/complaints/{complaint_id}/notes
GET /api/v1/case-management/complaints/{complaint_id}/notes?include_internal=true
```

**Database Schema:**
- `id` (UUID)
- `complaint_id` (UUID, FK to complaints)
- `note` (Text)
- `note_type` (Enum: general, status_update, department_routing, escalation, resolution, work_update)
- `created_by` (UUID, FK to users)
- `is_public` (Boolean - visible to citizen)
- `resets_idle_timer` (Boolean - resets idle timer)
- `created_at` (DateTime)

### 4. **Department Routing System** ✅
**Locations:**
- Model: `backend/app/models/case_note.py` (DepartmentRouting)
- API Endpoints: `backend/app/routers/case_management.py`

**Features:**
- Department officers and moderators can route complaints to the correct department
- Requires reason selection and optional comments
- Automatically creates a public case note when routing occurs
- Tracks routing history with acceptance status
- Clears assignment when routing to ensure proper reassignment

**Routing Reasons:**
- Incorrect Department
- Better Suited
- Specialized Team Required
- Jurisdiction Issue
- Other

**API Endpoints:**
```
POST /api/v1/case-management/complaints/{complaint_id}/route
GET /api/v1/case-management/complaints/{complaint_id}/routing-history
```

**Database Schema:**
- `id` (UUID)
- `complaint_id` (UUID, FK to complaints)
- `from_dept_id` (UUID, FK to departments, nullable)
- `to_dept_id` (UUID, FK to departments)
- `reason` (Enum)
- `comments` (Text, optional)
- `routed_by` (UUID, FK to users)
- `routed_at` (DateTime)
- `accepted` (Boolean, nullable)
- `accepted_by` (UUID, FK to users, nullable)
- `accepted_at` (DateTime, nullable)

### 5. **Citizen Escalation to MLA** ✅
**Locations:**
- Model: `backend/app/models/case_note.py` (ComplaintEscalation)
- API Endpoints: `backend/app/routers/case_management.py`

**Features:**
- Citizens can escalate complaints to MLA when:
  - Complaint incorrectly closed
  - Wrongly routed to wrong department
  - No progress updates for extended period
  - Delayed resolution
  - Poor quality work
  - Department unresponsive
- Only complaint creator can escalate
- Prevents duplicate escalations (must resolve existing first)
- MLA/Admin can resolve escalations with notes
- Creates public case notes for transparency

**Escalation Reasons:**
- Incorrectly Closed
- Wrongly Routed
- No Progress Update
- Delayed Resolution
- Poor Quality Work
- Unresponsive
- Other

**API Endpoints:**
```
POST /api/v1/case-management/complaints/{complaint_id}/escalate
POST /api/v1/case-management/escalations/{escalation_id}/resolve
GET /api/v1/case-management/complaints/{complaint_id}/escalations
```

**Database Schema:**
- `id` (UUID)
- `complaint_id` (UUID, FK to complaints)
- `reason` (Enum)
- `description` (Text)
- `escalated_by` (UUID, FK to users)
- `resolved` (Boolean, default false)
- `resolution_notes` (Text, nullable)
- `resolved_by` (UUID, FK to users, nullable)
- `resolved_at` (DateTime, nullable)
- `created_at` (DateTime)

### 6. **Enhanced Complaint Model** ✅
**Location:** `backend/app/models/complaint.py`

**New Fields:**
- `suggested_dept_id` - AI-suggested department
- `citizen_selected_dept` - Boolean flag if citizen manually selected department
- `last_activity_at` - Timestamp updated by case notes to prevent idle aging

---

## Database Migration

**File:** `backend/alembic/versions/add_case_notes_routing_escalations.py`

Creates:
- `case_notes` table with indexes on `complaint_id` and `created_at`
- `department_routing` table with indexes on `complaint_id` and `routed_at`
- `complaint_escalations` table with indexes on `complaint_id` and `created_at`
- New columns in `complaints` table: `suggested_dept_id`, `citizen_selected_dept`, `last_activity_at`

**To apply migration:**
```bash
cd backend
alembic upgrade head
```

---

## API Router Registration

Add to `backend/app/main.py`:

```python
from app.routers import case_management

app.include_router(case_management.router)
```

---

## Frontend Integration Points

### Mobile App (React Native)
1. **Complaint Submission:**
   - Add department selection dropdown
   - Call `/suggest-department` endpoint after user enters title/description
   - Show suggested departments with confidence scores
   - Allow citizen to select from suggestions or choose manually

2. **Complaint Detail:**
   - Display case notes (public only for citizens)
   - Show routing history
   - Add "Escalate to MLA" button with reason selection
   - Display escalation status and resolution

3. **Department Officer View:**
   - Show assigned complaints
   - Add "Route to Department" button
   - Case notes interface (can create internal/public notes)

### Admin Dashboard (React)
1. **Complaint Detail Page:**
   - Case notes section (all notes for staff)
   - Routing controls for moderators/officers
   - Escalation management for MLA/admin
   - Department suggestion display

2. **Map View:**
   - Already implemented department filtering for officers
   - Shows only relevant complaints based on officer's department

3. **Department Management:**
   - View routing statistics
   - Accept/reject routed complaints
   - Bulk routing capabilities

---

## Workflow Examples

### Citizen Files Complaint
1. Citizen enters title: "Water leaking from pipe"
2. System suggests: BWSSB (confidence: 0.85)
3. Citizen confirms or selects different department
4. Complaint created with `dept_id` and `suggested_dept_id`

### Department Moderator Routes Complaint
1. Moderator reviews complaint assigned to wrong department
2. Clicks "Route to Department"
3. Selects target department and reason
4. System:
   - Creates routing record
   - Updates complaint `dept_id`
   - Clears `assigned_to`
   - Creates public case note
   - Resets `last_activity_at`

### Officer Adds Progress Note
1. Officer working on complaint adds note: "Work started, materials ordered"
2. Sets `resets_idle_timer=true`
3. System updates `last_activity_at`
4. Prevents complaint from appearing in "idle" reports

### Citizen Escalates to MLA
1. Complaint closed but citizen disagrees
2. Citizen clicks "Escalate to MLA"
3. Selects reason: "Incorrectly Closed"
4. Provides description
5. System:
   - Creates escalation record
   - Creates public case note
   - Notifies MLA
   - Resets `last_activity_at`

### MLA Resolves Escalation
1. MLA reviews escalation
2. Investigates complaint
3. Provides resolution notes
4. Marks escalation as resolved
5. System creates public case note with resolution

---

## Testing Checklist

### Backend Testing
- [ ] Create case notes (public and internal)
- [ ] Retrieve case notes with visibility filtering
- [ ] Route complaint between departments
- [ ] View routing history
- [ ] Create escalation as citizen
- [ ] Prevent duplicate escalations
- [ ] Resolve escalation as MLA/admin
- [ ] Test department suggestions with various keywords
- [ ] Verify idle timer reset on case note creation
- [ ] Test permissions (citizen, officer, moderator, admin, MLA)

### Frontend Testing
- [ ] Department selection during complaint submission
- [ ] Display suggested departments
- [ ] Show case notes on complaint detail
- [ ] Test escalation flow from citizen app
- [ ] Department routing from officer/moderator view
- [ ] Map filtering for department officers
- [ ] Escalation management for MLA/admin

---

## Performance Considerations

1. **Index Strategy:**
   - Indexed `complaint_id` on case_notes, department_routing, escalations
   - Indexed timestamps for chronological queries
   - Consider composite indexes for frequent query patterns

2. **Query Optimization:**
   - Department suggestions use in-memory keyword matching (fast)
   - Batch fetch user/department names to avoid N+1 queries
   - Use eager loading for related entities

3. **Caching Opportunities:**
   - Department keyword mappings (static data)
   - Department list per constituency
   - User permissions/roles

---

## Security Considerations

1. **Authorization:**
   - Only complaint creator can escalate
   - Only officers/moderators can route
   - Only MLA/admin can resolve escalations
   - Case note visibility based on role

2. **Data Validation:**
   - Validate department exists before routing
   - Validate complaint exists before operations
   - Prevent duplicate escalations
   - Sanitize note content

3. **Audit Trail:**
   - All routing actions logged with timestamps
   - Escalations tracked with full history
   - Case notes provide complete timeline

---

## Future Enhancements

1. **ML-based Department Suggestions:**
   - Train model on historical routing data
   - Improve confidence scores
   - Learn from corrections

2. **Auto-routing:**
   - Automatically route based on high-confidence suggestions
   - Require manual approval for low-confidence cases

3. **SLA Tracking:**
   - Define department-specific SLAs
   - Alert when approaching deadlines
   - Use `last_activity_at` for accurate aging

4. **Bulk Operations:**
   - Bulk routing for moderators
   - Bulk case note creation
   - Mass escalation resolution

5. **Analytics:**
   - Routing accuracy metrics
   - Escalation trends
   - Department performance
   - Idle time distribution

---

## Configuration

### Environment Variables
No new environment variables required. Uses existing database connection.

### Department Setup
Ensure departments are properly configured with:
- Correct department codes (matching keyword mappings)
- Constituency associations
- Contact information

---

## Support & Maintenance

### Monitoring
- Track escalation rates by department
- Monitor routing frequency
- Analyze case note patterns
- Review department suggestion accuracy

### Common Issues
1. **No department suggestions:**
   - Check if departments exist in constituency
   - Verify department codes match keyword mappings
   - Review complaint text for keywords

2. **Cannot escalate:**
   - Verify user is complaint creator
   - Check for existing unresolved escalation
   - Ensure complaint exists

3. **Routing fails:**
   - Verify target department exists
   - Check user permissions
   - Confirm department is in same constituency

---

## Conclusion

This implementation provides a complete department workflow system with:
- ✅ Smart department suggestions for citizens
- ✅ Flexible routing with full audit trail
- ✅ Comprehensive case notes system
- ✅ Citizen escalation to MLA
- ✅ Idle timer management
- ✅ Role-based access control
- ✅ Full transparency through public notes

All backend features are complete and ready for frontend integration. The system is designed to be extensible and can accommodate future ML-based improvements.
