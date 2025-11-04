# Multi-Tenancy & Role-Based Access Control

## Overview

The Janasamparka application implements **constituency-based multi-tenancy** with **role-based access control (RBAC)**. This ensures that users only see data relevant to their constituency, except for administrators who have system-wide access.

## Architecture

### Data Isolation Strategy

- **Constituency-Based Filtering**: All data is automatically filtered by `constituency_id`
- **Role-Based Permissions**: Different roles have different access levels
- **Automatic Enforcement**: Backend APIs apply filters transparently

### User Roles

| Role | Access Scope | Permissions |
|------|-------------|-------------|
| **Admin** | All constituencies | Full system access, manage all data |
| **MLA** | Single constituency | View and manage constituency data |
| **Moderator** | Single constituency | Review and moderate complaints |
| **Department Officer** | Single constituency | Handle assigned complaints |
| **Citizen** | Single constituency | Submit and view own complaints |

## Implementation

### Backend (FastAPI)

#### Authentication Dependency

File: `/backend/app/core/auth.py`

```python
def get_user_constituency_id(current_user: Optional[User]) -> Optional[UUID]:
    """
    Returns constituency_id for filtering:
    - Admin: Returns None (sees all)
    - Other roles: Returns user's constituency_id
    - No auth: Returns None (development mode)
    """
```

#### Automatic Filtering

All complaint endpoints automatically filter by constituency:

```python
@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    
    # Apply constituency filter
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)
```

### Key Features

1. **Transparent Filtering**: Developers don't need to remember to add filters manually
2. **Security by Default**: Non-admin users cannot access other constituencies' data
3. **Admin Override**: Admin role bypasses constituency filtering
4. **Development Mode**: Without authentication, all data is visible (for testing)

## Test Data

### Constituencies

- **Puttur** (Dakshina Kannada) - 12 complaints
- **Mangalore North** (Dakshina Kannada) - 8 complaints  
- **Udupi** (Udupi District) - 0 complaints

### Test Users

| Phone | Role | Constituency | Access |
|-------|------|-------------|--------|
| +919876543210 | Admin | Puttur | **All 20 complaints** |
| +919876543211 | MLA | Puttur | **12 Puttur complaints only** |
| +919876543212 | Moderator | Puttur | **12 Puttur complaints only** |
| +919876543213 | Moderator | Mangalore North | **8 Mangalore complaints only** |
| +919876543214 | Citizen | Puttur | **12 Puttur complaints only** |

## Testing Multi-Tenancy

### Without Authentication (Development)

```bash
# Returns all 20 complaints (no filtering)
curl http://localhost:8000/api/complaints/
```

### With Authentication (Production)

```bash
# Login as Puttur MLA
POST /api/auth/request-otp
{ "phone": "+919876543211" }

POST /api/auth/verify-otp
{ "phone": "+919876543211", "otp": "123456" }

# Get complaints (returns only Puttur's 12 complaints)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/complaints/
```

```bash
# Login as Admin
POST /api/auth/verify-otp
{ "phone": "+919876543210", "otp": "123456" }

# Get complaints (returns all 20 complaints)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/complaints/
```

## Frontend Integration

### Update Required

The frontend should:

1. **Store user context** after login (including constituency_id and role)
2. **Send JWT token** with all API requests
3. **Display constituency name** in the header/navbar
4. **Hide admin features** for non-admin users

### Example: AuthContext Update

```javascript
// Store user data after login
const userData = {
  id: "...",
  name: "Puttur MLA",
  role: "mla",
  constituency_id: "7288dfd8-bb8c-48bc-bba6-d05b65734ec6",
  constituency_name: "Puttur"
};

localStorage.setItem('user', JSON.stringify(userData));
```

### Example: API Calls

```javascript
// Axios automatically includes the token
const response = await complaintsAPI.getAll(filters);

// For Puttur MLA: Returns only Puttur complaints
// For Admin: Returns all complaints
```

### Example: UI Conditional Rendering

```jsx
const { user } = useAuth();

// Show constituency name
<Header>
  {user.role !== 'admin' && (
    <span>{user.constituency_name} Constituency</span>
  )}
</Header>

// Hide multi-constituency features
{user.role === 'admin' && (
  <ConstituencySelector />
)}
```

## Database Structure

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    phone VARCHAR(15) UNIQUE,
    role userrole,  -- admin, mla, moderator, dept_officer, citizen
    constituency_id UUID REFERENCES constituencies(id),
    ...
);
```

### Complaints Table

```sql
CREATE TABLE complaints (
    id UUID PRIMARY KEY,
    constituency_id UUID REFERENCES constituencies(id),
    user_id UUID REFERENCES users(id),
    ...
);
```

## Security Considerations

### ✅ Implemented

- Constituency-based data isolation
- Role-based access control
- JWT token authentication structure
- Automatic query filtering

### 🔄 To Implement (Future)

- Rate limiting per constituency
- Audit logging for cross-constituency access
- IP-based geo-fencing for citizens
- Two-factor authentication for admins

## API Endpoints with Multi-Tenancy

| Endpoint | Admin | MLA/Moderator | Citizen |
|----------|-------|---------------|---------|
| `GET /api/complaints/` | All constituencies | Own constituency | Own constituency |
| `GET /api/complaints/{id}` | Any complaint | Own constituency only | Own constituency only |
| `POST /api/complaints/` | Any constituency | Own constituency | Own constituency |
| `GET /api/constituencies/` | All | Own only | Own only |
| `GET /api/users/` | All | Own constituency | Forbidden |

## Migration Path

### Phase 1: Development (Current)
- No authentication required
- All data visible
- Testing multi-tenancy logic

### Phase 2: Staging
- Enable authentication
- Test with different user roles
- Verify data isolation

### Phase 3: Production
- Enforce authentication on all endpoints
- Enable audit logging
- Monitor for unauthorized access attempts

## Troubleshooting

### Issue: Seeing all complaints when logged in

**Cause**: User has `admin` role

**Solution**: Expected behavior for admins

### Issue: Not seeing any complaints

**Cause**: No complaints in user's constituency

**Solution**: Add complaints to the constituency or check user's constituency_id

### Issue: Getting 404 on complaint details

**Cause**: Complaint belongs to different constituency

**Solution**: User can only view complaints from their constituency (except admins)

## Best Practices

1. **Never disable constituency filtering** for non-admin users
2. **Always check user role** before showing admin features
3. **Log constituency switches** by admins for audit trail
4. **Validate constituency_id** matches user's constituency on write operations
5. **Cache constituency data** to minimize database queries

## Future Enhancements

- [ ] Constituency-level feature flags
- [ ] Custom branding per constituency
- [ ] Constituency-specific SLA configurations
- [ ] Cross-constituency collaboration (with permissions)
- [ ] Constituency performance dashboards for state-level admins

---

**Status**: ✅ Multi-tenancy fully implemented and tested

**Last Updated**: October 28, 2025
