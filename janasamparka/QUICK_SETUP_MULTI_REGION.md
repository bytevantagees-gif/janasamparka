# 🚀 Quick Setup: Multi-Region Access Control

## Testing Constituencies with Multi-Taluk Support

### 1. Run Migration (Add Taluks Support)

```bash
# Connect to database
docker exec -it janasamparka-db psql -U postgres -d janasamparka_db

# Run migration
\i /docker-entrypoint-initdb.d/add_constituency_taluks.sql

# Or manually:
ALTER TABLE constituencies ADD COLUMN IF NOT EXISTS taluks TEXT[] DEFAULT '{}';

UPDATE constituencies SET taluks = ARRAY['Puttur', 'Kadaba'] WHERE code = 'PUT001';
UPDATE constituencies SET taluks = ARRAY['Mangalore'] WHERE code = 'MNG001';
UPDATE constituencies SET taluks = ARRAY['Bantwal'] WHERE code = 'BAN001';

# Verify
SELECT name, code, taluks FROM constituencies;
```

Expected Output:
```
       name        | code   |      taluks
-------------------+--------+------------------
 Puttur            | PUT001 | {Puttur,Kadaba}
 Mangalore North   | MNG001 | {Mangalore}
 Bantwal           | BAN001 | {Bantwal}
```

---

### 2. Assign Users to Constituencies

#### Assign Existing Test Users

```sql
-- Get constituency IDs
SELECT id, code, name FROM constituencies;

-- Assign Citizens to Constituencies
UPDATE users 
SET constituency_id = (SELECT id FROM constituencies WHERE code = 'PUT001')
WHERE phone IN ('+919988770001', '+919988770002', '+919988770003');

UPDATE users 
SET constituency_id = (SELECT id FROM constituencies WHERE code = 'MNG001')
WHERE phone IN ('+919988770004', '+919988770005');

-- Assign Officers to Constituencies
UPDATE users 
SET constituency_id = (SELECT id FROM constituencies WHERE code = 'PUT001')
WHERE phone = '+918242226101' AND role = 'department_officer';

UPDATE users 
SET constituency_id = (SELECT id FROM constituencies WHERE code = 'MNG001')
WHERE phone = '+918242226102' AND role = 'department_officer';

-- Assign Moderators to Constituencies
UPDATE users 
SET constituency_id = (SELECT id FROM constituencies WHERE code = 'PUT001')
WHERE phone = '+917676001111' AND role = 'moderator';

-- Assign Auditors to Constituencies
UPDATE users 
SET constituency_id = (SELECT id FROM constituencies WHERE code = 'MNG001')
WHERE phone = '+917676002222' AND role = 'auditor';

-- Verify assignments
SELECT u.name, u.phone, u.role, c.name as constituency
FROM users u
LEFT JOIN constituencies c ON u.constituency_id = c.id
WHERE u.role IN ('citizen', 'department_officer', 'moderator', 'auditor')
ORDER BY u.role, c.name;
```

---

### 3. Test Data: Complaints by Constituency

```sql
-- Ensure complaints are linked to constituencies
UPDATE complaints c
SET constituency_id = u.constituency_id
FROM users u
WHERE c.user_id = u.id AND c.constituency_id IS NULL;

-- Verify complaint distribution
SELECT 
  co.name as constituency,
  co.taluks,
  COUNT(c.id) as total_complaints,
  COUNT(CASE WHEN c.status = 'submitted' THEN 1 END) as submitted,
  COUNT(CASE WHEN c.status IN ('resolved', 'closed') THEN 1 END) as resolved
FROM constituencies co
LEFT JOIN complaints c ON c.constituency_id = co.id
GROUP BY co.id, co.name, co.taluks
ORDER BY total_complaints DESC;
```

Expected Output:
```
  constituency   |      taluks       | total | submitted | resolved
-----------------+-------------------+-------+-----------+----------
 Puttur          | {Puttur,Kadaba}   |   12  |     4     |    5
 Mangalore North | {Mangalore}       |    8  |     3     |    3
 Bantwal         | {Bantwal}         |    5  |     2     |    2
```

---

### 4. Test Login & Constituency Filtering

#### Test as Puttur Citizen
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919988770001", "otp": "123456"}'

# Response includes: access_token, user with constituency_id

# 2. Fetch complaints (should show ONLY Puttur complaints)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/complaints

# Expected: Only complaints from Puttur constituency
```

#### Test as Mangalore Officer
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918242226102", "otp": "123456"}'

# 2. Fetch assigned complaints (should show ONLY Mangalore complaints assigned to this officer)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/my-complaints

# Expected: Only Mangalore complaints assigned to this officer
```

#### Test as Admin (All Constituencies)
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "otp": "123456"}'

# 2. Fetch all complaints (no constituency filter)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/complaints

# Expected: ALL complaints from all constituencies
```

---

### 5. Frontend Testing

#### Citizen Login Flow
```
1. Open http://localhost:5173
2. Login as +919988770001 (Puttur citizen)
3. If first time:
   - See ConstituencySelector
   - Select "Puttur"
   - Dashboard shows Puttur data only
