# Git Commit Checklist

## Files to Commit

### Database Seeding Scripts
- [ ] `backend/seed_database.py` - Master seeding script
- [ ] `backend/create_moderator.py` - Moderator creation script
- [ ] `backend/create_department_users.py` - Department officers & auditors
- [ ] `backend/delete_dept_officers.py` - Utility script

### Documentation
- [ ] `SEEDING_GUIDE.md` - Complete restoration guide
- [ ] `GIT_COMMIT_CHECKLIST.md` - This file

### Frontend Changes
- [ ] `admin-dashboard/src/pages/Login.jsx` - Updated with correct phone numbers

### Other Files (if modified)
- [ ] `admin-dashboard/src/components/ComplaintMap.jsx` - Map center fix
- [ ] `admin-dashboard/src/pages/Map.jsx` - Map center prop

## Pre-Commit Verification

### 1. Verify All Phone Numbers are Correct (13 characters)
```bash
# Should return phone numbers with 10 digits after +91
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
for role in ['moderator', 'department_officer', 'auditor']:
    users = db.query(User).filter(User.role == role).all()
    for user in users:
        if len(user.phone) != 13:
            print(f'❌ WRONG: {user.name} - {user.phone} ({len(user.phone)} chars)')
        else:
            print(f'✅ OK: {user.name} - {user.phone}')
"
```

Expected: All users should have 13-character phone numbers

### 2. Test Seeding from Scratch
```bash
# Delete all test users
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
for role in ['moderator', 'department_officer', 'auditor']:
    db.query(User).filter(User.role == role).delete()
db.commit()
"

# Re-seed
docker compose exec backend python seed_database.py

# Verify counts
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
print(f'Moderators: {db.query(User).filter(User.role == \"moderator\").count()}')
print(f'Dept Officers: {db.query(User).filter(User.role == \"department_officer\").count()}')
print(f'Auditors: {db.query(User).filter(User.role == \"auditor\").count()}')
"
```

Expected output:
```
Moderators: 3
Dept Officers: 15
Auditors: 3
```

### 3. Test Frontend Login
- [ ] Go to http://localhost:3000/login
- [ ] Hard refresh browser (Cmd+Shift+R)
- [ ] Verify all phone numbers show 13 characters
- [ ] Test login with `+9199001000` / `demo`
- [ ] Should redirect to department officer dashboard

### 4. Check Git Status
```bash
git status
```

Should show:
```
modified:   admin-dashboard/src/pages/Login.jsx
modified:   admin-dashboard/src/components/ComplaintMap.jsx (if changed)
modified:   admin-dashboard/src/pages/Map.jsx (if changed)
new file:   backend/seed_database.py
new file:   SEEDING_GUIDE.md
new file:   GIT_COMMIT_CHECKLIST.md
```

## Git Commands

### Add Files
```bash
# Add seeding scripts
git add backend/seed_database.py
git add backend/create_moderator.py
git add backend/create_department_users.py
git add backend/delete_dept_officers.py

# Add documentation
git add SEEDING_GUIDE.md
git add GIT_COMMIT_CHECKLIST.md

# Add frontend changes
git add admin-dashboard/src/pages/Login.jsx
git add admin-dashboard/src/components/ComplaintMap.jsx
git add admin-dashboard/src/pages/Map.jsx
```

### Check Diff
```bash
# Review changes before committing
git diff --cached
```

### Commit
```bash
git commit -m "feat: Add database seeding scripts with correct phone numbers

- Add seed_database.py master seeding script
- Fix phone numbers to Indian format (13 chars: +91 + 10 digits)
- Update Login.jsx with correct department officer phones
- Add comprehensive SEEDING_GUIDE.md for state restoration
- Fix map center prop for correct complaint display

Test users created:
- 3 Moderators (+919900000000-02)
- 15 Department Officers (+9199001000-5200)
- 3 Auditors (+9199006000-02)

All users use password: demo
Can restore state anytime with: docker compose exec backend python seed_database.py"
```

### Push
```bash
# Push to remote
git push origin main

# Or if using a feature branch
git push origin feature/database-seeding
```

## Post-Push Verification

### On Another Machine (or Fresh Clone)
```bash
# 1. Clone repository
git clone <your-repo-url>
cd <repo-name>/janasamparka

# 2. Start containers
docker compose up -d

# 3. Wait for database to be ready
sleep 60

# 4. Run migrations (if needed)
docker compose exec backend alembic upgrade head

# 5. Seed database
docker compose exec backend python seed_database.py

# 6. Verify
curl http://localhost:3000/login
```

Should see login page with all test user buttons showing correct 13-character phone numbers.

## Rollback (If Needed)

### Undo Last Commit (Not Pushed)
```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Already Pushed)
```bash
git revert HEAD
git push origin main
```

## Tags (Optional but Recommended)

```bash
# Create a tag for this stable state
git tag -a v1.0.0-seeding -m "Add database seeding with correct phone numbers"

# Push tag
git push origin v1.0.0-seeding
```

## Branches

### Current Branch
```bash
git branch --show-current
```

### Create Feature Branch (if not done already)
```bash
git checkout -b feature/database-seeding
# Make changes
git add .
git commit -m "..."
git push origin feature/database-seeding
```

## Summary Checklist

- [ ] All phone numbers are 13 characters
- [ ] Seeding script tested and works
- [ ] Frontend shows correct phone numbers
- [ ] Login tested with sample user
- [ ] All files added to git
- [ ] Commit message is descriptive
- [ ] Changes pushed to remote
- [ ] Documentation is complete
- [ ] State can be restored from scratch

## Ready to Push? ✅

Run this final verification:
```bash
# 1. Status clean except for tracked changes
git status

# 2. All tests pass (if you have tests)
# docker compose exec backend pytest

# 3. Frontend builds without errors
docker compose logs frontend --tail 20

# 4. Backend running without errors
docker compose logs backend --tail 20

# 5. Can seed successfully
docker compose exec backend python seed_database.py
```

If all checks pass, you're ready to push! 🚀
