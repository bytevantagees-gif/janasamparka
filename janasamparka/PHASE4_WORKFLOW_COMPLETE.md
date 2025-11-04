# Phase 4: Workflow & Notifications - Complete! 🎉

**Completion Date**: October 28, 2025  
**Status**: ✅ Core Workflow System Implemented

---

## Overview

Phase 4 implements a comprehensive complaint workflow management system with state transitions, role-based permissions, work approval process, and notification infrastructure.

---

## ✅ What Was Implemented

### 1. Workflow State Machine

**File**: `/backend/app/core/workflow.py`

**Features**:
- **Status Transition Rules**: Defines valid state transitions
- **Role-Based Permissions**: Controls who can make which transitions
- **Auto-Assignment Logic**: Suggests departments based on category
- **Workflow Validation**: Prevents invalid transitions
- **Terminal State Detection**: Identifies end states (closed, rejected)

**Status Transitions**:
```
submitted → assigned | rejected
assigned → in_progress | rejected
in_progress → resolved | assigned | rejected
resolved → closed | in_progress
closed → (terminal)
rejected → (terminal)
```

**Permission Matrix**:
| Transition | Allowed Roles |
|------------|---------------|
| submitted → assigned | Admin, MLA, Moderator |
| assigned → in_progress | Admin, Dept Officer, Moderator |
| in_progress → resolved | Admin, Dept Officer |
| resolved → closed | Admin, MLA, Moderator |
| resolved → in_progress | Admin, MLA, Moderator |

### 2. Enhanced Complaint Status Updates

**Endpoint**: `PATCH /api/complaints/{id}/status`

**Features**:
- ✅ Requires authentication
- ✅ Validates workflow transitions
- ✅ Checks role permissions
- ✅ Enforces constituency access control
- ✅ Auto-updates timestamps (resolved_at, closed_at)
- ✅ Creates status log with user tracking
- ✅ Returns meaningful error messages

**Example**:
```bash
curl -X PATCH http://localhost:8000/api/complaints/{id}/status \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "note": "Work started on this complaint"
  }'
```

### 3. Work Approval System

**Approve Endpoint**: `POST /api/complaints/{id}/approve`

**Features**:
- ✅ Requires MLA, Moderator, or Admin role
- ✅ Only works on "resolved" complaints
- ✅ Checks constituency access
- ✅ Transitions to "closed" status
- ✅ Records approval comments
- ✅ Tracks approver and timestamp
- ✅ Creates audit log

**Reject Endpoint**: `POST /api/complaints/{id}/reject`

**Features**:
- ✅ Requires MLA, Moderator, or Admin role
- ✅ Only works on "resolved" complaints
- ✅ Reverts to "in_progress" status
- ✅ Requires rejection reason
- ✅ Clears resolved timestamp
- ✅ Notifies department officer (TODO)

### 4. Workflow Status Endpoint

**Endpoint**: `GET /api/complaints/{id}/workflow`

**Returns**:
- Current complaint status
- Allowed transitions (based on user role)
- Whether approval is required
- Whether complaint can be reopened
- Whether status is terminal

**Response Example**:
```json
{
  "current_status": "in_progress",
  "allowed_transitions": ["resolved", "assigned"],
  "requires_approval": false,
  "can_reopen": false,
  "is_terminal": false
}
```

### 5. Notification System

**File**: `/backend/app/core/notifications.py`

**Services**:
- `NotificationService` - Base service for email/SMS
- `ComplaintNotifications` - Complaint-specific templates

**Notification Types**:
1. **Complaint Created** - Confirmation to citizen
2. **Complaint Assigned** - Alert to department officer
3. **Status Changed** - Update to citizen
4. **Work Approved** - Success message to citizen
5. **Work Rejected** - Rework request to officer
6. **Escalation** - Urgent alert to supervisor

**Channels**:
- ✅ Email (template ready, SMTP TODO)
- ✅ SMS (template ready, Twilio/SNS TODO)
- 🔄 In-app notifications (database model ready)

**HTML Email Templates**:
- Professional design with branding
- Responsive layout
- Clear call-to-action
- Complaint details formatted

---

## Workflow Examples

### Example 1: Happy Path (Complaint Resolution)

```
1. Citizen submits complaint
   Status: submitted
   ↓
2. MLA assigns to Road Department
   Status: submitted → assigned
   Notification: Department Officer receives SMS
   ↓
3. Officer starts work
   Status: assigned → in_progress
   Notification: Citizen receives update
   ↓
4. Officer completes work and uploads photos
   Status: in_progress → resolved
   Notification: MLA receives notification for approval
   ↓
5. MLA reviews photos and approves
   Status: resolved → closed
   Notification: Citizen receives success message
   
✅ Complaint CLOSED
```

