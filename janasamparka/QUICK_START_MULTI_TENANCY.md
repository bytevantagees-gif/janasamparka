# Quick Start: Multi-Tenancy Testing

## Current Status

✅ **Multi-tenancy is ACTIVE** - Data is automatically filtered by constituency based on user role.

## Test Scenarios

### Scenario 1: View All Data (Development Mode)

**Without Authentication:**
```bash
curl http://localhost:8000/api/complaints/
# Returns: 20 complaints (12 from Puttur + 8 from Mangalore)
```

**Frontend (No Login):**
- Visit: http://localhost:3000/map
- **Expected**: See all 20 complaints on map
- **Current**: Works in development mode

### Scenario 2: Puttur MLA Login (Future - When Auth is Enabled)

**Credentials:**
- Phone: `+919876543211`
- OTP: `123456`

**Expected Behavior:**
- Map shows only **12 Puttur complaints** (12.76°N, 75.21°E)
- Cannot see Mangalore complaints
- Cannot see other constituencies' data

### Scenario 3: Mangalore Moderator Login (Future - When Auth is Enabled)

**Credentials:**
- Phone: `+919876543213`
- OTP: `123456`

**Expected Behavior:**
- Map shows only **8 Mangalore complaints** (12.91°N, 74.86°E)
- Cannot see Puttur complaints
- Cannot access Puttur data

### Scenario 4: Admin Login (Future - When Auth is Enabled)

**Credentials:**
- Phone: `+919876543210`
- OTP: `123456`

**Expected Behavior:**
- Map shows **all 20 complaints**
- Can switch between constituencies
- Full system access

## Data Distribution

| Constituency | Complaints | Coordinates | Test Users |
|-------------|-----------|-------------|------------|
| **Puttur** | 12 | 12.76°N, 75.21°E | MLA, Moderator, Citizen |
| **Mangalore North** | 8 | 12.91°N, 74.86°E | Moderator |
| **Udupi** | 0 | - | None |

## How It Works

### Backend Logic

```python
# In complaints API endpoint
constituency_filter = get_user_constituency_id(current_user)

if constituency_filter:
    # Non-admin user: filter by their constituency
    query = query.filter(Complaint.constituency_id == constituency_filter)
else:
    # Admin or no auth: show all
    pass
```

### Role-Based Filtering

```
Current User → Extract Role → Determine Filter

Admin         → No Filter     → See ALL complaints
MLA           → Constituency  → See ONLY constituency complaints  
Moderator     → Constituency  → See ONLY constituency complaints
Dept Officer  → Constituency  → See ONLY constituency complaints
Citizen       → Constituency  → See ONLY constituency complaints
No Auth       → No Filter     → See ALL (development only)
```

## Next Steps

### 1. Enable Frontend Authentication

Update `admin-dashboard/src/contexts/AuthContext.jsx`:
- Store constituency_id in user object
- Pass JWT token with API requests

### 2. Test with Different Users

Login with each test user and verify map shows correct data:
- Puttur users should see Puttur area only
- Mangalore users should see Mangalore area only
- Admin should see both areas

### 3. Add Constituency Display

Show current constituency in header:
```jsx
{user && user.role !== 'admin' && (
  <div>Viewing: {user.constituency_name}</div>
)}
```

## Verification Commands

### Check Complaint Distribution

```bash
docker exec janasamparka_db psql -U janasamparka -d janasamparka_db -c "
SELECT 
    c.name as constituency, 
    COUNT(comp.id) as complaints,
    ROUND(AVG(comp.lat::numeric), 2) as avg_lat,
    ROUND(AVG(comp.lng::numeric), 2) as avg_lng
FROM constituencies c
LEFT JOIN complaints comp ON c.id = comp.constituency_id
GROUP BY c.name
ORDER BY c.name;
"
```

### List All Test Users

```bash
docker exec janasamparka_db psql -U janasamparka -d janasamparka_db -c "
SELECT 
    name, 
    phone, 
    role,
    (SELECT name FROM constituencies WHERE id = users.constituency_id) as constituency
FROM users
WHERE phone LIKE '+9198765432%'
ORDER BY role, name;
"
```

### Test API Without Auth

```bash
# Get all complaints (development mode)
curl -s http://localhost:8000/api/complaints/ | jq '.total'
# Expected: 20

# Get specific complaint
COMPLAINT_ID=$(curl -s http://localhost:8000/api/complaints/ | jq -r '.complaints[0].id')
curl -s http://localhost:8000/api/complaints/$COMPLAINT_ID | jq '{title, constituency_id}'
```

## Important Notes

🔴 **Current State**: Multi-tenancy is implemented but **not enforced** because authentication is optional in development.

🟡 **Development Mode**: All users see all data (no JWT required)

🟢 **Production Ready**: When you enable `require_auth` dependency, filtering will be enforced automatically

## Enabling Full Multi-Tenancy

To enforce authentication and constituency filtering:

1. **Update complaints.py:**
```python
# Change from:
constituency_filter: Optional[UUID] = Depends(get_user_constituency_id)

# To:
current_user: User = Depends(require_auth),
constituency_filter: Optional[UUID] = Depends(get_user_constituency_id)
```

2. **Enable in frontend:**
```javascript
// In api.js, ensure token is sent
config.headers.Authorization = `Bearer ${token}`;
```

3. **Test thoroughly** with each user role

---

**Ready to Test**: ✅ Backend is ready, waiting for frontend auth integration