4. If returning:
   - Go directly to dashboard
   - See "My Submissions" filtered by Puttur
```

#### Officer Login Flow
```
1. Login as +918242226101 (Puttur officer)
2. Dashboard shows:
   - "Your Region: Puttur"
   - "Taluks: Puttur, Kadaba"
   - Work queue: ONLY Puttur complaints assigned to this officer
3. Cannot see Mangalore or Bantwal complaints
```

#### Moderator Login Flow
```
1. Login as +917676001111 (Puttur moderator)
2. Moderator Control Center shows:
   - "Moderating: Puttur"
   - Triage queue: ONLY Puttur new submissions
   - Pending review: ONLY Puttur long-running cases
```

---

### 6. Visual Indicators (Already Implemented)

All dashboards show constituency info:

**Citizen:**
```jsx
<p>Submit complaints, feedback, ideas or queries - we're here to help!</p>
```

**Officer:**
```jsx
<p>{user?.constituency_name || 'All Constituencies'}</p>
// Shows: "Puttur" or "Mangalore North"
```

**Moderator:**
```jsx
<p>{user?.name || 'Moderator'} • {user?.constituency_name || 'All Constituencies'}</p>
```

---

### 7. Verify Multi-Taluk Display

```sql
-- Query to see taluks
SELECT 
  u.name as user_name,
  u.role,
  c.name as constituency,
  c.taluks
FROM users u
JOIN constituencies c ON u.constituency_id = c.id
WHERE u.role IN ('department_officer', 'moderator', 'mla')
ORDER BY c.name;
```

Expected:
```
  user_name     |      role          | constituency |      taluks
----------------+--------------------+--------------+------------------
 Officer Kumar  | department_officer | Puttur       | {Puttur,Kadaba}
 MLA Sharma     | mla                | Puttur       | {Puttur,Kadaba}
```

---

### 8. Common Issues & Fixes

#### Issue: Users not assigned to constituency
```sql
-- Check unassigned users
SELECT id, name, phone, role 
FROM users 
WHERE constituency_id IS NULL 
AND role != 'admin';

-- Fix: Assign to default constituency
UPDATE users 
SET constituency_id = (SELECT id FROM constituencies WHERE code = 'PUT001')
WHERE constituency_id IS NULL AND role = 'citizen';
```

#### Issue: Complaints not linked to constituency
```sql
-- Check orphaned complaints
SELECT id, title, user_id 
FROM complaints 
WHERE constituency_id IS NULL;

-- Fix: Link via user's constituency
UPDATE complaints c
SET constituency_id = u.constituency_id
FROM users u
WHERE c.user_id = u.id AND c.constituency_id IS NULL;
```

#### Issue: Officer sees all complaints instead of just their constituency
```
Problem: Backend filtering not working
Solution: Ensure get_user_constituency_id dependency is used in endpoints

# Check complaints.py endpoint:
@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),  # ✅ This must exist
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    if constituency_filter:
        query = query.filter(Complaint.constituency_id == constituency_filter)  # ✅ Apply filter
```

---

### 9. Test Matrix

| User Type | Phone          | Constituency | Expected Behavior                          |
|-----------|----------------|--------------|---------------------------------------------|
| Citizen   | +919988770001  | Puttur       | See only Puttur submissions                |
| Citizen   | +919988770004  | Mangalore    | See only Mangalore submissions             |
| Officer   | +918242226101  | Puttur       | Work queue: Puttur complaints (assigned)   |
| Officer   | +918242226102  | Mangalore    | Work queue: Mangalore complaints (assigned)|
| Moderator | +917676001111  | Puttur       | Triage: Puttur new submissions only        |
| Auditor   | +917676002222  | Mangalore    | Audit: Mangalore compliance metrics        |
| Admin     | +919876543210  | None         | See ALL constituencies (system-wide)       |

---

### 10. Next Steps

✅ **Completed:**
- Multi-taluk database schema
- Backend filtering by constituency
- Frontend terminology update (Submissions)
- Documentation created

⏳ **Pending:**
- Update officer/moderator/auditor dashboards to show taluks
- Admin UI for constituency assignment
- Multi-taluk visual display in dashboards

---

### 11. Quick Verification Commands

```bash
# Check if backend is filtering correctly
curl -H "Authorization: Bearer <citizen-token>" \
  http://localhost:8000/api/complaints | jq '.complaints[].constituency_id' | sort -u

# Should return only ONE constituency_id (the citizen's constituency)

# Check if admin sees all
curl -H "Authorization: Bearer <admin-token>" \
  http://localhost:8000/api/complaints | jq '.complaints[].constituency_id' | sort -u

# Should return MULTIPLE constituency_ids
```

---

**Last Updated:** October 30, 2024  
**Migration Status:** Ready to Apply  
**Testing Status:** Awaiting Verification