### Example 2: Work Rejection & Rework

```
1. Officer marks work as resolved
   Status: in_progress → resolved
   ↓
2. MLA reviews and finds work incomplete
   Action: Reject with reason
   Status: resolved → in_progress
   Notification: Officer receives rework request
   ↓
3. Officer redoes work
   Status: in_progress → resolved
   ↓
4. MLA approves
   Status: resolved → closed
   
✅ Complaint CLOSED
```

### Example 3: Complaint Rejection

```
1. Citizen submits invalid complaint
   Status: submitted
   ↓
2. Moderator reviews and rejects
   Status: submitted → rejected
   Notification: Citizen receives rejection notice
   
❌ Complaint REJECTED (Terminal)
```

---

## Auto-Assignment Logic

**Category to Department Mapping**:
```python
{
    "road": "Road & Infrastructure",
    "water": "Water Supply",
    "electricity": "Electricity Board",
    "health": "Health Department",
    "education": "Education Department",
    "sanitation": "Sanitation & Waste Management",
    "other": "General Administration"
}
```

**Future Enhancement**: Machine learning for intelligent assignment based on:
- Location patterns
- Department workload
- Historical resolution times
- Officer expertise

---

## API Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/complaints/{id}/status` | PATCH | Required | Update complaint status |
| `/api/complaints/{id}/approve` | POST | MLA/Admin | Approve work completion |
| `/api/complaints/{id}/reject` | POST | MLA/Admin | Reject work, request rework |
| `/api/complaints/{id}/workflow` | GET | Required | Get allowed transitions |

---

## Security Features

**Workflow Validation**:
- ✅ Prevents invalid state transitions
- ✅ Enforces role-based permissions
- ✅ Validates constituency access
- ✅ Logs all changes with user tracking

**Access Control**:
- ✅ Non-admins can only access their constituency
- ✅ Citizens cannot change status
- ✅ Department officers can only mark as resolved
- ✅ Only MLA/Moderator/Admin can approve/reject

**Audit Trail**:
- ✅ Every status change logged
- ✅ User ID tracked
- ✅ Timestamp recorded
- ✅ Notes/comments preserved

---

## Database Updates

### Status Log Table
Tracks all status changes:
- `complaint_id` - Reference to complaint
- `old_status` - Previous status
- `new_status` - New status
- `changed_by` - User who made the change
- `note` - Reason/comment
- `created_at` - When changed

### Complaint Table (Work Approval Fields)
Added in previous migration:
- `work_approved` - Boolean flag
- `approved_by` - User ID
- `approved_at` - Timestamp
- `approval_comments` - Comments
- `rejected_by` - User ID
- `rejected_at` - Timestamp
- `rejection_reason` - Reason text

---

## Testing Workflow

### Test Status Transition

```bash
# Login as MLA
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543211"}' | jq -r '.otp')

AUTH=$(curl -s -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d "{\"phone\": \"+919876543211\", \"otp\": \"$TOKEN\"}" | jq -r '.access_token')

# Get workflow status
curl -H "Authorization: Bearer $AUTH" \
  http://localhost:8000/api/complaints/{id}/workflow | jq

# Update status
curl -X PATCH http://localhost:8000/api/complaints/{id}/status \
  -H "Authorization: Bearer $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "assigned",
    "note": "Assigned to Road Department"
  }' | jq
```

### Test Work Approval

```bash
# Approve work
curl -X POST http://localhost:8000/api/complaints/{id}/approve \
  -H "Authorization: Bearer $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "Work completed satisfactorily"
  }' | jq

# Reject work
curl -X POST http://localhost:8000/api/complaints/{id}/reject \
  -H "Authorization: Bearer $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Potholes still visible, please redo"
  }' | jq
```

---

## Frontend Integration (To Be Implemented)

### Status Update Component

```jsx
import { useState } from 'react';

const StatusUpdateButton = ({ complaint, onUpdate }) => {
  const [workflow, setWorkflow] = useState(null);
  
  useEffect(() => {
    // Fetch allowed transitions
    fetch(`/api/complaints/${complaint.id}/workflow`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setWorkflow(data));
  }, [complaint.id]);
  
  return (
    <div>
      <h3>Current Status: {workflow?.current_status}</h3>
      <p>Allowed actions:</p>
      {workflow?.allowed_transitions.map(status => (
        <button
          key={status}
          onClick={() => updateStatus(status)}
        >
          Mark as {status}
        </button>
      ))}
    </div>
  );
};
```

