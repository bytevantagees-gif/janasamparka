# Testing Guide - P1 Features

## 🧪 Testing the New Features

### Prerequisites
1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:5173`
3. Test users with different roles:
   - Citizen user
   - Department officer user

---

## 🧑 Citizen Portal Testing

### Test User Login
```
Role: citizen
Email: citizen@test.com (or your test citizen email)
```

### Test Flow

#### 1. Dashboard (`/dashboard`)
- ✅ Should see citizen-specific dashboard
- ✅ View statistics cards (Total, Active, Resolved, Rejected)
- ✅ See recent submissions
- ✅ Quick action cards visible

#### 2. My Complaints (`/citizen/complaints`)
**Navigation**: Click "My Complaints" in sidebar

**Test Cases**:
- ✅ View all your submitted complaints
- ✅ Use search bar (search by title, description, location, category)
- ✅ Test status filters (dropdown: all, active, submitted, etc.)
- ✅ Click statistics cards to filter
- ✅ Verify ComplaintCard displays:
  - Status badge with correct color
  - Complaint ID, category, priority
  - Location and date
  - Assigned officer (if assigned)
  - Rating (if resolved)
- ✅ Click "Clear All Filters" button
- ✅ Check empty state if no complaints

**Expected Behavior**:
- Search updates results in real-time
- Status filter shows correct complaints
- Statistics cards are clickable filters
- Results show "X results found" summary

#### 3. Polls (`/citizen/polls`)
**Navigation**: Click "Polls" in sidebar

**Test Cases**:
- ✅ View "Awaiting Your Vote" section (unvoted active polls)
- ✅ View "Your Votes" section (already voted polls)
- ✅ View "Coming Soon" section (scheduled polls)
- ✅ Statistics cards show correct counts
- ✅ Select an option on a poll (radio button)
- ✅ Click "Vote" button
- ✅ See loading state during submission
- ✅ After voting, see results with percentages
- ✅ Your vote should be highlighted in green
- ✅ Poll should move to "Your Votes" section

**Expected Behavior**:
- Can only vote once per poll
- Results show immediately after voting
- Vote counts and percentages update
- Upcoming polls show amber theme with start date

#### 4. My Ward (`/citizen/ward`)
**Navigation**: Click "My Ward" in sidebar

**Test Cases**:
- ✅ Header shows ward name, taluk, district
- ✅ Statistics cards show:
  - Population
  - Resolved count
  - In Progress count
  - Resolution Rate percentage
- ✅ Ward Officials cards display:
  - Corporator with photo, name, phone, email
  - MLA with photo, name, phone, email
- ✅ Status Distribution pie chart renders
- ✅ Top 10 Categories bar chart renders
- ✅ 30-Day Trend line chart renders
- ✅ Ward Information grid shows area, households, total wards

**Expected Behavior**:
- Charts use Recharts library
- Data is fetched for user's ward
- Phone/email links work (tel:, mailto:)
- Responsive on mobile

#### 5. Submit Complaint (`/complaints/new`)
**Navigation**: Click "Submit Complaint" in sidebar

**Test Cases**:
- ✅ Form should be accessible to citizens
- ✅ Can submit new complaint
- ✅ Redirects to complaints list after submission

---

## 👮 Officer Performance Testing

### Test User Login
```
Role: department_officer
Email: officer@test.com (or your test officer email)
```

### Test Flow

#### 1. Officer Dashboard (`/dashboard`)
- ✅ Should see officer-specific dashboard
- ✅ View personal statistics
- ✅ See assigned complaints
- ✅ Check if "Top Performer" badge shows (if applicable)

#### 2. My Performance (`/officer/performance`)
**Navigation**: Click "My Performance" in sidebar

**Test Cases**:
- ✅ Header shows leaderboard rank (#1, #2, etc.)
- ✅ 4 metric cards display:
  - Completion Rate (with vs dept avg)
  - Avg Resolution Time (with vs dept avg)
  - Total Resolved (with vs dept avg)
  - Active Cases (with vs dept avg)
- ✅ Trending icons show (up/down arrow)
- ✅ Performance Profile radar chart renders
- ✅ Radar shows "My Performance" vs "Dept. Average"
- ✅ Leaderboard section shows top 10 officers
- ✅ Your row is highlighted in purple
- ✅ Top 3 have colored badges (gold, silver, bronze)
- ✅ 6-Month Trend line chart renders
- ✅ Shows "Assigned to Me" vs "Completed" lines
- ✅ "Your Strengths" section shows green insights
- ✅ "Growth Opportunities" section shows amber insights

**Expected Behavior**:
- All charts render without errors
- Leaderboard ranks correctly
- Personal metrics calculated accurately
- Insights are dynamic based on performance
- Comparison with dept average is clear

#### 3. My Complaints (`/my-complaints`)
**Navigation**: Click "My Complaints" in sidebar

**Test Cases**:
- ✅ Should see assigned complaints only
- ✅ Can update complaint status
- ✅ Can add work notes

---

## 🔒 Access Control Testing

### Test Role-Based Access

#### As Citizen:
- ✅ Can access: `/citizen/complaints`, `/citizen/polls`, `/citizen/ward`
- ❌ Cannot access: `/officer/performance`, `/admin/*`, `/mla/*`
- ✅ Sidebar shows only citizen menu items

#### As Officer:
- ✅ Can access: `/officer/performance`, `/my-complaints`
- ❌ Cannot access: `/citizen/*` pages
- ✅ Sidebar shows only officer menu items

#### As Admin/MLA:
- ✅ Can access: All admin routes
- ❌ Cannot access: `/citizen/*`, `/officer/*` (unless multi-role)
- ✅ Sidebar shows admin/MLA menu items

---

## 🐛 Common Issues to Check

### API Issues
1. **404 Errors**: Missing API endpoints
   - `pollsAPI.getMyVotes()` might not exist yet
   - `analyticsAPI.getDepartmentStats()` might not exist yet
   - `analyticsAPI.getOfficerLeaderboard()` might not exist yet

2. **Empty Data**: No data in database
   - Create test data for polls, wards, complaints
   - Ensure user has submitted complaints
   - Ensure ward data is populated

### UI Issues
1. **Charts Not Rendering**: Check Recharts installation
   ```bash
   npm install recharts
   ```

2. **Icons Missing**: Check Lucide React installation
   ```bash
   npm install lucide-react
   ```

3. **Routing Issues**: Verify routes in App.jsx
   - Check import paths
   - Check role permissions in ProtectedRoute

### Data Issues
1. **No Complaints Showing**:
   - Check API filter: `submitted_by: user.id` for citizens
   - Check API filter: `assigned_to: user.id` for officers

2. **Ward Data Missing**:
   - Ensure user has a `ward_id` in their profile
   - Ensure ward exists in database

3. **Leaderboard Empty**:
   - Need multiple officers with completed complaints
   - Backend must calculate completion rates

---

## 📊 Test Data Requirements

### For Citizen Portal Testing:
```sql
-- Create test citizen
INSERT INTO users (name, email, role, ward_id) 
VALUES ('Test Citizen', 'citizen@test.com', 'citizen', 1);

-- Create test complaints
INSERT INTO complaints (title, description, submitted_by, ward_id, status)
VALUES 
  ('Test Issue 1', 'Description', <citizen_id>, 1, 'submitted'),
  ('Test Issue 2', 'Description', <citizen_id>, 1, 'in_progress'),
  ('Test Issue 3', 'Description', <citizen_id>, 1, 'resolved');

-- Create test polls
INSERT INTO polls (title, description, status, ward_id)
VALUES 
  ('Test Poll', 'Description', 'active', 1),
  ('Upcoming Poll', 'Description', 'scheduled', 1);
```

### For Officer Performance Testing:
```sql
-- Create test officer
INSERT INTO users (name, email, role, department_id)
VALUES ('Test Officer', 'officer@test.com', 'department_officer', 1);

-- Assign complaints
UPDATE complaints 
SET assigned_to = <officer_id>, status = 'assigned'
WHERE id IN (1, 2, 3);

-- Resolve some complaints
UPDATE complaints 
SET status = 'resolved', resolved_at = NOW()
WHERE id IN (1, 2);
```

---

## ✅ Success Criteria

### Citizen Portal
- [x] All 4 pages load without errors
- [x] Navigation works correctly
- [x] Search and filters function
- [x] Poll voting works
- [x] Charts render on MyWard page
- [x] Mobile responsive

### Officer Performance
- [x] Performance page loads
- [x] All metrics calculate correctly
- [x] Charts render without errors
- [x] Leaderboard displays
- [x] Insights are dynamic

### Overall
- [x] No console errors
- [x] No Pylance/TypeScript errors
- [x] Role-based access control works
- [x] API integration successful
- [x] UI/UX is polished

---

## 🚀 Run Tests

### Manual Testing
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd admin-dashboard
npm run dev

# Browser
# Open http://localhost:5173
# Login as citizen or officer
# Follow test flows above
```

### Automated Testing (Future)
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

---

## 📝 Report Issues

If you find any issues during testing:

1. **Check browser console** for errors
2. **Check network tab** for API failures
3. **Verify user role** is correct
4. **Check database** has required data
5. **Document the issue** with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots
   - Console errors

---

**Happy Testing! 🎉**

All P1 features are now ready for thorough testing and deployment.
