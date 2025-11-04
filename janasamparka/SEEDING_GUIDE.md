# Database Seeding & State Restoration Guide

## Overview
This guide explains how to seed the database with test users and restore the application state at any time.

## Database State Includes

### Users by Role:
- **3 Moderators** - One per constituency
- **15 Department Officers** - 5 departments × 3 constituencies
- **3 Auditors** - One per constituency
- **4 MLAs** - Already created
- **1 Admin** - Already created
- **Citizens** - Created via app registration

### Phone Number Format
All phone numbers follow Indian format: **+91** followed by **10 digits** (13 characters total)

## Seeding the Database

### Quick Method (Recommended)
```bash
# From the janasamparka directory
docker compose exec backend python seed_database.py
```

This single command will:
- ✅ Check for existing users (no duplicates)
- ✅ Create all moderators, department officers, and auditors
- ✅ Assign officers to correct departments and constituencies
- ✅ Print summary and login credentials

### Manual Method (Individual Scripts)
```bash
# Create moderators only
docker compose exec backend python create_moderator.py

# Create department officers and auditors
docker compose exec backend python create_department_users.py
```

## Login Credentials

### Moderators (3 users)
- **Puttur:**           `+919900000000`
- **Mangalore North:**  `+919900000001`
- **Udupi:**            `+919900000002`

### Department Officers (15 users)

**Puttur:**
- PWD:          `+9199001000`
- Water:        `+9199002000`
- Electricity:  `+9199003000`
- Health:       `+9199004000`
- Education:    `+9199005000`

**Mangalore North:**
- PWD:          `+9199001100`
- Water:        `+9199002100`
- Electricity:  `+9199003100`
- Health:       `+9199004100`
- Education:    `+9199005100`

**Udupi:**
- PWD:          `+9199001200`
- Water:        `+9199002200`
- Electricity:  `+9199003200`
- Health:       `+9199004200`
- Education:    `+9199005200`

### Auditors (3 users)
- **Puttur:**           `+9199006000`
- **Mangalore North:**  `+9199006001`
- **Udupi:**            `+9199006002`

### Default Password
All test users use password: **`demo`**

## Restoring State from Scratch

### Complete Reset & Restore
```bash
# 1. Stop all containers
docker compose down

# 2. Remove database volume (⚠️ DESTROYS ALL DATA)
docker volume rm janasamparka_postgres_data

# 3. Start fresh
docker compose up -d

# 4. Wait for database to initialize (30-60 seconds)
docker compose logs db | grep "database system is ready"

# 5. Run migrations (if needed)
docker compose exec backend alembic upgrade head

# 6. Seed the database
docker compose exec backend python seed_database.py

# 7. Verify frontend is running
curl http://localhost:3000
```

### Soft Reset (Keep Structure, Reset Data)
```bash
# 1. Delete test users only
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
roles = ['moderator', 'department_officer', 'auditor']
for role in roles:
    users = db.query(User).filter(User.role == role).all()
    for user in users:
        db.delete(user)
db.commit()
print('✅ Deleted all test users')
"

# 2. Re-seed
docker compose exec backend python seed_database.py
```

## Quick Verification

### Check User Counts
```bash
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
for role in ['moderator', 'department_officer', 'auditor']:
    count = db.query(User).filter(User.role == role).count()
    print(f'{role:20} {count:3} users')
"
```

Expected output:
```
moderator                 3 users
department_officer       15 users
auditor                   3 users
```

### Test Login
1. Go to: http://localhost:3000/login
2. Enter any test phone number (e.g., `+9199001000`)
3. Password: `demo`
4. Should redirect to appropriate dashboard

## Git Workflow

### Before Committing
```bash
# Make sure seeding scripts are tracked
git add backend/seed_database.py
git add backend/create_moderator.py
git add backend/create_department_users.py
git add SEEDING_GUIDE.md

# Commit
git commit -m "Add database seeding scripts and restoration guide"
```

### After Cloning Repository
```bash
# 1. Start containers
docker compose up -d

# 2. Wait for services to be ready
sleep 60

# 3. Seed database
docker compose exec backend python seed_database.py

# 4. Ready to develop!
```

## Database Backup & Restore (Production)

### Create Backup
```bash
# Backup to file
docker compose exec db pg_dump -U janasamparka janasamparka > backup_$(date +%Y%m%d).sql

# Or with compression
docker compose exec db pg_dump -U janasamparka janasamparka | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore from Backup
```bash
# From plain SQL file
docker compose exec -T db psql -U janasamparka janasamparka < backup_20241104.sql

# From compressed file
gunzip -c backup_20241104.sql.gz | docker compose exec -T db psql -U janasamparka janasamparka
```

## Troubleshooting

### "No constituencies found"
```bash
# Run migrations first
docker compose exec backend alembic upgrade head

# Check if constituencies exist
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.constituency import Constituency
db = SessionLocal()
print(f'Constituencies: {db.query(Constituency).count()}')
"
```

### "User already exists"
This is normal - the seed script skips existing users. If you want fresh data:
```bash
# Delete and re-seed (see "Soft Reset" section above)
```

### Frontend not showing updated data
```bash
# Hard refresh browser
# Chrome/Edge: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
# Safari: Cmd+Option+R

# Or restart frontend
docker compose restart frontend
```

## Files Reference

- `seed_database.py` - Master seeding script (recommended)
- `create_moderator.py` - Create moderators only
- `create_department_users.py` - Create dept officers & auditors
- `delete_dept_officers.py` - Utility to delete dept officers
- `SEEDING_GUIDE.md` - This file

## Phone Number Schema

```
Moderators:      +91990 0000 [0-2]         (constituency index)
Dept Officers:   +91990 [01-05] [0-2] 00   (dept, constituency, padding)
Auditors:        +91990 060 [0-2]          (constituency index)
```

Examples:
- `+919900000000` = Puttur Moderator
- `+9199001000` = PWD Officer Puttur
- `+9199002100` = Water Officer Mangalore
- `+9199006002` = Auditor Udupi

All numbers are **13 characters** (+91 followed by 10 digits) - valid Indian mobile format.