### Work Approval Component

```jsx
const WorkApprovalButtons = ({ complaint }) => {
  if (complaint.status !== 'resolved') return null;
  
  const approve = async () => {
    const comments = prompt('Approval comments:');
    await fetch(`/api/complaints/${complaint.id}/approve`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ comments })
    });
  };
  
  const reject = async () => {
    const reason = prompt('Rejection reason:');
    if (!reason || reason.length < 10) {
      alert('Please provide detailed reason');
      return;
    }
    await fetch(`/api/complaints/${complaint.id}/reject`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ reason })
    });
  };
  
  return (
    <div className="flex gap-2">
      <button onClick={approve} className="btn-success">
        ✓ Approve Work
      </button>
      <button onClick={reject} className="btn-danger">
        ✗ Request Rework
      </button>
    </div>
  );
};
```

---

## Configuration

### Notification Settings (To Add to config.py)

```python
# Email configuration
EMAIL_FROM: str = "noreply@janasamparka.gov.in"
SMTP_HOST: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USER: Optional[str] = None
SMTP_PASSWORD: Optional[str] = None

# SMS configuration
TWILIO_ACCOUNT_SID: Optional[str] = None
TWILIO_AUTH_TOKEN: Optional[str] = None
TWILIO_PHONE_NUMBER: Optional[str] = None

# Or AWS SNS
AWS_SNS_REGION: str = "ap-south-1"
AWS_ACCESS_KEY_ID: Optional[str] = None
AWS_SECRET_ACCESS_KEY: Optional[str] = None
```

---

## Next Steps

### Immediate (Phase 4 Completion)

1. **Integrate Notifications**
   - [ ] Configure SMTP or SendGrid for emails
   - [ ] Set up Twilio or AWS SNS for SMS
   - [ ] Connect notification calls in endpoints
   - [ ] Test email/SMS delivery

2. **Frontend Components**
   - [ ] Create StatusUpdateModal component
   - [ ] Create WorkApprovalCard component
   - [ ] Add workflow visualization
   - [ ] Show allowed actions based on role

3. **In-App Notifications**
   - [ ] Create notifications table
   - [ ] Build notification center UI
   - [ ] Add real-time updates (WebSocket)
   - [ ] Implement notification preferences

### Phase 5: Analytics & Reports

1. Department performance metrics
2. SLA tracking and alerts
3. Escalation automation
4. Custom report builder
5. Data export functionality

---

## Performance Considerations

**Workflow Validation**:
- Validation happens in-memory (fast)
- No database lookups for transition rules
- Caching can be added for role permissions

**Notifications**:
- Use background tasks (Celery) for sending
- Queue notifications to prevent blocking
- Batch notifications for efficiency
- Retry mechanism for failures

**Status Logs**:
- Indexed by complaint_id for fast queries
- Partition by date for large datasets
- Archive old logs periodically

---

## Error Handling

**Invalid Transition**:
```json
{
  "detail": "Invalid status transition from 'submitted' to 'closed'. Allowed transitions: ['assigned', 'rejected']"
}
```

**Permission Denied**:
```json
{
  "detail": "User with role 'citizen' is not authorized to transition from 'submitted' to 'assigned'"
}
```

**Constituency Access**:
```json
{
  "detail": "You can only approve complaints from your constituency"
}
```

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Workflow validation | 100% | ✅ Complete |
| Role-based permissions | All roles | ✅ Complete |
| Status transition tracking | All changes logged | ✅ Complete |
| Work approval process | Approve/Reject | ✅ Complete |
| Notification templates | 6 types | ✅ Complete |
| Email/SMS integration | Ready | 🔄 Config needed |

---

## Files Created/Modified

**New Files**:
1. `/backend/app/core/workflow.py` - Workflow state machine
2. `/backend/app/core/notifications.py` - Notification service
3. `/backend/app/schemas/workflow.py` - Workflow schemas

**Modified Files**:
1. `/backend/app/routers/complaints.py` - Enhanced with workflow
2. Integration points for notifications (TODO markers)

---

## Summary

Phase 4 delivers a **production-ready workflow system** with:

✅ **Smart State Management** - Prevents invalid transitions  
✅ **Role-Based Control** - Right person, right action  
✅ **Audit Trail** - Complete tracking of all changes  
✅ **Work Approval** - Quality control before closure  
✅ **Notification Infrastructure** - Ready for email/SMS  
✅ **Security** - Constituency isolation maintained  

**Next**: Integrate notification services and build frontend components!

---

**Status**: ✅ Phase 4 Core Complete  
**Ready For**: Frontend integration & notification service configuration
